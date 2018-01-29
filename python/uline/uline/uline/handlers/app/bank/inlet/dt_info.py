#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/14/16'

# ajax获取某个商户的具体请求
from __future__ import division
import os
import json
from tornado.web import authenticated, asynchronous
from tornado import gen
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
from uline.handlers.baseHandlers import BkAdminHandler
from .form import GetDistributorInfo
from uline.public import common, log
from uline.public.constants import AUTH_STATUS, rate_sort, old_payment_relations
from uline.utils.record import record_utils
from uline.public.permit import check_permission
from uline.settings import FEATURE_SWITCH


class GetDistributorInfoHandler(BkAdminHandler):
    executor = ThreadPoolExecutor(8)

    @authenticated
    @check_permission
    def prepare(self):
        form = GetDistributorInfo(self)
        if not form.validate():
            f_rsp = common.f_rsp(code=406, msg='fail')
            self.finish(f_rsp)
        self.dt_id = form.dt_id.data

    @run_on_executor
    @asynchronous
    @gen.coroutine
    def get(self):
        # 先连表查询进件信息表和结算明细表,再单独查询支付信息表
        """
        """
        inlet_and_balance = dict()
        with self.db.get_db() as cur:
            try:
                inlet_and_balance = yield self.format_inlet_and_balance(cur)
                # payment = yield self.get_payment(cur)
                self.NEW_INLET = FEATURE_SWITCH.get('NEW_INLET')
                self.role = {}
                payment = yield self.get_new_payment(cur)
                if not self.NEW_INLET:
                    self.role = yield self.get_d0_withdraw_fee(cur)
                auth_info = yield self.get_auth_info(cur)
                activated_info = yield self.get_activated_info(cur)
                wx_ali_ind_info = yield self.get_wx_ali_ind_code(cur)
                rate = yield self.get_dt_rate(cur)
                inlet_and_balance.update(wx_ali_ind_info)
                inlet_and_balance.update({
                    'role': self.role,
                    'payment': payment,
                    'auth_info': auth_info,
                    'activated_info': activated_info,
                    'rate': rate
                })
            except Exception as err:
                cur.connection.rollback()
                log.exception.info(err)
                self.write(common.f_rsp(code=406, msg='fail'))

        s_rsp = common.scc_rsp(code=200, msg='success', **inlet_and_balance)

        # 查询修改状态表看是否有数据正在审核中，如果有就进行替换
        result = yield record_utils.select_change_record(self, s_rsp['data']['dt_id'])

        # 替换原来需要显示给用户的费率
        if result:
            result = json.loads(result[1])
            record_utils.swap_value(result, s_rsp['data'], change_id=s_rsp['data']['dt_id'])

        self.write(s_rsp)

    @gen.coroutine
    def get_inlet_and_balance(self, cursor):
        """
        """
        query = """
        SELECT dt_inlet_info.dt_id,
           dt_inlet_info.activated_status,
           dt_inlet_info.dt_name,
           dt_inlet_info.province,
           dt_inlet_info.city,
           dt_inlet_info.district,
           dt_inlet_info.address,
           dt_inlet_info.contact,
           dt_inlet_info.mobile,
           dt_inlet_info.service_phone,
           dt_inlet_info.email,
           dt_inlet_info.auth_status,
           dt_inlet_info.unionpay_id,
           dt_balance.balance_type,
           dt_balance.balance_name,
           dt_balance.bank_no,
           dt_balance.balance_account,
           dt_balance.id_card_no,
           to_char(dt_inlet_info.create_at, 'YYYY-MM-DD HH24:MI:SS'),
           to_char(dt_inlet_info.auth_at, 'YYYY-MM-DD HH24:MI:SS'),
           dt_inlet_info.id_card_img_b,
           dt_inlet_info.id_card_img_f,
           balance_bank_info.bank_name,
           dt_user.wx_sub_mch_id,
           dt_inlet_info.license_num,
           to_char(dt_inlet_info.license_start_date, 'YYYY-MM-DD'),
           to_char(dt_inlet_info.license_end_date, 'YYYY-MM-DD'),
           dt_inlet_info.license_period,
           dt_inlet_info.license_scope,
           dt_inlet_info.license_img,
           bk_user.bk_type,
           bk_user.bk_name,
           dt_inlet_info.alipay_pid
            FROM dt_inlet_info
            INNER JOIN dt_user ON dt_inlet_info.dt_id = dt_user.dt_id
            INNER JOIN dt_balance ON dt_inlet_info.dt_id = dt_balance.dt_id
            INNER JOIN balance_bank_info ON
            dt_balance.bank_no = balance_bank_info.bank_no
            INNER JOIN bk_user on bk_user.bk_id=dt_inlet_info.bk_id
            WHERE dt_inlet_info.dt_id = %s;"""
        cursor.execute(query, (self.dt_id,))
        ret = cursor.fetchone()
        fields = [
            'dt_id', 'activated_status', 'dt_name', 'province', 'city', 'district', 'address',
            'contact', 'mobile', 'service_phone', 'email', 'auth_status', 'unionpay_id',
            'balance_type', 'balance_name', 'bank_no',
            'balance_account', 'id_card_no', 'create_at',
            'auth_at', 'id_card_img_b', 'id_card_img_f',
            'bank_name',
            'wx_sub_mch_id',
            'license_num',
            'license_start_date', 'license_end_date',
            'license_period',
            'license_scope', 'license_img', 'bk_id', 'bk_name', 'alipay_pid'
        ]

        data = dict(zip(fields, ret))
        data['bk_type'] = data['bk_id']
        raise gen.Return(data)

    @gen.coroutine
    def get_old_ind_code(self, cursor):
        query = """select wx_ind_code, old_ind_code from dt_inlet_info where dt_id=%s;"""
        cursor.execute(query, (self.dt_id,))
        ret = cursor.fetchone()
        raise gen.Return(ret)

    @gen.coroutine
    def get_d0_withdraw_fee(self, cursor):
        cursor.execute(
            """
            SELECT wx,alipay FROM d0_withdraw_fee WHERE role=%s and role_type=%s;""", (self.dt_id, 'dt'))
        ret = cursor.fetchone()
        data = {}
        if ret:
            if ret[0] or ret[1]:
                # 数据库只能存int
                wx = ret[0] / 100 if ret[0] else ret[0]
                alipay = ret[1] / 100 if ret[1] else ret[1]
                data = {
                    'wx_draw_fee': wx,
                    'ali_draw_fee': alipay
                }
        raise gen.Return(data)

    @gen.coroutine
    def get_wx_ali_ind_code(self, cursor):
        ret = [''] * 4
        ret_ind_code = yield self.get_old_ind_code(cursor)
        if ret_ind_code[0]:
            query = """select
                    dt_inlet_info.u_ind_code,
                    industry_uline_info.industry_name,
                    industry_ali_info.industry_name,
                    industry_wx_info.industry_name
                    from dt_inlet_info
                    inner join industry_uline_info on industry_uline_info.industry_code = dt_inlet_info.u_ind_code
                    inner join industry_ali_info on industry_ali_info.industry_code = dt_inlet_info.ali_ind_code
                    inner join industry_wx_info on industry_wx_info.industry_code = dt_inlet_info.wx_ind_code
                    where dt_inlet_info.dt_id=%s;"""
            cursor.execute(query, (self.dt_id,))
            ret = cursor.fetchone()
        else:
            # inner_join
            query = """select
                    dt_inlet_info.u_ind_code,
                    industry_uline_info.industry_name,
                    industry_ali_info.industry_name
                    from dt_inlet_info
                    inner join industry_uline_info on industry_uline_info.industry_code = dt_inlet_info.u_ind_code
                    inner join industry_ali_info on industry_ali_info.industry_code = dt_inlet_info.ali_ind_code
                    where dt_inlet_info.dt_id=%s;"""
            cursor.execute(query, (self.dt_id,))
            u_ind_code_ret = cursor.fetchone()

            # 微信经营信息
            query = """select industry_name from industry_uline_info where wx_ind_code=%s and status=2;"""
            cursor.execute(query, (ret_ind_code[1],))
            wx_ind_code_ret = cursor.fetchone()
            if not u_ind_code_ret:
                # 不存在uline的经营类目，则通过微信行业code反查uline行业code，并使用微信经营信息
                query = """select industry_code from industry_uline_info where wx_ind_code=%s and status=1"""
                cursor.execute(query, (ret_ind_code[1],))
                u_ind_code_ret = cursor.fetchone()
                if u_ind_code_ret:
                    ret[0] = u_ind_code_ret[0]
                ret[1], ret[3] = wx_ind_code_ret[0], wx_ind_code_ret[0]
            else:
                ret = list(u_ind_code_ret)
                ret.append(wx_ind_code_ret[0])

        fields = ['u_ind_code', 'u_ind_name', 'ali_ind_name', 'wx_ind_name']
        data = dict(zip(fields, ret))
        if ret_ind_code[0]:
            data['wx_ind_code'] = ret_ind_code[0]
        else:
            data['wx_ind_code'] = ret_ind_code[1]
        raise gen.Return(data)

    @gen.coroutine
    def get_new_payment(self, cursor):
        cursor.execute("""SELECT uline_payment_code,settle_rate, settle_rate, activated_status, uline_settle_id,
                              payment_type, withdraw_fee, withdraw_rate FROM dt_payment
                              WHERE dt_id=%s;""", (self.dt_id,))
        ret = cursor.fetchall()
        fields = ['uline_payment_code', 'settle_rate', 'pay_rate', 'activated_status', 'uline_settle_id', 'pay_type',
                  'withdraw_fee', 'withdraw_rate', 'operate']
        data = [dict(zip(fields, [i[0], i[1] / 10, i[2] / 10, i[3], i[4], i[5], i[6], i[7], 1]))
                for i in ret] if ret else []
        for row in data:
            # if row.get('uline_settle_id') == 2:
            #     row['uline_payment_code'] += '_D0'
            row['sort'] = rate_sort.get(row.get('uline_payment_code'))
            # 新的进件，手续费和垫资费存在dt_paymnet
            if self.NEW_INLET and row.get('withdraw_fee') and row.get('withdraw_rate'):
                if row.get('uline_payment_code').startswith('WX'):
                    self.role['wx_draw_fee'] = row.get('withdraw_fee') / 100
                    self.role['wx_draw_rate'] = row.get('withdraw_rate') / 10
                if row.get('uline_payment_code').startswith('ALI'):
                    self.role['ali_draw_fee'] = row.get('withdraw_fee') / 100
                    self.role['ali_draw_rate'] = row.get('withdraw_rate') / 10
        # data.sort(key=lambda x: (x.get('uline_settle_id'), x.get('uline_payment_code')), reverse=True)
        data.sort(key=lambda x: x.get('sort'))
        raise gen.Return(data)

    @gen.coroutine
    def get_payment(self, cursor):
        """
        SELECT payment_type,payment_rate,activated_status FROM dt_payment WHERE dt_id=100000000846;
        """
        cursor.execute(
            """SELECT payment_type,payment_rate,activated_status FROM dt_payment WHERE dt_id=%s;""", (self.dt_id,))
        ret = cursor.fetchall()
        fields = ['pay_type', 'pay_rate', 'activated_status', 'operate']
        data = [dict(zip(fields, [i[0], i[1] / 10, i[2], 1])) for i in ret] if ret else []
        raise gen.Return(data)

    @gen.coroutine
    def get_auth_info(self, cursor):
        query = """
        select to_char(create_at, 'YYYY-MM-DD HH24:MI:SS'),
        comment,auth_user,auth_status from auth_dt_info where dt_id=%s order by create_at"""
        cursor.execute(query, (self.dt_id,))
        ret = cursor.fetchall()
        fields = ['auth_at', 'auth_comment', 'auth_user', 'auth_status']
        data = [dict(zip(fields, i)) for i in ret] if ret else []
        for d in data:
            d['comment'] = AUTH_STATUS[str(d['auth_status'])]
        raise gen.Return(data)

    @gen.coroutine
    def get_activated_info(self, cursor):
        query = """
        select to_char(create_at, 'YYYY-MM-DD HH24:MI:SS'),
        comment, payment_type,
        activated_user from activated_dt_info where dt_id=%s order by create_at;"""
        cursor.execute(query, (self.dt_id, ))
        ret = cursor.fetchall()
        fields = ['activated_at', 'comment', 'payment_type', 'activated_user']
        data = [dict(zip(fields, i)) for i in ret] if ret else []
        for row in data:
            row['uline_payment_code'] = old_payment_relations.get(str(row.get('payment_type')))
            row['sort'] = rate_sort.get(row.get('uline_payment_code'))
        data = sorted(data, key=lambda k: (k.get('activated_at'), k.get('sort')), reverse=True)
        raise gen.Return(data)

    @gen.coroutine
    def format_inlet_and_balance(self, cur):
        inlet_and_balance = yield self.get_inlet_and_balance(cur)
        base_dir = '/static/uploads/dt/idcard'
        file_dir = os.path.join(base_dir, '{}'.format(self.dt_id))
        img_b_path = os.path.join(file_dir, inlet_and_balance.get('id_card_img_b'))
        img_f_path = os.path.join(file_dir, inlet_and_balance.get('id_card_img_f'))
        if inlet_and_balance.get('license_img', None):
            license_img_path = os.path.join(file_dir, inlet_and_balance.get('license_img'))
        else:
            license_img_path = None
        inlet_and_balance['id_card_img_b'] = img_b_path
        inlet_and_balance['id_card_img_f'] = img_f_path
        if license_img_path:
            inlet_and_balance['license_img'] = license_img_path
        else:
            inlet_and_balance['license_img'] = None
        raise gen.Return(inlet_and_balance)

    @gen.coroutine
    def get_dt_rate(self, cursor):
        query = '''select rate from dt_user where dt_id=%s;'''
        cursor.execute(query, (self.dt_id, ))
        ret = cursor.fetchone()
        raise gen.Return(ret[0])
