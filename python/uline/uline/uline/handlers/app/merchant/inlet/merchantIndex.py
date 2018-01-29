# -*- coding: utf-8 -*-
from __future__ import division
import os
import json
from tornado.web import authenticated, asynchronous
from tornado import gen
from uline.handlers.baseHandlers import MchAdminHandler
from uline.public.constants import AUTH_STATUS, ACTIVATED_STATUS, PAYMENT, rate_sort, AVAILABLE_PAYMENTS_FORMAT, \
    old_payment_relations
from uline.utils.record import record_utils
from uline.settings import QR_SCAN_URL, FEATURE_SWITCH
from uline.public import auth_util, constants
from uline.public.permit import check_permission

from uline.utils.wxpay.wx_util import get_wx_configs


class MerchantInletIndexHandler(MchAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        self.mch_id = self.current_user

    @asynchronous
    @gen.coroutine
    def get(self):
        # 先连表查询进件信息表和结算明细表,再单独查询支付信息表
        inlet_and_balance = yield self.format_inlet_and_balance()
        # payment = yield self.get_payment()
        self.NEW_INLET = FEATURE_SWITCH.get('NEW_INLET')
        self.role = {'wx_draw_fee': '', 'ali_draw_fee': '', 'wx_draw_rate': '', 'ali_draw_rate': ''}
        payment = yield self.get_new_payment()
        if not self.NEW_INLET:
            self.role = yield self.get_d0_withdraw_fee()
        auth_info = yield self.get_auth_info()
        activated_info = yield self.get_activated_info()
        wx_ali_ind_info = yield self.get_wx_ali_ind_code()
        inlet_and_balance.update(wx_ali_ind_info)
        # 修改要显示的费率
        subsidize_info = self.get_mch_subsidize_info()
        risk_account_status = self.get_mch_settle_status()
        inlet_and_balance.update({
            'role': self.role,
            'payment': payment,
            'auth_info': auth_info,
            'activated_info': activated_info,
            'subsidize_info': subsidize_info,
        })
        inlet_and_balance.update(risk_account_status)

        update_records = yield record_utils.select_change_record(self, self.mch_id, change_type=2)
        if update_records:
            result = json.loads(update_records[1])
            record_utils.swap_value(result,  inlet_and_balance, change_id=self.mch_id, role_type=2)
        status_num = inlet_and_balance['auth_status']

        for each_payment in inlet_and_balance.get('payment', list()):
            each_payment['pay_type_name'] = AVAILABLE_PAYMENTS_FORMAT.get(
                each_payment.get('uline_payment_code'))
            each_payment['activated_status'] = ACTIVATED_STATUS[str(each_payment['activated_status'])]
        inlet_and_balance['auth_status'] = auth_util.print_auth_status_simple(status_num)
        # if status_num in [1, 4]:
        #     inlet_and_balance['auth_status'] = "审核中"
        # else:
        #     inlet_and_balance['auth_status'] = AUTH_STATUS[str(status_num)]
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
        for each_payment in inlet_and_balance.get('payment', {}):
            each_payment['pay_type_name'] = AVAILABLE_PAYMENTS_FORMAT.get(
                each_payment.get('uline_payment_code'))
        download_url = '/common/qrdownload?text={0}/r?m={1}&size={{}}&save_name={2}({1}).jpg'.format(
            QR_SCAN_URL, self.mch_id, inlet_and_balance.get('mch_shortname'))
        download_qr_url = [download_url.format(size) for size in [142, 258, 430]]
        self.render('merchant/inlet/merchant.html', form=inlet_and_balance, QR_SCAN_URL=QR_SCAN_URL,
                    download_qr_url=download_qr_url)

    def generate_unchanged_render_params(self):
        return {
            "license_type_map": constants.LICENSE_TYPE_MAP,
            "head_type_map": constants.HEAD_TYPE_MAP,
        }

    @gen.coroutine
    def get_inlet_and_balance(self):
        """
        """
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
           mch_inlet_info.activated_status,
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
           mch_user.jd_sub_mch_id,
           mch_user.ali_level,
           mch_user.status,
           mch_inlet_info.license_num,
           to_char(mch_inlet_info.license_start_date, 'YYYY-MM-DD'),
           to_char(mch_inlet_info.license_end_date, 'YYYY-MM-DD'),
           mch_inlet_info.license_period,
           mch_inlet_info.license_scope,
           mch_inlet_info.license_img,
           mch_inlet_info.img_with_id_card,
           mch_inlet_info.pay_notify_url,
           mch_user.wx_app_sub_mch_id,
           mch_inlet_info.annex_img1,
           mch_inlet_info.annex_img2,
           mch_inlet_info.annex_img3,
           mch_inlet_info.annex_img4,
           mch_inlet_info.annex_img5,
           mch_inlet_info.license_type,
           mch_inlet_info.head_type
            FROM mch_inlet_info
            INNER JOIN mch_user on mch_inlet_info.mch_id = mch_user.mch_id
            INNER JOIN mch_balance ON mch_inlet_info.mch_id = mch_balance.mch_id
            INNER JOIN dt_user on mch_inlet_info.dt_id = dt_user.dt_id
            INNER JOIN balance_bank_info on mch_balance.bank_no = balance_bank_info.bank_no
            WHERE mch_inlet_info.mch_id = %s;
        """, (self.current_user,))
        fields = [
            'mch_id', 'mch_name', 'mch_shortname', 'province', 'city', 'district',
            'address',
            'contact', 'head_mobile', 'head_name',
            'mobile', 'service_phone', 'email', 'auth_status',
            'activated_status', 'balance_type',
            'balance_name', 'bank_no', 'balance_account',
            'id_card_no', 'create_at', 'auth_at',
            'id_card_img_b', 'id_card_img_f',
            'dt_name', 'bank_name', 'wx_sub_mch_id', 'ali_sub_mch_id', 'jd_sub_mch_id',
            'ali_level', 'status',
            'license_num',
            'license_start_date', 'license_end_date',
            'license_period',
            'license_scope', 'license_img', 'img_with_id_card',
            'pay_notify_url', 'wx_app_sub_mch_id',
            'annex_img1', 'annex_img2', 'annex_img3', 'annex_img4', 'annex_img5',
            'license_type', 'head_type'
        ]
        data = dict(zip(fields, ret))

        extensions = dict()
        sql = """SELECT extension_name, extension_value FROM role_info_extension WHERE role_id=%s and role_type=%s"""
        extension_infos = self.db.selectSQL(sql, (self.mch_id, 'mch'), fetchone=False, use_dict=True)
        if extension_infos:
            for each_extension in extension_infos:
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
    def get_payment(self):
        ret = self.db.selectSQL(
            """SELECT payment_type,payment_rate,activated_status FROM mch_payment WHERE mch_id=%s;""", (
                self.mch_id,),
            fetchone=False)
        fields = ['pay_type_name', 'pay_rate', 'activated_status', 'pay_type']
        data = [dict(zip(fields, [
            PAYMENT[str(i[0])], i[1] / 10, i[2], i[0]])) for i in ret] if ret else []
        raise gen.Return(data)

    @gen.coroutine
    def get_new_payment(self):
        ret = self.db.selectSQL(
            """SELECT uline_payment_code,settle_rate,settle_rate, activated_status, uline_settle_id, payment_type,
                      withdraw_fee, withdraw_rate FROM mch_payment WHERE mch_id=%s;""", (
                self.mch_id,),
            fetchone=False)
        fields = ['uline_payment_code', 'settle_rate', 'pay_rate',
                  'activated_status', 'uline_settle_id', 'pay_type', 'withdraw_fee', 'withdraw_rate']
        data = [dict(zip(fields, [i[0], i[1] / 10, i[2] / 10, i[3], i[4], i[5], i[6], i[7]]))
                for i in ret] if ret else []
        for row in data:
            # if row.get('uline_settle_id') == 2:
            #     row['uline_payment_code'] += '_D0'
            row['sort'] = rate_sort.get(row.get('uline_payment_code'))
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
    def get_d0_withdraw_fee(self):
        sql = """SELECT wx,alipay FROM d0_withdraw_fee WHERE role=%s and role_type=%s;"""
        ret = self.db.selectSQL(sql, (self.mch_id, 'mch'), fetchone=True)
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
    def get_auth_info(self):
        query = """select to_char(create_at, 'YYYY-MM-DD HH24:MI:SS'),comment,auth_status from auth_mch_info
                    where mch_id=%s and auth_status <> 4 order by create_at"""
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
                auth_info['comment'] = '审核驳回'
            auth_info_list.append(auth_info)

        raise gen.Return(auth_info_list)

    @gen.coroutine
    def get_activated_info(self):
        query = """
            select
            to_char(create_at, 'YYYY-MM-DD HH24:MI:SS'),
            payment_type,comment from activated_mch_info where mch_id=%s;"""
        ret = self.db.selectSQL(query, (self.mch_id,), fetchone=False)
        fields = ['activated_at', 'payment_type', 'comment']
        data = [dict(zip(fields, [i[0], constants.PAYMENT[str(i[1])], i[2]])) for i in ret] if ret else []
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
        img_b_path = os.path.join(
            file_dir, inlet_and_balance.get('id_card_img_b'))
        img_f_path = os.path.join(
            file_dir, inlet_and_balance.get('id_card_img_f'))
        if inlet_and_balance.get('license_img', None):
            license_img_path = os.path.join(
                file_dir, inlet_and_balance.get('license_img'))
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
                inlet_and_balance[img_key] = os.path.join(
                    file_dir, this_annex)
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
        # 先默认给个空
        inlet_and_balance['unionpay_level'] = ''
        inlet_and_balance['unionpay_limit'] = ''
        raise gen.Return(inlet_and_balance)

    def get_mch_subsidize_info(self):
        query = """select rate from discount where role_id=%s and role=%s and valid=1 order by create_at desc limit 1"""
        ret = self.db.selectSQL(query, (self.current_user, 'mch'), fetchone=True, use_dict=True)
        subsidize_info = {}
        if ret and ret['rate']:
            rate_info = json.loads(ret['rate'])
            rate_info['weixin'] = rate_info['weixin'] / 100.0
            rate_info['alipay'] = rate_info['alipay'] / 100.0
            subsidize_info.update(rate_info)
        return subsidize_info

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
