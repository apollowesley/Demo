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
from uline.handlers.baseHandlers import IntBkAdminHandler
from .form import GetMerchantInfo
from uline.public.constants import AUTH_STATUS, DINNER_TOGGETHER_PAY_TYPES, rate_sort, old_payment_relations
from uline.public import common, log, constants, merchant_risk_util
from uline.utils.record import record_utils
from uline.settings import FEATURE_SWITCH
from uline.public.permit import check_permission


class GetMerchantInfoHandler(IntBkAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        form = GetMerchantInfo(self)
        if not form.validate():
            f_rsp = common.f_rsp(code=406, msg='fail')
            self.finish(f_rsp)
        self.mch_id = form.mch_id.data
        self.open_review = FEATURE_SWITCH.get('REVIEW', False)

    @asynchronous
    @gen.coroutine
    def get(self):
        # 先连表查询进件信息表和结算明细表,再单独查询支付信息表
        """
        """

        # payment = yield self.get_payment()
        self.NEW_INLET = FEATURE_SWITCH.get('NEW_INLET')
        self.role = {}
        payment = yield self.get_new_payment()
        if not self.NEW_INLET:
            self.role = yield self.get_d0_withdraw_fee()
        auth_info = yield self.get_auth_info()
        activated_info = yield self.get_activated_info()
        inlet_and_balance = yield self.format_inlet_and_balance()
        wx_ali_ind_info = yield self.get_wx_ali_ind_code()
        mch_rate_type = yield self.get_mch_rate()
        risk_status = self.get_mch_settle_status()
        risk_info = self.get_mch_risk_info() if inlet_and_balance.get('auth_status', 0) in (1, 4) else {}
        inlet_and_balance.update(wx_ali_ind_info)
        inlet_and_balance.update({
            'role': self.role,
            'payment': payment,
            'auth_info': auth_info,
            'activated_info': activated_info,
            'rate': mch_rate_type,
            'risk_info': risk_info,
        })
        inlet_and_balance.update(risk_status)
        s_rsp = common.scc_rsp(code=200, msg='success', **inlet_and_balance)
        # 查询修改状态表看是否有数据正在审核中，如果有就进行替换
        changes = yield record_utils.select_change_record(self, s_rsp['data']['mch_id'], change_type=2)

        # 替换原来需要显示给用户的费率
        if changes:
            changes = json.loads(changes[1])
            record_utils.swap_value(changes, s_rsp['data'], change_id=s_rsp['data']['mch_id'], role_type=2)

        cs_id = s_rsp['data'].get("cs_id", None)
        if cs_id:
            sql = """select dt_short_name, dt_name from dt_inlet_info where dt_id=%s"""
            parent_info = self.db.selectSQL(sql, (cs_id,), use_dict=True)
            if parent_info:
                s_rsp['data']['parent_name'] = parent_info['dt_name']
                s_rsp['data']['parent_short_name'] = parent_info['dt_short_name']

        self.use_dine = 0
        for payment in s_rsp['data']['payment']:
            if int(payment['pay_type']) in DINNER_TOGGETHER_PAY_TYPES:
                self.use_dine = 1
        s_rsp['data']['use_dine'] = self.use_dine
        if not self.use_dine:
            for each_key in ['mch_front_img', 'mch_desk_img', 'mch_inner_img']:
                if each_key in s_rsp['data']:
                    del s_rsp['data'][each_key]

        self.write(s_rsp)

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
           mch_inlet_info.head_mobile,
           mch_inlet_info.head_name,
           mch_inlet_info.mobile,
           mch_inlet_info.service_phone,
           mch_inlet_info.email,
           mch_inlet_info.auth_status,
           mch_balance.balance_type,
           mch_balance.balance_name,
           mch_balance.bank_no,
           mch_balance.balance_account,
           mch_balance.id_card_no,
           mch_balance.status as balance_status,
           to_char(mch_inlet_info.create_at, 'YYYY-MM-DD HH24:MI:SS'),
           to_char(mch_inlet_info.auth_at, 'YYYY-MM-DD HH24:MI:SS'),
           mch_inlet_info.id_card_img_b,
           mch_inlet_info.id_card_img_f,
           dt_user.dt_name,
           balance_bank_info.bank_name,
           mch_user.wx_sub_mch_id,
           mch_user.wx_app_sub_mch_id,
           mch_user.jd_sub_mch_id,
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
           mch_inlet_info.img_with_id_card,
           mch_inlet_info.pay_notify_url,
           dt_subuser.dt_sub_name,
           dt_inlet_info.dt_type,
           mch_inlet_info.cs_id,
           mch_inlet_info.annex_img1,
           mch_inlet_info.annex_img2,
           mch_inlet_info.annex_img3,
           mch_inlet_info.annex_img4,
           mch_inlet_info.annex_img5,
           mch_inlet_info.activate_email_tag,
           mch_inlet_info.license_type,
           mch_inlet_info.head_type

            FROM mch_inlet_info
            INNER JOIN mch_user on mch_inlet_info.mch_id = mch_user.mch_id
            INNER JOIN mch_balance ON mch_inlet_info.mch_id = mch_balance.mch_id
            INNER JOIN dt_user on mch_inlet_info.dt_id = dt_user.dt_id
            INNER JOIN balance_bank_info on mch_balance.bank_no = balance_bank_info.bank_no
            LEFT JOIN dt_subuser on mch_inlet_info.dt_sub_id = dt_subuser.dt_sub_id
            LEFT JOIN dt_inlet_info on mch_inlet_info.dt_id = dt_inlet_info.dt_id
            WHERE mch_inlet_info.mch_id = %s;
                """, (self.mch_id, ))
        fields = [
            'mch_id', 'mch_name', 'mch_shortname',
            'province', 'city', 'district', 'address', 'contact', 'head_mobile', 'head_name',
            'mobile', 'service_phone', 'email', 'auth_status',
            'balance_type', 'balance_name', 'bank_no',
            'balance_account', 'id_card_no', 'balance_status', 'create_at',
            'auth_at', 'id_card_img_b', 'id_card_img_f',
            'dt_name', 'bank_name', 'wx_sub_mch_id', 'wx_app_sub_mch_id', 'jd_sub_mch_id',
            'ali_sub_mch_id', 'ali_level',
            'status',
            'wx_use_parent',
            'license_num',
            'license_start_date', 'license_end_date',
            'license_period',
            'license_scope', 'license_img', 'img_with_id_card',
            'pay_notify_url', 'dt_sub_name', 'dt_type', 'cs_id',
            'annex_img1', 'annex_img2', 'annex_img3', 'annex_img4', 'annex_img5', 'activate_email_tag',
            'license_type', 'head_type'
        ]
        data = dict(zip(fields, ret))
        data['activate_email_tag'] = "商户" if data['activate_email_tag'] == 1 else "渠道商"

        extensions = dict()
        sql = """SELECT extension_name, extension_value FROM role_info_extension WHERE role_id=%s and role_type=%s"""
        for each_extension in self.db.selectSQL(sql, (self.mch_id, 'mch'), fetchone=False, use_dict=True):
            extensions[each_extension['extension_name']] = each_extension['extension_value']
        data.update(extensions)
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
            query = """select
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
            query = """select
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
    def get_payment(self):
        """
        SELECT payment_type,payment_rate,activated_status FROM mch_payment WHERE mch_id=100000000846;
        """
        ret = self.db.selectSQL(
            """SELECT payment_type,payment_rate,activated_status FROM mch_payment WHERE mch_id=%s;""", (
                self.mch_id,),
            fetchone=False)
        fields = ['pay_type', 'pay_rate', 'activated_status', 'operate']
        data = [dict(zip(fields, [i[0], i[1] / 10, i[2], 1])) for i in ret] if ret else []
        raise gen.Return(data)

    @gen.coroutine
    def get_d0_withdraw_fee(self):
        ret = self.db.selectSQL(
            """
            SELECT wx,alipay FROM d0_withdraw_fee WHERE role=%s and role_type=%s;""", (self.mch_id, 'mch'),
            fetchone=True)
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
    def get_new_payment(self):
        ret = self.db.selectSQL("""SELECT uline_payment_code,settle_rate, settle_rate,
            activated_status, uline_settle_id, payment_type,
            withdraw_fee, withdraw_rate FROM mch_payment WHERE mch_id=%s;""", (self.mch_id,),
                                fetchone=False)
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
    def get_auth_info(self):
        query = """select to_char(create_at, 'YYYY-MM-DD HH24:MI:SS'),comment,auth_user,auth_status from auth_mch_info where mch_id=%s order by create_at"""
        ret = self.db.selectSQL(query, (self.mch_id,), fetchone=False)
        fields = ['auth_at', 'auth_comment', 'auth_user', 'auth_status']
        data = [dict(zip(fields, i)) for i in ret] if ret else []
        for auth_info in data:
            auth_status = auth_info['auth_status']
            auth_info['comment'] = AUTH_STATUS[str(auth_status)]
            if not self.open_review:
                if auth_status in [constants.AUTH_STATUS_SUBMIT, constants.AUTH_STATUS_PREVIEWD]:
                    auth_info['comment'] = '审核中'
                elif auth_status in [constants.AUTH_STATUS_FIRST_DENY, constants.AUTH_STATUS_DENY]:
                    auth_info['comment'] = '审核驳回'
        raise gen.Return(data)

    @gen.coroutine
    def get_activated_info(self):
        query = """
            select
            to_char(create_at, 'YYYY-MM-DD HH24:MI:SS'),
            comment, payment_type, activated_user from activated_mch_info
            where mch_id=%s order by create_at;"""
        ret = self.db.selectSQL(query, (self.mch_id,), fetchone=False)
        fields = ['activated_at', 'comment', 'payment_type', 'activated_user']
        data = [dict(zip(fields, i)) for i in ret] if ret else []
        for row in data:
            row['uline_payment_code'] = old_payment_relations.get(str(row.get('payment_type')))
            row['sort'] = rate_sort.get(row.get('uline_payment_code'))
        data = sorted(data, key=lambda k: (k.get('activated_at'), k.get('sort')), reverse=True)
        raise gen.Return(data)

    @gen.coroutine
    def format_inlet_and_balance(self):
        inlet_and_balance = yield self.get_inlet_and_balance()
        base_dir = '/static/uploads/mch/idcard'
        file_dir = os.path.join(base_dir, '{}'.format(self.mch_id))
        img_b_path = os.path.join(file_dir, inlet_and_balance.get('id_card_img_b'))
        img_f_path = os.path.join(file_dir, inlet_and_balance.get('id_card_img_f'))
        if inlet_and_balance.get('license_img', None):
            license_img_path = os.path.join(file_dir, inlet_and_balance.get('license_img'))
        else:
            license_img_path = None
        if inlet_and_balance.get('img_with_id_card', None):
            img_with_id_card_path = os.path.join(
                file_dir, inlet_and_balance.get('img_with_id_card'))
        else:
            img_with_id_card_path = None
        inlet_and_balance['id_card_img_b'] = img_b_path
        inlet_and_balance['id_card_img_f'] = img_f_path
        if license_img_path:
            inlet_and_balance['license_img'] = license_img_path
        else:
            inlet_and_balance['license_img'] = None

        if img_with_id_card_path:
            inlet_and_balance['img_with_id_card'] = img_with_id_card_path
        else:
            inlet_and_balance['img_with_id_card'] = None

        for img_count in range(1, 6):
            img_key = 'annex_img' + str(img_count)
            this_annex = inlet_and_balance.get(img_key)
            if this_annex:
                inlet_and_balance[img_key] = os.path.join(file_dir, this_annex)
            else:
                inlet_and_balance[img_key] = this_annex

        db_mch_front_img = inlet_and_balance.get('mch_front_img', None)
        inlet_and_balance['mch_front_img'] = os.path.join(
            file_dir, db_mch_front_img) if db_mch_front_img else None

        db_mch_inner_img = inlet_and_balance.get('mch_inner_img', None)
        inlet_and_balance['mch_inner_img'] = os.path.join(
            file_dir, db_mch_inner_img) if db_mch_inner_img else None

        db_mch_desk_img = inlet_and_balance.get('mch_desk_img', None)
        inlet_and_balance['mch_desk_img'] = os.path.join(
            file_dir, db_mch_desk_img) if db_mch_desk_img else None

        for img_index in range(1, 6):
            img_key = 'wx_dine_annex_img' + str(img_index)
            annex_img_name = inlet_and_balance.get(img_key)
            inlet_and_balance[img_key] = os.path.join(file_dir, annex_img_name) if annex_img_name else None

        raise gen.Return(inlet_and_balance)

    @gen.coroutine
    def get_mch_rate(self):
        query = '''select rate from mch_user where mch_id=%s;'''
        ret = self.db.selectSQL(query, (self.mch_id,), fetchone=True)
        raise gen.Return(ret[0])

    def get_mch_risk_info(self):
        query = """select merchant_risk_item.risk_type from merchant_risk_item
                   inner join merchant_risk on merchant_risk.id=merchant_risk_item.merchant_risk_id
                   where  merchant_risk_item.has_risk>0 and merchant_risk.status=1 and merchant_risk_item.status=1
                      and sys_id=%s and sys_type_id=%s;
                """
        ret = self.db.selectSQL(query, (self.mch_id, 'mch'), fetchone=False, use_dict=True)
        risk_type_list = [merchant_risk_util.get_merchaint_risk_type_msg(risk_info['risk_type']) for risk_info in ret]
        risk_info = {
            'risk_msg': u'{}存在风险'.format('、'.join(risk_type_list)) if risk_type_list else '',
        }
        return risk_info

    def get_mch_settle_status(self):
        query = """select credit,settle from risk_control WHERE sys_id=%s and sys_type_id=%s"""
        result = self.db.selectSQL(query, (self.mch_id, 'mch'), fetchone=True, use_dict=True)
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