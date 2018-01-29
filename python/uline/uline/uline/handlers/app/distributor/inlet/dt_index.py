# -*- coding: utf-8 -*-
from __future__ import division
import os
import json
from tornado.web import authenticated, asynchronous
from tornado import gen
from uline.handlers.baseHandlers import DtAdminHandler
from uline.public.constants import AUTH_STATUS, ACTIVATED_STATUS, PAYMENT, AVAILABLE_PAYMENTS_FORMAT, rate_sort
from uline.utils.record import record_utils
from uline.public.permit import check_permission
from uline.settings import FEATURE_SWITCH


class DistributorInletIndexHandler(DtAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        self.dt_id = self.current_user

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
        inlet_and_balance.update({
            'role': self.role,
            'payment': payment,
            'auth_info': auth_info,
            'activated_info': activated_info
        })
        update_records = yield record_utils.select_change_record(self, self.dt_id)
        if update_records:
            update_records = json.loads(update_records[1])
            record_utils.swap_value(update_records, inlet_and_balance, change_id=self.dt_id)
        for each_payment in inlet_and_balance.get('payment', list()):
            # each_payment['pay_type_name'] = PAYMENT[str(each_payment['pay_type'])]
            each_payment['pay_type_name'] = AVAILABLE_PAYMENTS_FORMAT.get(
                each_payment.get('uline_payment_code'))
            each_payment['activated_status'] = ACTIVATED_STATUS[str(each_payment['activated_status'])]
        status_num = inlet_and_balance['auth_status']
        for each_payment in inlet_and_balance.get('payment', {}):
            each_payment['pay_type_name'] = AVAILABLE_PAYMENTS_FORMAT.get(
                each_payment.get('uline_payment_code'))
        if status_num in [1, 4]:
            inlet_and_balance['auth_status'] = "审核中"
        else:
            inlet_and_balance['auth_status'] = AUTH_STATUS[str(status_num)]
        inlet_and_balance['activated_status'] = ACTIVATED_STATUS[str(inlet_and_balance['activated_status'])]
        self.render('distributor/inlet/distributor.html', form=inlet_and_balance)

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
               dt_inlet_info.license_num,
               to_char(dt_inlet_info.license_start_date, 'YYYY-MM-DD'),
               to_char(dt_inlet_info.license_end_date, 'YYYY-MM-DD'),
               dt_inlet_info.license_period,
               dt_inlet_info.license_scope,
               dt_inlet_info.license_img,
               dt_inlet_info.alipay_pid
                FROM dt_inlet_info
                INNER JOIN dt_balance ON dt_inlet_info.dt_id = dt_balance.dt_id
                INNER JOIN balance_bank_info on dt_balance.bank_no = balance_bank_info.bank_no
                WHERE dt_inlet_info.dt_id = %s;
        """, (self.current_user,))
        fields = [
            'dt_id', 'dt_name', 'province', 'city', 'district', 'address',
            'contact', 'mobile', 'service_phone', 'email', 'auth_status',
            'activated_status', 'balance_type', 'balance_name', 'bank_no', 'balance_account', 'id_card_no',
            'create_at', 'auth_at', 'id_card_img_b', 'id_card_img_f', 'bank_name',
            'license_num',
            'license_start_date', 'license_end_date',
            'license_period',
            'license_scope', 'license_img', 'alipay_pid'
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
            """SELECT payment_type,payment_rate,activated_status FROM dt_payment WHERE dt_id=%s ORDER BY payment_type ASC;""", (
                self.dt_id,),
            fetchone=False)
        fields = ['pay_type_name', 'pay_rate', 'activated_status', 'pay_type']
        data = [dict(zip(fields, [PAYMENT[str(i[0])], i[1] / 10.0, i[2], i[0]]))
                for i in ret] if ret else []
        raise gen.Return(data)

    @gen.coroutine
    def get_new_payment(self):
        ret = self.db.selectSQL(
            """SELECT uline_payment_code,settle_rate,settle_rate, activated_status, uline_settle_id, payment_type,
                      withdraw_fee, withdraw_rate FROM dt_payment WHERE dt_id=%s;;""", (
                self.dt_id,),
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
        ret = self.db.selectSQL(
            """
            SELECT wx,alipay FROM d0_withdraw_fee WHERE role=%s and role_type=%s;""", (self.dt_id, 'dt'), fetchone=True)
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
        query = """select to_char(create_at, 'YYYY-MM-DD HH24:MI:SS'),comment,auth_status
                  from auth_dt_info
                  where dt_id=%s and auth_status <> 4 order by create_at"""
        ret = self.db.selectSQL(query, (self.dt_id,), fetchone=False)
        fields = ['auth_at', 'auth_comment', 'auth_status']
        data = [dict(zip(fields, [i[0], i[1], i[2]])) for i in ret] if ret else []
        for d in data:
            d['comment'] = "审核中" if d['auth_status'] == 1 else AUTH_STATUS[str(d['auth_status'])]
        raise gen.Return(data)

    @gen.coroutine
    def get_activated_info(self):
        query = """select to_char(create_at, 'YYYY-MM-DD HH24:MI:SS'), comment from activated_dt_info where dt_id=%s"""
        ret = self.db.selectSQL(query, (self.dt_id, ), fetchone=False)
        fields = ['activated_at', 'comment']
        raise gen.Return([dict(zip(fields, [i[0], i[1]])) for i in ret] if ret else [])

    @gen.coroutine
    def format_inlet_and_balance(self):
        inlet_and_balance = yield self.get_inlet_and_balance()
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
