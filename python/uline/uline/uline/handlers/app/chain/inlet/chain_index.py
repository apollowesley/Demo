# -*- coding: utf-8 -*-
from __future__ import division
import os
import json
from tornado.web import authenticated, asynchronous
from tornado import gen
from uline.public import log
from uline.handlers.baseHandlers import ChainAdminHandler
from uline.public.constants import AUTH_STATUS, ACTIVATED_STATUS, PAYMENT
from uline.utils.record import record_utils

from uline.utils.wxpay.wx_util import get_wx_configs
from uline.public import auth_util, constants
from uline.public.permit import check_permission


class ChainInletIndexHandler(ChainAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        self.dt_id = self.current_user

    def generate_unchanged_render_params(self):
        return {
            'print_status': auth_util.print_auth_status,
            'license_type_map': constants.LICENSE_TYPE_MAP,
            'head_type_map': constants.HEAD_TYPE_MAP,
        }

    @asynchronous
    @gen.coroutine
    def get(self):
        # 先连表查询进件信息表和结算明细表,再单独查询支付信息表
        inlet_and_balance = yield self.format_inlet_and_balance()
        payment = yield self.get_payment()
        auth_info = yield self.get_auth_info()
        activated_info = yield self.get_activated_info()
        wx_ali_ind_info = yield self.get_wx_ali_ind_code()
        subsidize_info = self.get_mch_subsidize_info()
        inlet_and_balance.update(wx_ali_ind_info)
        # 修改要显示的费率
        inlet_and_balance.update({
            'payment': payment,
            'auth_info': auth_info,
            'activated_info': activated_info,
            'subsidize_info': subsidize_info,
        })
        update_records = yield record_utils.select_change_record(self, self.dt_id)
        if update_records:
            update_records = json.loads(update_records[1])
            record_utils.swap_value(
                update_records, inlet_and_balance, change_id=self.dt_id)

        for each_payment in inlet_and_balance.get('payment', list()):
            each_payment['pay_type_name'] = PAYMENT[str(each_payment['pay_type'])]
            each_payment['activated_status'] = ACTIVATED_STATUS[str(each_payment['activated_status'])]

        status_num = inlet_and_balance['auth_status']
        inlet_and_balance['auth_status'] = auth_util.print_auth_status_simple(status_num)
        inlet_and_balance['activated_status'] = ACTIVATED_STATUS[str(
            inlet_and_balance['activated_status'])]

        wx_pay_configs = list()
        wx_sub_mch_id = inlet_and_balance['wx_sub_mch_id']
        if wx_sub_mch_id:
            wx_reg_config = yield get_wx_configs(wx_sub_mch_id)
            wx_reg_config['channel'] = 2
            wx_reg_config['channel_str'] = u'线下'
            inlet_and_balance['wx_reg_config'] = wx_reg_config
            wx_pay_configs.append(wx_reg_config)
        else:
            inlet_and_balance['wx_reg_config'] = None
        wx_app_sub_mch_id = inlet_and_balance['wx_app_sub_mch_id']
        if wx_app_sub_mch_id:
            wx_app_config = yield get_wx_configs(wx_app_sub_mch_id, channel_type=6)
            wx_app_config['channel'] = 6
            wx_app_config['channel_str'] = u'线上'
            inlet_and_balance['wx_app_config'] = wx_app_config
            wx_pay_configs.append(wx_app_config)
        else:
            inlet_and_balance['wx_app_config'] = None

        inlet_and_balance['wx_pay_configs'] = wx_pay_configs
        log.detail.info('inlet_and_balance:%s' % str(inlet_and_balance))
        self.render('chain/inlet/chain.html',
                    form=inlet_and_balance)

    @gen.coroutine
    def get_inlet_and_balance(self):
        """
        """
        ret = self.db.selectSQL("""
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
               dt_inlet_info.activated_status,
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
               dt_user.jd_sub_mch_id,
               dt_user.ali_level,
               dt_inlet_info.license_num,
               to_char(dt_inlet_info.license_start_date, 'YYYY-MM-DD'),
               to_char(dt_inlet_info.license_end_date, 'YYYY-MM-DD'),
               dt_inlet_info.license_period,
               dt_inlet_info.license_scope,
               dt_inlet_info.license_img,
               dt_user.wx_sub_mch_id,
               dt_user.wx_app_sub_mch_id,
               dt_inlet_info.pay_notify_url,
               dt_inlet_info.head_mobile,
               dt_inlet_info.head_name,
               dt_inlet_info.license_type,
               dt_inlet_info.head_type
                FROM dt_inlet_info
                INNER JOIN dt_balance ON dt_inlet_info.dt_id = dt_balance.dt_id
                INNER JOIN dt_user ON dt_user.dt_id = dt_inlet_info.dt_id
                INNER JOIN balance_bank_info on dt_balance.bank_no = balance_bank_info.bank_no
                WHERE dt_inlet_info.dt_id = %s;
        """, (self.current_user,))
        fields = [
            'dt_id', 'dt_name', 'province', 'city', 'district', 'address',
            'contact', 'mobile', 'service_phone', 'email', 'auth_status',
            'activated_status', 'balance_type', 'balance_name', 'bank_no', 'balance_account', 'id_card_no',
            'create_at', 'auth_at', 'id_card_img_b', 'id_card_img_f', 'bank_name',
            'wx_sub_mch_id', 'ali_sub_mch_id', 'jd_sub_mch_id', 'ali_level',
            'license_num',
            'license_start_date', 'license_end_date',
            'license_period',
            'license_scope', 'license_img', 'wx_sub_mch_id', 'wx_app_sub_mch_id', 'pay_notify_url',
            'head_mobile', 'head_name', 'license_type', 'head_type'
        ]
        data = dict(zip(fields, ret))
        raise gen.Return(data)

    @gen.coroutine
    def get_old_ind_code(self):
        query = """select wx_ind_code, old_ind_code from dt_inlet_info where dt_id=%s;"""
        ret = self.db.selectSQL(query, (self.dt_id,))
        raise gen.Return(ret)

    @gen.coroutine
    def get_wx_ali_ind_code(self):
        ret = [''] * 4
        ret_ind_code = yield self.get_old_ind_code()
        if ret_ind_code[0]:
            query = """
                select
                dt_inlet_info.u_ind_code,
                industry_uline_info.industry_name,
                industry_ali_info.industry_name,
                industry_wx_info.industry_name
                from dt_inlet_info
                inner join industry_uline_info on industry_uline_info.industry_code = dt_inlet_info.u_ind_code
                inner join industry_ali_info on industry_ali_info.industry_code = dt_inlet_info.ali_ind_code
                inner join industry_wx_info on industry_wx_info.industry_code = dt_inlet_info.wx_ind_code
                where dt_inlet_info.dt_id=%s;"""
            ret = self.db.selectSQL(query, (self.dt_id,))
        else:
            query = """select industry_name from industry_uline_info where wx_ind_code=%s and status=2;"""
            wx_ind_code_ret = self.db.selectSQL(query, (ret_ind_code[1],))

            query = """
                select
                dt_inlet_info.u_ind_code,
                industry_uline_info.industry_name,
                industry_ali_info.industry_name
                from dt_inlet_info
                inner join industry_uline_info on industry_uline_info.industry_code = dt_inlet_info.u_ind_code
                inner join industry_ali_info on industry_ali_info.industry_code = dt_inlet_info.ali_ind_code
                where dt_inlet_info.dt_id=%s;"""
            u_ind_code_ret = self.db.selectSQL(query, (self.dt_id,))

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
        SELECT payment_type,payment_rate,activated_status FROM dt_payment WHERE dt_id=100000000846;
        """
        ret = self.db.selectSQL(
            """SELECT payment_type,payment_rate,activated_status FROM dt_payment WHERE dt_id=%s;""", (
                self.dt_id,),
            fetchone=False)
        fields = ['pay_type_name', 'pay_rate', 'activated_status', 'pay_type']
        data = [dict(zip(fields, [PAYMENT[str(i[0])], i[1] / 10.0, i[2], i[0]]))
                for i in ret] if ret else []
        raise gen.Return(data)

    @gen.coroutine
    def get_auth_info(self):
        query = """select to_char(create_at, 'YYYY-MM-DD HH24:MI:SS'),comment,auth_status
                  from auth_dt_info
                  where dt_id=%s and auth_status <> 4 order by create_at"""
        ret = self.db.selectSQL(query, (self.dt_id,), fetchone=False)
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
                auth_info['comment'] = '审核驳回'
            auth_info_list.append(auth_info)

        raise gen.Return(auth_info_list)

    @gen.coroutine
    def get_activated_info(self):
        query = """select to_char(create_at, 'YYYY-MM-DD HH24:MI:SS'), payment_type, comment from activated_dt_info where dt_id=%s"""
        ret = self.db.selectSQL(query, (self.dt_id,), fetchone=False)
        fields = ['activated_at', 'payment_type', 'comment']
        raise gen.Return([dict(zip(fields, [i[0], constants.PAYMENT[str(i[1])], i[2]]))
                          for i in ret] if ret else [])

    @gen.coroutine
    def format_inlet_and_balance(self):
        inlet_and_balance = yield self.get_inlet_and_balance()
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
