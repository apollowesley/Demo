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
from uline.handlers.baseHandlers import ChainAdminHandler
from .form import GetMerchanInfo
from uline.public import common, constants
from uline.public.constants import AUTH_STATUS
from uline.utils.record import record_utils
from uline.model.uline.base import uline_session
from uline.model.uline.base import DtSubUser
from uline.public.permit import check_permission


class GetCsInfoHandler(ChainAdminHandler):
    executor = ThreadPoolExecutor(8)

    @authenticated
    @check_permission
    def prepare(self):
        form = GetMerchanInfo(self)
        form.cs_id = self.current_user
        if not form.validate():
            f_rsp = common.f_rsp(code=406, msg='fail')
            self.finish(f_rsp)
        self.mch_id = form.mch_id.data

    @asynchronous
    @gen.coroutine
    def get(self):
        # 先连表查询进件信息表和结算明细表,再单独查询支付信息表
        """
        """
        payment = yield self.get_payment()
        role = yield self.get_d0_withdraw_fee()
        auth_info = yield self.get_auth_info()
        has_authed = 2 in [each_auth_info['auth_status']
                           for each_auth_info in auth_info]
        activated_info = yield self.get_activated_info()
        inlet_and_balance = yield self.format_inlet_and_balance()
        wx_ali_ind_info = yield self.get_wx_ali_ind_code()
        mch_rate_type = yield self.get_mch_rate()
        subsidize_info = self.get_mch_subsidize_info()
        inlet_and_balance.update(wx_ali_ind_info)
        risk_account_status = self.get_mch_settle_status()
        inlet_and_balance.update({
            'payment': payment,
            'auth_info': auth_info,
            'activated_info': activated_info,
            'rate': mch_rate_type,
            'role': role,
            'has_authed': has_authed,
            'subsidize_info': subsidize_info,
        })
        inlet_and_balance.update(risk_account_status)
        s_rsp = common.scc_rsp(code=200, msg='success', **inlet_and_balance)
        # 查询修改状态表看是否有数据正在审核中，如果有就进行替换
        result = yield record_utils.select_change_record(self, s_rsp['data']['mch_id'], change_type=2)

        # 替换原来需要显示给用户的费率
        if result:
            result = json.loads(result[1])
            record_utils.swap_value(
                result, s_rsp['data'], change_id=s_rsp['data']['mch_id'], role_type=2)

        dt_sub_user = yield self.get_dt_sub_user_name(s_rsp['data']['dt_sub_id'])
        s_rsp['data']['dt_sub_user'] = dt_sub_user
        # 商户信息去空格
        for _, key in enumerate(s_rsp['data']):
            if not (key == 'create_at' or key == 'auth_at'):
                if isinstance(s_rsp['data'][key], str):
                    s_rsp['data'][key] = s_rsp['data'][key].replace(' ', '')
        self.write(s_rsp)

    @gen.coroutine
    def get_dt_sub_user_name(self, dt_sub_id):
        """如果有对应渠道商，则返回其名字， 否则返回空"""
        dt_sub_user = uline_session.query(DtSubUser).filter(
            DtSubUser.dt_sub_id == dt_sub_id).one_or_none()
        if dt_sub_user:
            return dt_sub_user.dt_sub_name
        else:
            return ''

    @gen.coroutine
    def get_inlet_and_balance(self):
        ret = self.db.selectSQL("""
        SELECT mch_inlet_info.mch_id,
           mch_inlet_info.mch_name,
           mch_inlet_info.mch_shortname,
           mch_inlet_info.province,
           mch_inlet_info.city,
           mch_inlet_info.district,
           mch_inlet_info.address,
           mch_inlet_info.contact,
           mch_inlet_info.mobile,
           mch_inlet_info.service_phone,
           mch_inlet_info.email,
           mch_inlet_info.auth_status,
           mch_inlet_info.dt_sub_id,
           mch_balance.balance_type,
           mch_balance.balance_name,
           mch_balance.bank_no,
           mch_balance.balance_account,
           mch_balance.id_card_no,
           to_char(mch_inlet_info.create_at, 'YYYY-MM-DD HH24:MI:SS'),
           to_char(mch_inlet_info.auth_at, 'YYYY-MM-DD HH24:MI:SS'),
           mch_inlet_info.id_card_img_b,
           mch_inlet_info.id_card_img_f,
           dt_user.dt_name,
           balance_bank_info.bank_name,
           mch_user.wx_sub_mch_id,
           mch_user.ali_sub_mch_id,
           mch_user.ali_level,
           mch_user.status,
           mch_user.wx_use_parent,
           mch_inlet_info.license_num,
           to_char(mch_inlet_info.license_start_date, 'YYYY-MM-DD'),
           to_char(mch_inlet_info.license_end_date, 'YYYY-MM-DD'),
           mch_inlet_info.license_period,
           mch_inlet_info.license_scope,
           mch_inlet_info.license_img,
           mch_inlet_info.pay_notify_url,
            mch_inlet_info.activate_email_tag,
            mch_inlet_info.activated_status
            FROM mch_inlet_info
            INNER JOIN mch_user on mch_inlet_info.mch_id = mch_user.mch_id
            INNER JOIN mch_balance ON mch_inlet_info.mch_id = mch_balance.mch_id
            INNER JOIN dt_user on mch_inlet_info.cs_id = dt_user.dt_id
            INNER JOIN balance_bank_info on mch_balance.bank_no = balance_bank_info.bank_no
            WHERE mch_inlet_info.cs_id = %s
              AND mch_inlet_info.mch_id = %s;
        """, (self.current_user, self.mch_id))
        fields = [
            'mch_id', 'mch_name', 'mch_shortname', 'province', 'city', 'district',
            'address', 'contact',
            'mobile', 'service_phone', 'email', 'auth_status', 'dt_sub_id',
            'balance_type', 'balance_name', 'bank_no',
            'balance_account', 'id_card_no',
            'create_at', 'auth_at', 'id_card_img_b', 'id_card_img_f',
            'dt_name', 'bank_name', 'wx_sub_mch_id', 'ali_sub_mch_id', 'ali_level', 'status',
            'mch_wx_use_parent',
            'license_num',
            'license_start_date', 'license_end_date',
            'license_period',
            'license_scope', 'license_img',
            'pay_notify_url', 'activate_email_tag', 'activated_status'
        ]
        data = dict(zip(fields, ret))
        data['activate_email_tag'] = "门店" if data['activate_email_tag'] == 1 else "渠道商"
        raise gen.Return(data)

    @gen.coroutine
    def get_old_ind_code(self):
        query = """select wx_ind_code, old_ind_code from mch_inlet_info where mch_id=%s;"""
        ret = self.db.selectSQL(query, (self.mch_id,))
        raise gen.Return(ret)

    @gen.coroutine
    def get_wx_ali_ind_code(self):
        ret = [''] * 4
        ret_ind_code = yield self.get_old_ind_code()
        if ret_ind_code[0]:
            query = """
                select
                mch_inlet_info.u_ind_code,
                industry_uline_info.industry_name,
                industry_ali_info.industry_name,
                industry_wx_info.industry_name
                from mch_inlet_info
                inner join industry_uline_info on industry_uline_info.industry_code = mch_inlet_info.u_ind_code
                inner join industry_ali_info on industry_ali_info.industry_code = mch_inlet_info.ali_ind_code
                inner join industry_wx_info on industry_wx_info.industry_code = mch_inlet_info.wx_ind_code
                where mch_inlet_info.mch_id=%s;"""
            ret = self.db.selectSQL(query, (self.mch_id,))
        else:
            query = """
                select
                mch_inlet_info.u_ind_code,
                industry_uline_info.industry_name,
                industry_ali_info.industry_name
                from mch_inlet_info
                inner join industry_uline_info on industry_uline_info.industry_code = mch_inlet_info.u_ind_code
                inner join industry_ali_info on industry_ali_info.industry_code = mch_inlet_info.ali_ind_code
                where mch_inlet_info.mch_id=%s;"""
            u_ind_code_ret = self.db.selectSQL(query, (self.mch_id,))

            query = """select industry_name from industry_uline_info where wx_ind_code=%s and status=2;"""
            wx_ind_code_ret = self.db.selectSQL(query, (ret_ind_code[1],))
            if not u_ind_code_ret:
                # 不存在uline的经营类目，则展示微信的经营类目
                query = """select industry_code from industry_uline_info where wx_ind_code=%s and status=1"""
                u_ind_code_ret = self.db.selectSQL(query, (ret_ind_code[1],))
                if u_ind_code_ret:
                    ret[0] = u_ind_code_ret[0]
                ret[1], ret[3] = wx_ind_code_ret[0], wx_ind_code_ret[0]
            else:
                ret = list(u_ind_code_ret)
                ret.append(wx_ind_code_ret[0])

        fields = ['u_ind_code', 'u_ind_name', 'ali_ind_name', 'wx_ind_name']
        data = dict(zip(fields, ret))
        raise gen.Return(data)

    @gen.coroutine
    def get_d0_withdraw_fee(self):
        ret = self.db.selectSQL(
            """
            SELECT wx,alipay FROM d0_withdraw_fee WHERE role=%s and role_type=%s;""", (self.mch_id, 'mch'))
        data = {}
        if ret:
            if ret[0] or ret[1]:
                # 数据库只能存int
                wx = ret[0] / 100 if ret[0] else ret[0]
                alipay = ret[1] / 100 if ret[1] else ret[1]
                data = {
                    'wx': wx,
                    'alipay': alipay
                }
        raise gen.Return(data)

    @gen.coroutine
    def get_payment(self):
        """
        SELECT payment_type,payment_rate,activated_status FROM mch_payment WHERE mch_id=100000000846;
        """
        ret = self.db.selectSQL(
            """SELECT payment_type,payment_rate,activated_status FROM mch_payment WHERE mch_id=%s;""", (
                self.mch_id,),
            fetchone=False)
        fields = ['pay_type', 'pay_rate', 'activated_status']
        data = [dict(zip(fields, [i[0], i[1] / 10, i[2]]))
                for i in ret] if ret else []
        raise gen.Return(data)

    @gen.coroutine
    def get_auth_info(self):
        query = """select to_char(create_at, 'YYYY-MM-DD HH24:MI:SS'),comment,auth_status from auth_mch_info
                            where mch_id=%s order by create_at"""
        ret = self.db.selectSQL(query, (self.mch_id,), fetchone=False)
        fields = ['auth_at', 'auth_comment', 'auth_status']
        data = [dict(zip(fields, [i[0], i[1], i[2]]))
                for i in ret] if ret else []
        auth_info_list = list()
        for auth_info in data:
            auth_status = auth_info['auth_status']
            if auth_status in [constants.AUTH_STATUS_INLETING, constants.AUTH_STATUS_INTERNET_FAIL,
                               constants.AUTH_STATUS_PREVIEWD]:
                continue
            auth_info['comment'] = AUTH_STATUS[str(auth_status)]
            if auth_status in [constants.AUTH_STATUS_SUBMIT, constants.AUTH_STATUS_PREVIEWD]:
                auth_info['comment'] = '审核中'
            elif auth_status in [constants.AUTH_STATUS_FIRST_DENY, constants.AUTH_STATUS_DENY]:
                auth_info['auth_status'] = constants.AUTH_STATUS_DENY
                auth_info['comment'] = '审核驳回'
            auth_info_list.append(auth_info)

        raise gen.Return(auth_info_list)

    @gen.coroutine
    def get_activated_info(self):
        query = """
            select
            to_char(create_at, 'YYYY-MM-DD HH24:MI:SS'),
            comment, payment_type from activated_mch_info
            where mch_id=%s order by create_at;"""
        ret = self.db.selectSQL(query, (self.mch_id, ), fetchone=False)
        fields = ['activated_at', 'comment', 'payment_type']
        data = [dict(zip(fields, i)) for i in ret] if ret else []
        raise gen.Return(data)

    @gen.coroutine
    def format_inlet_and_balance(self):
        inlet_and_balance = yield self.get_inlet_and_balance()
        base_dir = '/static/uploads/mch/idcard'
        file_dir = os.path.join(base_dir, '{}'.format(self.mch_id))
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
    def get_mch_rate(self):
        query = '''select rate from mch_user where mch_id=%s;'''
        ret = self.db.selectSQL(query, (self.mch_id,), fetchone=True)
        raise gen.Return(ret[0])

    def get_mch_subsidize_info(self):
        query = """select rate from discount where role_id=%s and role=%s and valid=1 order by create_at desc limit 1"""
        ret = self.db.selectSQL(query, (self.current_user, 'chain'), fetchone=True, use_dict=True)
        subsidize_info = {}
        if ret and ret['rate']:
            rate_info = json.loads(ret['rate'])
            rate_info['weixin'] = rate_info['weixin'] / 100.0
            rate_info['alipay'] = rate_info['alipay'] / 100.0
            subsidize_info.update(rate_info)
        return subsidize_info

    def get_mch_settle_status(self):
        query = """select credit,settle from risk_control WHERE sys_id=%s and sys_type_id=%s"""
        result = self.db.selectSQL(query, (self.mch_id, 'cs'), fetchone=True, use_dict=True)
        settle_status = {
            'weixin': 0,
            'alipay': 0,
        }
        credit_status = {
            'weixin': 0,
            'alipay': 0,
        }
        if result:
            channels = json.loads(result['settle']) if result['settle'] else {}
            if channels:
                frozen_channel = channels.get('channel', [])
                if frozen_channel:
                    settle_status.update({channel: 1 for channel in frozen_channel})

            channels = json.loads(result['credit']) if result['credit'] else {}
            if channels:
                frozen_channel = channels.get('channel', [])
                if frozen_channel:
                    credit_status.update({channel: 1 for channel in frozen_channel})

        return {'settle_status': settle_status, 'credit_status': credit_status}

