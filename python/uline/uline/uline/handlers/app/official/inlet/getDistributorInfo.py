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
from uline.handlers.baseHandlers import OfclAdminHandler
from .form import GetDistributorInfo
from uline.public.constants import AUTH_STATUS, rate_sort, old_payment_relations
from uline.public import common, log, auth_util, merchant_risk_util
from uline.utils.record import record_utils
from uline.public.permit import check_permission
from uline.settings import FEATURE_SWITCH


class GetDistributorInfoHandler(OfclAdminHandler):
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
                has_authed = 2 in [each_auth_info['auth_status']
                                   for each_auth_info in auth_info]
                activated_info = yield self.get_activated_info(cur)
                wx_ali_ind_info = yield self.get_wx_ali_ind_code(cur)
                rate = yield self.get_dt_rate(cur)
                subsidize_info = self.get_mch_subsidize_info(cur)
                risk_info = self.get_mch_risk_info() if inlet_and_balance.get('auth_status', 0) in (1, 4) else {}
                inlet_and_balance.update(wx_ali_ind_info)
                inlet_and_balance.update({
                    'payment': payment,
                    'auth_info': auth_info,
                    'activated_info': activated_info,
                    'rate': rate,
                    'role': self.role,
                    'has_authed': has_authed,
                    'subsidize_info': subsidize_info,
                    'risk_info': risk_info,
                })
            except Exception as err:
                cur.connection.rollback()
                log.exception.info(err)
                self.write(common.f_rsp(code=406, msg='fail'))
                return
            else:
                cur.connection.commit()

        s_rsp = common.scc_rsp(code=200, msg='success', **inlet_and_balance)

        # 查询修改状态表看是否有数据正在审核中，如果有就进行替换
        if s_rsp.get('data'):
            result = yield record_utils.select_change_record(self, s_rsp['data']['dt_id'])
            # 替换原来需要显示给用户的费率
            if result:
                result = json.loads(result[1])
                record_utils.swap_value(
                    result, s_rsp['data'], change_id=s_rsp['data']['dt_id'])

            # 去掉渠道商里的字符串里面的空格
            for _, key in enumerate(s_rsp['data']):
                if not (key == 'create_at' or key == 'auth_at'):
                    if isinstance(s_rsp['data'][key], str):
                        s_rsp['data'][key] = s_rsp['data'][key].replace(' ', '')
        self.write(s_rsp)

    @gen.coroutine
    def get_inlet_and_balance(self, cursor):
        """
        """
        query = """
        SELECT dt_inlet_info.dt_id,
           dt_inlet_info.activated_status,
           dt_inlet_info.wx_app_channel_id,
           dt_inlet_info.wx_channel_id,
           dt_inlet_info.unionpay_id,
           dt_inlet_info.dt_name,
           dt_inlet_info.dt_type,
           dt_inlet_info.province,
           dt_inlet_info.city,
           dt_inlet_info.district,
           dt_inlet_info.address,
           dt_inlet_info.contact,
           dt_inlet_info.mobile,
           dt_inlet_info.service_phone,
           dt_inlet_info.email,
           dt_inlet_info.auth_status,
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
           dt_user.ali_sub_mch_id,
           dt_user.ali_level,
           dt_user.status,
           dt_inlet_info.license_num,
           to_char(dt_inlet_info.license_start_date, 'YYYY-MM-DD'),
           to_char(dt_inlet_info.license_end_date, 'YYYY-MM-DD'),
           dt_inlet_info.license_period,
           dt_inlet_info.license_scope,
           dt_inlet_info.license_img,
          dt_inlet_info.activate_email_tag,
           bu.bk_name,
           bu.bk_type,
           dt_inlet_info.alipay_pid,
           dt_inlet_info.head_mobile,
           dt_inlet_info.head_name,
           dt_inlet_info.license_type,
           dt_inlet_info.head_type
            FROM dt_inlet_info
            INNER JOIN dt_user ON dt_inlet_info.dt_id = dt_user.dt_id
            INNER JOIN dt_balance ON dt_inlet_info.dt_id = dt_balance.dt_id
            INNER JOIN balance_bank_info ON dt_balance.bank_no = balance_bank_info.bank_no
            INNER JOIN bk_user as bu on bu.bk_id = dt_inlet_info.bk_id
            WHERE dt_inlet_info.dt_id = %s;"""
        cursor.execute(query, (self.dt_id,))
        ret = cursor.fetchone()
        fields = [
            'dt_id', 'activated_status', 'wx_app_channel_id', 'wx_channel_id', 'unionpay_id', 'dt_name', 'dt_type',
            'province', 'city', 'district', 'address',
            'contact', 'mobile', 'service_phone', 'email', 'auth_status',
            'balance_type', 'balance_name', 'bank_no',
            'balance_account', 'id_card_no', 'create_at',
            'auth_at', 'id_card_img_b', 'id_card_img_f',
            'bank_name',
            'wx_sub_mch_id', 'ali_sub_mch_id', 'ali_level',
            'status',
            'license_num',
            'license_start_date', 'license_end_date',
            'license_period',
            'license_scope', 'license_img', 'activate_email_tag',
            'bk_name', 'bk_type', 'alipay_pid',
            'head_mobile', 'head_name', 'license_type', 'head_type',
        ]

        data = dict(zip(fields, ret))
        data['activate_email_tag'] = "商户" if data['activate_email_tag'] == 1 else "渠道商"

        if not data['wx_channel_id']:
            data['wx_channel_id'] = ' '
        if not data['wx_app_channel_id']:
            data['wx_app_channel_id'] = ' '
        if not data['unionpay_id']:
            data['unionpay_id'] = ' '
        raise gen.Return(data)

    @gen.coroutine
    def get_old_ind_code(self, cursor):
        query = """select wx_ind_code, old_ind_code from dt_inlet_info where dt_id=%s;"""
        cursor.execute(query, (self.dt_id,))
        ret = cursor.fetchone()
        raise gen.Return(ret)

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

            query = """select industry_name from industry_uline_info where wx_ind_code=%s and status=2;"""
            cursor.execute(query, (ret_ind_code[1],))
            wx_ind_code_ret = cursor.fetchone()
            if not u_ind_code_ret:
                # 不存在uline的经营类目，则展示微信的经营类目
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
    def get_payment(self, cursor):
        """
        SELECT payment_type,payment_rate,activated_status FROM dt_payment WHERE dt_id=100000000846;
        """
        cursor.execute(
            """SELECT payment_type,payment_rate,activated_status FROM dt_payment WHERE dt_id=%s;""", (self.dt_id,))
        ret = cursor.fetchall()
        fields = ['pay_type', 'pay_rate', 'activated_status']
        data = [dict(zip(fields, [i[0], i[1] / 10, i[2]]))
                for i in ret] if ret else []
        raise gen.Return(data)

    @gen.coroutine
    def get_new_payment(self, cursor):
        cursor.execute("""SELECT uline_payment_code,settle_rate, settle_rate, activated_status, uline_settle_id,
                              payment_type, withdraw_fee, withdraw_rate FROM dt_payment
                              WHERE dt_id=%s;""", (self.dt_id,))
        ret = cursor.fetchall()
        fields = ['uline_payment_code', 'settle_rate', 'pay_rate', 'activated_status', 'uline_settle_id', 'pay_type',
                  'withdraw_fee', 'withdraw_rate']
        data = [dict(zip(fields, [i[0], i[1] / 10, i[2] / 10, i[3], i[4], i[5], i[6], i[7]]))
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
    def get_auth_info(self, cursor):
        query = """
        select to_char(create_at, 'YYYY-MM-DD HH24:MI:SS'),
        comment,auth_user,auth_status from auth_dt_info where dt_id=%s order by create_at;"""
        cursor.execute(query, (self.dt_id,))
        ret = cursor.fetchall()
        fields = ['auth_at', 'auth_comment', 'auth_user', 'auth_status']
        data = [dict(zip(fields, [i[0], i[1], i[2], i[3]]))
                for i in ret] if ret else []
        for d in data:
            d['comment'] = auth_util.print_auth_status(d['auth_status'])
        raise gen.Return(data)

    @gen.coroutine
    def get_activated_info(self, cursor):
        query = """
        select to_char(create_at, 'YYYY-MM-DD HH24:MI:SS'),
        comment, payment_type from activated_dt_info where dt_id=%s order by create_at;"""
        cursor.execute(query, (self.dt_id,))
        ret = cursor.fetchall()
        fields = ['activated_at', 'comment', 'payment_type']
        data = [dict(zip(fields, i)) for i in ret] if ret else []
        for row in data:
            row['uline_payment_code'] = old_payment_relations.get(str(row.get('payment_type')))
            row['sort'] = rate_sort.get(row.get('uline_payment_code'))
        data.sort(key=lambda x: (x.get('activated_at'), x.get('sort')))
        raise gen.Return(data)

    @gen.coroutine
    def format_inlet_and_balance(self, cur):
        inlet_and_balance = yield self.get_inlet_and_balance(cur)
        base_dir = '/static/uploads/dt/idcard'
        file_dir = os.path.join(base_dir, '{}'.format(self.dt_id))
        img_b_path = os.path.join(
            file_dir, inlet_and_balance.get('id_card_img_b'))
        img_f_path = os.path.join(
            file_dir, inlet_and_balance.get('id_card_img_f'))
        if inlet_and_balance.get('license_img', None):
            license_img_path = os.path.join(
                file_dir, inlet_and_balance.get('license_img'))
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
        cursor.execute(query, (self.dt_id,))
        ret = cursor.fetchone()
        raise gen.Return(ret[0])

    def get_mch_subsidize_info(self, cur):
        query = """select rate from discount where role_id=%s and role in %s and valid=1 order by create_at desc limit 1"""
        cur.execute(query, (self.dt_id, ('chain', 'dt')))
        ret = cur.fetchone()
        subsidize_info = {}
        if ret and ret[0]:
            rate_info = json.loads(ret[0])
            rate_info['weixin'] = rate_info['weixin'] / 100.0
            rate_info['alipay'] = rate_info['alipay'] / 100.0
            subsidize_info.update(rate_info)
        return subsidize_info

    def get_mch_risk_info(self):
        query = """select merchant_risk_item.risk_type from merchant_risk_item
                   inner join merchant_risk on merchant_risk.id=merchant_risk_item.merchant_risk_id
                   where  merchant_risk_item.has_risk>0 and merchant_risk.status=1 and merchant_risk_item.status=1
                      and sys_id=%s and sys_type_id in %s;
                """
        ret = self.db.selectSQL(query, (self.dt_id, ('chain', 'dt')), fetchone=False, use_dict=True)
        risk_type_list = [merchant_risk_util.get_merchaint_risk_type_msg(risk_info['risk_type']) for risk_info in ret]
        risk_info = {
            'risk_msg': u'{}存在风险'.format('、'.join(risk_type_list)) if risk_type_list else '',
        }
        return risk_info