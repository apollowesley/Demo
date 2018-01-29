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
from uline.handlers.baseHandlers import IntBkAdminHandler
from .form import GetDistributorInfo
from uline.public import common, log, auth_util, merchant_risk_util
from uline.public.constants import AUTH_STATUS
from uline.utils.record import record_utils
from uline.public.permit import check_permission


class GetChainInfoHandler(IntBkAdminHandler):
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
                payment = yield self.get_payment(cur)
                auth_info = yield self.get_auth_info(cur)
                activated_info = yield self.get_activated_info(cur)
                wx_ali_ind_info = yield self.get_wx_ali_ind_code(cur)
                rate = yield self.get_dt_rate(cur)
                risk_info = self.get_mch_risk_info() if inlet_and_balance.get('auth_status', 0) in (1, 4) else {}
                inlet_and_balance.update(wx_ali_ind_info)
                inlet_and_balance.update({
                    'payment': payment,
                    'auth_info': auth_info,
                    'activated_info': activated_info,
                    'rate': rate,
                    'risk_info': risk_info,
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
            record_utils.swap_value(
                result, s_rsp['data'], change_id=s_rsp['data']['dt_id'])

        parent_id = s_rsp['data'].get('parent_id', '')
        if parent_id:
            sql = """select dt_name from dt_inlet_info where dt_id=%s;"""
            dt_parent_name = self.db.selectSQL(sql, (parent_id,))
            if dt_parent_name:
                s_rsp['data']['parent_name'] = dt_parent_name[0]

        dt_sub_id = s_rsp['data'].get('dt_sub_id', '')
        if dt_sub_id:
            query = """select dt_sub_name from dt_subuser where dt_subuser.dt_sub_id=%s;"""
            dt_sub_name = self.db.selectSQL(query, (dt_sub_id,))
            if dt_sub_name:
                s_rsp['data']['dt_sub_name'] = dt_sub_name[0]

        self.write(s_rsp)

    @gen.coroutine
    def get_inlet_and_balance(self, cursor):
        """
        """
        query = """
        SELECT dt_inlet_info.dt_id,
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
           dt_inlet_info.license_num,
           to_char(dt_inlet_info.license_start_date, 'YYYY-MM-DD'),
           to_char(dt_inlet_info.license_end_date, 'YYYY-MM-DD'),
           dt_inlet_info.license_period,
           dt_inlet_info.license_scope,
           dt_inlet_info.license_img,
           dt_inlet_info.parent_id,
           dt_inlet_info.activated_status,
           dt_inlet_info.dt_sub_id,
           dt_inlet_info.activate_email_tag,
           dt_inlet_info.head_mobile,
           dt_inlet_info.head_name,
           dt_inlet_info.license_type,
           dt_inlet_info.head_type

            FROM dt_inlet_info
            INNER JOIN dt_user ON dt_inlet_info.dt_id = dt_user.dt_id
            INNER JOIN dt_balance ON dt_inlet_info.dt_id = dt_balance.dt_id
            INNER JOIN balance_bank_info ON
            dt_balance.bank_no = balance_bank_info.bank_no
            WHERE dt_inlet_info.dt_id = %s;"""
        cursor.execute(query, (self.dt_id,))
        ret = cursor.fetchone()
        fields = [
            'dt_id', 'dt_name', 'province', 'city', 'district', 'address',
            'contact', 'mobile', 'service_phone', 'email', 'auth_status',
            'balance_type', 'balance_name', 'bank_no',
            'balance_account', 'id_card_no', 'create_at',
            'auth_at', 'id_card_img_b', 'id_card_img_f',
            'bank_name',
            'wx_sub_mch_id', 'ali_sub_mch_id', 'ali_level',
            'license_num',
            'license_start_date', 'license_end_date',
            'license_period',
            'license_scope', 'license_img', 'parent_id', 'activated_status', 'dt_sub_id', 'activate_email_tag',
            'head_mobile', 'head_name', 'license_type', 'head_type'
        ]

        data = dict(zip(fields, ret))
        data['activate_email_tag'] = "商户" if data['activate_email_tag'] == 1 else "渠道商"

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
    def get_auth_info(self, cursor):
        query = """
        select to_char(create_at, 'YYYY-MM-DD HH24:MI:SS'),
        comment,auth_user,auth_status from auth_dt_info where dt_id=%s order by create_at"""
        cursor.execute(query, (self.dt_id,))
        ret = cursor.fetchall()
        fields = ['auth_at', 'auth_comment', 'auth_user', 'auth_status']
        data = [dict(zip(fields, i)) for i in ret] if ret else []
        for d in data:
            d['comment'] = auth_util.print_auth_status(d['auth_status'])
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

        if inlet_and_balance['dt_sub_id']:
            sub_user = self.get_dt_sub_user(
                cur, inlet_and_balance['dt_sub_id'])
            inlet_and_balance['dt_sub_name'] = sub_user

        parent_id = inlet_and_balance['parent_id']
        if parent_id:
            parent_info = self.get_parent_info(cur, parent_id)
            if parent_info:
                inlet_and_balance['parent_name'], inlet_and_balance['parent_type'] = parent_info

        raise gen.Return(inlet_and_balance)

    @gen.coroutine
    def get_dt_rate(self, cursor):
        query = '''select rate from dt_user where dt_id=%s;'''
        cursor.execute(query, (self.dt_id, ))
        ret = cursor.fetchone()
        raise gen.Return(ret[0])

    def get_dt_sub_user(self, cursor, dt_sub_id):
        query = """select dt_sub_name from dt_subuser where dt_subuser.dt_sub_id=%s;"""
        cursor.execute(query, (dt_sub_id,))
        ret = cursor.fetchone()
        if ret:
            return ret[0]
        else:
            return ""

    def get_parent_info(self, cur, parent_id):
        query = """select dt_name,dt_type from dt_inlet_info where dt_id=%s"""
        cur.execute(query, (parent_id,))
        ret = cur.fetchone()
        if ret:
            return ret
        else:
            return []

    def get_mch_risk_info(self):
        query = """select merchant_risk_item.risk_type from merchant_risk_item
                   inner join merchant_risk on merchant_risk.id=merchant_risk_item.merchant_risk_id
                   where  merchant_risk_item.has_risk>0 and merchant_risk.status=1 and merchant_risk_item.status=1
                      and sys_id=%s and sys_type_id=%s;
                """
        ret = self.db.selectSQL(query, (self.dt_id, 'chain'), fetchone=False, use_dict=True)
        risk_type_list = [merchant_risk_util.get_merchaint_risk_type_msg(risk_info['risk_type']) for risk_info in ret]
        risk_info = {
            'risk_msg': u'{}存在风险'.format('、'.join(risk_type_list)) if risk_type_list else '',
        }
        return risk_info
