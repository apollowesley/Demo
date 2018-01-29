# -*- coding: utf-8 -*-
'''
BEGIN
ajax请求 审核/驳回渠道商进件信息
    必选参数:

    可选参数:

    成功:
        {"code": 200, "msg": "成功"}
    失败:
        {"code": 406, "msg": "失败"}
END
'''
import json

from tornado import gen
from tornado.httpclient import (
    AsyncHTTPClient,
)
from tornado.web import authenticated, asynchronous

from uline.handlers.baseHandlers import IntBkAdminHandler
from uline.public import common, log, constants
from uline.public.constants import AUTH_STATUS, translate_payment_type, old_payment_relations, new_payment_relations
from uline.settings import FEATURE_SWITCH
from uline.settings import (
    WX_MCH_ID, WXPAY_KEY, APPID, WX_PUB_KEY, WX_PRIVATE_KEY, WX_ROOT_CA,
    WX_APP_MCH_ID, WXPAY_APP_KEY, WX_APP_APPID, WX_APP_PUB_KEY,
    WX_APP_PRIVATE_KEY, WX_APP_ROOT_CA,
    WX_0_WX_MCH_ID, WX_0_WXPAY_KEY, WX_0_APPID, BANK_NAME
)
from uline.utils.record import record_utils
from uline.utils.wxpay.merchantInletToWxV2 import UpdateMerchantInletToWx
from uline.utils.wxpay.query_wx import create_wx_mch
from uline.utils.wxpay.util import xml_to_dict
from .form import AuthDistributorInfo
from uline.public.permit import check_permission
from uline.model.uline.user import Employee
from uline.model.uline.info import UserProfile
from uline.model.uline.base import uline_session


class AuthDistributorInletStatusHandler(IntBkAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        form = AuthDistributorInfo(self)
        if not form.validate():
            f_rsp = common.f_rsp(code=406, msg='fail')
            self.finish(f_rsp)
        self.dt_id = form.dt_id.data
        self.create_at = self.update_at = common.timestamp_now()

        self.open_review = FEATURE_SWITCH['REVIEW']
        if self.open_review:
            self.bk_email = self.auth_user_email(self.session.get('bk_id'))

            with self.db.get_db() as cur:
                ret = self.latest_status(cur)
                self.query_status, self.query_user = ret[0], ret[1]
                if self.query_status == 1:
                    self.status = 4
                    self.rsp = common.scc_rsp(code=200, msg='fsuccess')
                    self.add_auth_inlet_info()
                    self.auth_dt_inlet()
                    self.finish(self.rsp)
                elif self.query_status == 4:
                    self.status = 2
                    self.rsp = common.scc_rsp(code=200, msg='csuccess')
                    if self.query_user == self.bk_email:
                        self.rsp = common.f_rsp(code=406, msg='fail')
                        self.finish(self.rsp)
                else:
                    self.rsp = common.f_rsp(code=406, msg='fail')
                    self.finish(self.rsp)
        else:
            self.status = 2
            self.rsp = common.scc_rsp(code=200, msg='success')
        self.has_been_authed = self.has_authed()
        self.open_daily_cut = FEATURE_SWITCH.get('OPEN_DAILY_CUT', False) and self.has_been_authed

    @asynchronous
    @gen.coroutine
    def get(self):
        # print self.get_arguments()
        self.bk_email = yield self.get_bk_email()
        wx_reg_flag, wx_app_flag = True, True
        # wx_reg_pay = yield self.get_dt_wx_reg_payment()
        # wx_app_pay = yield self.get_dt_wx_app_payment()
        #
        # wx_id = yield self.get_dt_user_wx_id()
        # dt_inlet_info = yield self.get_dt_inlet_info()
        # 由于微信端渠道商进件有调整，不对其进行api进件，但保留原始信息
        wx_reg, wx_app = "success", "success"

        if not wx_reg_flag or not wx_app_flag:
            log.exception.info('进件到微信失败 wx_reg_flag:{}, wx_app_flag:{}'.format(
                wx_reg_flag, wx_app_flag))
            self.rsp = common.f_rsp(code=406, msg='进件到微信失败')

            comment_news = [wx_reg, wx_app]
            field = ["微信支付进件:{}", "微信APP支付进件:{}"]
            show_comment = "  ".join(_f.format(_com)
                                     for _f, _com in zip(field, comment_news) if _com != "success")

            yield self.add_fail_auth_inlet_info(show_comment)
            yield record_utils.rollback(self)

            self.status = 3
            yield self.auth_dt_inlet()
        else:
            yield self.update_dt_user()
            yield self.auth_dt_inlet()
            yield self.add_auth_inlet_info()
            self.invalid_past_record()
            yield self.update_changes()
            # if not self.has_been_authed:
            #     self.activated_all_payment()

        self.update_dt_active_status()
        self.write(self.rsp)
        self.finish()

    @gen.coroutine
    def update_changes(self):
        cut_record = dict()
        # 检查这个商户是否有变更金额
        query_change_record_json = self.db.selectSQL(
            """select data_json, id from change_record where status=1 and dt_id = %s;""",
            (self.dt_id,))
        employee = uline_session.query(Employee).filter(Employee.login_name == str(self.dt_id) + ".dt").one()

        if self.status in [2, "2"]:
            uline_session.query(Employee).filter(Employee.id == employee.id).update({'status': 1})
            uline_session.query(UserProfile).filter(UserProfile.id == employee.user_id).update({'status': 1})
            uline_session.commit()
        # 验证数据的合法性
        if query_change_record_json:
            query_change_record = json.loads(query_change_record_json[0])
            if 'payment' in query_change_record:
                payments = query_change_record['payment']
                payment_cut_info = yield self.update_dt_payments(payments)
                if payment_cut_info:
                    cut_record['payment'] = payment_cut_info

            if 'role' in query_change_record:
                role = query_change_record['role']
                yield self.apply_d0_withdraw_fee(role)
                cut_record['withdraw'] = role
                # 账户信息修改
            if 'balance_info' in query_change_record:
                balance_update_info = query_change_record['balance_info']
                update_keys = ['balance_type', 'balance_name', 'bank_no', 'balance_account',
                               'id_card_no']
                change_balance_info = {key: balance_update_info[key] for key in update_keys if
                                       key in balance_update_info}
                change_balance_info['update_at'] = self.update_at
                self.update_balance_info(change_balance_info)

            need_update_keys = ['dt_name', 'province', 'city', 'address', 'contact', 'mobile', 'service_phone', 'email',
                                'id_card_img_f', 'id_card_img_b', 'dt_id', 'license_num',
                                'license_start_date', 'license_end_date', 'license_period', 'license_scope',
                                'license_img', 'wx_channel_id', 'wx_app_channel_id', 'dt_type', 'u_ind_code',
                                'wx_ind_code', 'ali_ind_code', 'alipay_pid']
            change_inlet_info = {key: query_change_record[key] for key in need_update_keys if
                                 key in query_change_record}

            # 判断联系电话是否修改
            new_mobile = query_change_record.get('mobile')
            if new_mobile:
                # _password = common.bcrypt_pwd_new(str(self.get_dt_user_mobile()))
                result = yield self.auth_password(str(self.get_dt_user_mobile()))
                # 如果reesult为True,说明该渠道商还未登录，mobile已经被修改了
                if result:
                    # 将密码修改为新的联系电话
                    new_password = common.bcrypt_pwd_new(str(new_mobile))
                    _query = """update dt_user set password=%s where dt_id=%s;"""
                    self.db.executeSQL(_query, (new_password, self.dt_id))
                    uline_session.query(Employee).filter(Employee.login_name == str(self.dt_id) + ".dt").update(
                        {'login_passwd': new_password})

            if change_inlet_info:
                self.update_dt_user_email(change_inlet_info.get('email'))
                self.update_dt_inlet_info(change_inlet_info)

            change_record_status = constants.CHANGE_RECORD_STATUS_ACCEPT
            if cut_record:
                change_record_status = constants.CHANGE_RECORD_STATUS_TO_CUT
                cut_record['change_record_id'] = query_change_record_json[1]
                cut_record['bk_id'] = self.current_user
                cut_record['bk_email'] = self.bk_email
                self.add_daily_cut_record(cut_record)

            query = """update change_record set status = %s, create_at = now() where dt_id = %s;"""
            self.db.executeSQL(query, (change_record_status, self.dt_id,))
            _employee = {"email": "email", "mobile": "phone1", "city": "city", "dt_name": "name"}
            employee_update = {_employee[i]: change_inlet_info[i] for i in _employee.keys() if change_inlet_info.get(i)}
            if employee_update:
                uline_session.query(UserProfile).filter(UserProfile.id == employee.user_id).update(employee_update)
                uline_session.commit()

    def update_balance_info(self, change_balance_info):
        """
        更新结算账户信息
        :param cur: 数据库相关游标
        :param change_balance_info: dict，需要修改的信息
        """
        sql = """update dt_balance set """
        update_colums = []
        params_values = []
        for key in change_balance_info:
            update_colums.append("""{}=%s""".format(key))
            params_values.append(change_balance_info[key])
        sql = sql + ','.join(update_colums)
        where_str = " where dt_id=%s;"
        sql = sql + where_str
        params_values.append(self.dt_id)
        self.db.executeSQL(sql, tuple(params_values))

    def get_dt_user_mobile(self):
        ret = self.db.selectSQL(
            "select mobile from dt_inlet_info where dt_id=%s", (self.dt_id,))
        return ret[0]

    def update_dt_user_email(self, email):
        if email:
            sql = "update dt_user set email = %s where dt_id = %s"
            self.db.executeSQL(sql, (email, self.dt_id))

    @gen.coroutine
    def apply_d0_withdraw_fee(self, role):

        # {"ali_draw_fee": 9100, "wx_draw_rate": 190, "wx_draw_fee": 1900, "ali_draw_rate": 910},
        # {"wx": 10, '"alipay": 20}
        # 考虑老的wx和alipay
        # wx = role.get('wx')
        # alipay = role.get('alipay')
        # 手续费
        wx_draw_fee = role.get('wx') if role.get('wx') else role.get('wx_draw_fee')
        ali_draw_fee = role.get('alipay') if role.get('alipay') else role.get('ali_draw_fee')
        # 垫资费
        wx_draw_rate = role.get('wx_draw_rate')
        ali_draw_rate = role.get('ali_draw_rate')

        select_query = """select wx, alipay from d0_withdraw_fee where role=%s and role_type='dt'"""
        new_draw = """select withdraw_rate, withdraw_fee from dt_payment where dt_id=%s and uline_payment_code like %s"""
        sql_wx_draw = self.db.selectSQL(new_draw, (self.dt_id, 'WX%'), fetchone=True, use_dict=True)
        sql_ali_draw = self.db.selectSQL(new_draw, (self.dt_id, 'ALI%'), fetchone=True, use_dict=True)

        # select_mch = """
        #     select d0_withdraw_fee.wx, d0_withdraw_fee.alipay, mch_inlet_info.mch_id
        #     from d0_withdraw_fee inner join mch_inlet_info on mch_inlet_info.mch_id = d0_withdraw_fee.role
        #     where mch_inlet_info.dt_id = %s and d0_withdraw_fee.role_type='mch'
        #     and (d0_withdraw_fee.wx < %s or d0_withdraw_fee.alipay < %s)
        # """

        ret = self.db.selectSQL(select_query, (self.dt_id,), fetchone=True, use_dict=True)
        # ret_mchs = self.db.selectSQL(select_mch, (self.dt_id, wx, alipay), fetchone=False)
        withdraw_cut_info = {}
        # 如果没有ret是None
        if ret:
            if sql_wx_draw and sql_wx_draw.get('withdraw_fee'):
                ret['wx'] = sql_wx_draw.get('withdraw_fee')
            if sql_ali_draw and sql_ali_draw.get('withdraw_fee'):
                ret['alipay'] = sql_wx_draw.get('withdraw_fee')
            # 需要立即更新的信息
            immediately_update_info = {}
            # 数据从无到有的信息
            # or ret['wx'] is not None and wx is None:
            if ret.get('wx') is None and wx_draw_fee is not None:
                immediately_update_info['wx'] = wx_draw_fee
            elif ret.get('wx') != wx_draw_fee:
                withdraw_cut_info['wx'] = wx_draw_fee

            # or ret['wx'] is not None and wx is None:
            if ret.get('alipay') is None and ali_draw_fee is not None:
                immediately_update_info['alipay'] = ali_draw_fee
            elif ret.get('alipay') != ali_draw_fee:
                withdraw_cut_info['alipay'] = ali_draw_fee

            if sql_wx_draw and sql_wx_draw.get('withdraw_rate') is None and wx_draw_rate is not None:
                immediately_update_info['wx_draw_rate'] = wx_draw_rate
            elif sql_wx_draw and sql_wx_draw.get('withdraw_rate') != wx_draw_rate:
                withdraw_cut_info['wx_draw_rate'] = wx_draw_rate

            if sql_ali_draw and sql_ali_draw.get('withdraw_rate') is None and ali_draw_rate is not None:
                immediately_update_info['ali_draw_rate'] = ali_draw_rate
            elif sql_ali_draw and sql_ali_draw.get('withdraw_rate') != ali_draw_rate:
                withdraw_cut_info['ali_draw_rate'] = ali_draw_rate

            # 没有打开日切，则立即生效
            if not self.open_daily_cut:
                query = """update d0_withdraw_fee set wx=%s, alipay=%s where role=%s and role_type = %s"""
                self.db.executeSQL(query, (wx_draw_fee, ali_draw_fee, self.dt_id, 'dt'))

                # 保存到dt_paymnt表中(有空再优化，心情烦躁)
                if wx_draw_fee:
                    update_sql = """update dt_payment set withdraw_fee=%s where dt_id=%s and uline_payment_code like %s"""
                    self.db.executeSQL(update_sql, (wx_draw_fee, self.dt_id, 'WX%'))
                if ali_draw_fee:
                    update_sql = """update dt_payment set withdraw_fee=%s where dt_id=%s and uline_payment_code like %s"""
                    self.db.executeSQL(update_sql, (ali_draw_fee, self.dt_id, 'ALI%'))
                if wx_draw_rate:
                    update_sql = """update dt_payment set withdraw_rate=%s where dt_id=%s and uline_payment_code like %s"""
                    self.db.executeSQL(update_sql, (wx_draw_rate, self.dt_id, 'WX%'))
                if ali_draw_rate:
                    update_sql = """update dt_payment set withdraw_rate=%s where dt_id=%s and uline_payment_code like %s"""
                    self.db.executeSQL(update_sql, (ali_draw_rate, self.dt_id, 'ALI%'))

                # 判断手续费和垫资费是否有高于下级商户
                if sql_wx_draw and sql_wx_draw.get('withdraw_fee'):
                    # 调高微信手续费
                    if wx_draw_fee and wx_draw_fee > sql_wx_draw.get('withdraw_fee'):
                        query = """select mch_payment.mch_id from mch_payment
                            where mch_payment.withdraw_fee < %s and mch_payment.dt_id=%s and
                            mch_payment.payment_type in (1,2,3,4,5);"""
                        mch_ids = self.db.selectSQL(
                            query, (wx_draw_fee, self.dt_id), fetchone=False)
                        tuple_mch_ids = tuple([mch_id[0] for mch_id in mch_ids])
                        if mch_ids:
                            self.db.executeSQL("""
                              update mch_payment set withdraw_fee=%s where mch_id in %s
                              and payment_type in (1,2,3,4,5);""", (wx_draw_fee, tuple_mch_ids))

                if sql_wx_draw and sql_wx_draw.get('withdraw_rate'):
                    # 调高微信手续费
                    if wx_draw_rate and wx_draw_rate > sql_wx_draw.get('withdraw_rate'):
                        query = """select mch_payment.mch_id from mch_payment
                            where mch_payment.withdraw_rate < %s and mch_payment.dt_id=%s and
                            mch_payment.payment_type in (1,2,3,4,5);"""
                        mch_ids = self.db.selectSQL(
                            query, (wx_draw_rate, self.dt_id), fetchone=False)
                        tuple_mch_ids = tuple([mch_id[0] for mch_id in mch_ids])
                        if mch_ids:
                            self.db.executeSQL("""
                              update mch_payment set withdraw_rate=%s where mch_id in %s
                              and payment_type in (1,2,3,4,5);""", (wx_draw_rate, tuple_mch_ids))

                if sql_ali_draw and sql_ali_draw.get('withdraw_fee'):
                    # 调高微信手续费
                    if ali_draw_fee and ali_draw_fee > sql_ali_draw.get('withdraw_fee'):
                        query = """select mch_payment.mch_id from mch_payment
                            where mch_payment.withdraw_fee < %s and mch_payment.dt_id=%s and
                            mch_payment.payment_type in (7,8,9);"""
                        mch_ids = self.db.selectSQL(
                            query, (ali_draw_fee, self.dt_id), fetchone=False)
                        tuple_mch_ids = tuple([mch_id[0] for mch_id in mch_ids])
                        if mch_ids:
                            self.db.executeSQL("""
                              update mch_payment set withdraw_fee=%s where mch_id in %s
                              and payment_type in (7,8,9);""", (ali_draw_fee, tuple_mch_ids))

                if sql_ali_draw and sql_ali_draw.get('withdraw_rate'):
                    # 调高微信手续费
                    if ali_draw_rate and ali_draw_rate > sql_ali_draw.get('withdraw_rate'):
                        query = """select mch_payment.mch_id from mch_payment
                            where mch_payment.withdraw_rate < %s and mch_payment.dt_id=%s and
                            mch_payment.payment_type in (7,8,9);"""
                        mch_ids = self.db.selectSQL(
                            query, (ali_draw_rate, self.dt_id), fetchone=False)
                        tuple_mch_ids = tuple([mch_id[0] for mch_id in mch_ids])
                        if mch_ids:
                            self.db.executeSQL("""
                              update mch_payment set withdraw_rate=%s where mch_id in %s
                              and payment_type in (7,8,9);""", (ali_draw_rate, tuple_mch_ids))

            # 如果打开了日切，并且有立即生效的数据，则更新改数据
            elif immediately_update_info and self.open_daily_cut:
                update_infos = []
                params = list()
                for key in immediately_update_info:
                    if key in ['wx', 'alipay']:
                        update_infos.append("{}=%s".format(key))
                        params.append(immediately_update_info[key])
                params.extend([self.dt_id, 'dt'])
                if update_infos:
                    update_sql = """update d0_withdraw_fee set {} where role=%s and role_type=%s""".format(
                        ','.join(update_infos))
                    self.db.executeSQL(update_sql, tuple(params))

                # 需要立即更新的数据保存到dt_paymnet表中
                if immediately_update_info.get('wx'):
                    update_sql = """update dt_payment set withdraw_fee=%s where dt_id=%s and uline_payment_code like %s"""
                    self.db.executeSQL(update_sql, (wx_draw_fee, self.dt_id, 'WX%'))
                    # 判断是否有商户低于渠道商成本
                    if sql_wx_draw.get('withdraw_fee') and immediately_update_info.get('wx') > sql_wx_draw.get('withdraw_fee'):
                        query = """select mch_payment.mch_id from mch_payment
                            where mch_payment.withdraw_fee < %s and mch_payment.dt_id=%s and
                            mch_payment.payment_type in (1,2,3,4,5);"""
                        mch_ids = self.db.selectSQL(
                            query, (wx_draw_fee, self.dt_id), fetchone=False)
                        tuple_mch_ids = tuple([mch_id[0] for mch_id in mch_ids])
                        if mch_ids:
                            self.db.executeSQL("""
                              update mch_payment set withdraw_fee=%s where mch_id in %s
                              and payment_type in (1,2,3,4,5);""", (wx_draw_fee, tuple_mch_ids))

                if immediately_update_info.get('alipay'):
                    update_sql = """update dt_payment set withdraw_fee=%s where dt_id=%s and uline_payment_code like %s"""
                    self.db.executeSQL(update_sql, (wx_draw_fee, self.dt_id, 'ALI%'))

                    # 判断是否有商户低于渠道商成本
                    if sql_ali_draw.get('withdraw_fee') and immediately_update_info.get('alipay') > sql_ali_draw.get('withdraw_fee'):
                        query = """select mch_payment.mch_id from mch_payment
                            where mch_payment.withdraw_fee < %s and mch_payment.dt_id=%s and
                            mch_payment.payment_type in (7,8,9);"""
                        mch_ids = self.db.selectSQL(
                            query, (ali_draw_fee, self.dt_id), fetchone=False)
                        tuple_mch_ids = tuple([mch_id[0] for mch_id in mch_ids])
                        if mch_ids:
                            self.db.executeSQL("""
                              update mch_payment set withdraw_fee=%s where mch_id in %s
                              and payment_type in (7,8,9;""", (immediately_update_info.get('alipay'), tuple_mch_ids))

                if immediately_update_info.get('wx_draw_rate'):
                    update_sql = """update dt_payment set withdraw_rate=%s where dt_id=%s and uline_payment_code like %s"""
                    self.db.executeSQL(update_sql, (wx_draw_rate, self.dt_id, 'WX%'))

                    if sql_wx_draw.get('withdraw_rate') and immediately_update_info.get('wx_draw_rate') > sql_wx_draw.get('withdraw_rate'):
                        query = """select mch_payment.mch_id from mch_payment
                            where mch_payment.withdraw_rate < %s and mch_payment.dt_id=%s and
                            mch_payment.payment_type in (7,8,9);"""
                        mch_ids = self.db.selectSQL(
                            query, (wx_draw_rate, self.dt_id), fetchone=False)
                        tuple_mch_ids = tuple([mch_id[0] for mch_id in mch_ids])
                        if mch_ids:
                            self.db.executeSQL("""
                              update mch_payment set withdraw_rate=%s where mch_id in %s
                              and payment_type in (7,8,9);""", (wx_draw_rate, tuple_mch_ids))

                if immediately_update_info.get('ali_draw_rate'):
                    update_sql = """update dt_payment set withdraw_rate=%s where dt_id=%s and uline_payment_code like %s"""
                    self.db.executeSQL(update_sql, (ali_draw_rate, self.dt_id, 'ALI%'))

                    if sql_ali_draw.get('withdraw_rate') and immediately_update_info.get('ali_draw_rate') > sql_ali_draw.get('withdraw_rate'):
                        query = """select mch_payment.mch_id from mch_payment
                            where mch_payment.withdraw_rate < %s and mch_payment.dt_id=%s and
                            mch_payment.payment_type in (7,8,9);"""
                        mch_ids = self.db.selectSQL(
                            query, (ali_draw_rate, self.dt_id), fetchone=False)
                        tuple_mch_ids = tuple([mch_id[0] for mch_id in mch_ids])
                        if mch_ids:
                            self.db.executeSQL("""
                              update mch_payment set withdraw_rate=%s where mch_id in %s
                              and payment_type in (7,8,9);""", (ali_draw_rate, tuple_mch_ids))

        else:
            query = """insert into d0_withdraw_fee(role, role_type, wx, alipay) values(%s,%s,%s,%s)"""
            self.db.executeSQL(query, (self.dt_id, 'dt', wx_draw_fee, ali_draw_fee))

            # 保存到dt_paymnt表中(有空再优化，心情烦躁)
            if wx_draw_fee:
                update_sql = """update dt_payment set withdraw_fee=%s where dt_id=%s and uline_payment_code like %s"""
                self.db.executeSQL(update_sql, (wx_draw_fee, self.dt_id, 'WX%'))
            if ali_draw_fee:
                update_sql = """update dt_payment set withdraw_fee=%s where dt_id=%s and uline_payment_code like %s"""
                self.db.executeSQL(update_sql, (ali_draw_fee, self.dt_id, 'ALI%'))
            if wx_draw_rate:
                update_sql = """update dt_payment set withdraw_rate=%s where dt_id=%s and uline_payment_code like %s"""
                self.db.executeSQL(update_sql, (wx_draw_rate, self.dt_id, 'WX%'))
            if ali_draw_rate:
                update_sql = """update dt_payment set withdraw_rate=%s where dt_id=%s and uline_payment_code like %s"""
                self.db.executeSQL(update_sql, (ali_draw_rate, self.dt_id, 'ALI%'))

        if not self.open_daily_cut:
            sql = """update d0_withdraw_fee set {0}=%s where role_type='mch' and role in (
                        select mch_inlet_info.mch_id
                        from d0_withdraw_fee as df1 inner join mch_inlet_info on mch_inlet_info.mch_id = df1.role
                        where mch_inlet_info.dt_id=%s and df1.role_type='mch'
                        and df1.{0}<%s and df1.{0} NOTNULL
                     )"""
            ali_sql = sql.format('alipay')
            self.db.executeSQL(ali_sql, (ali_draw_fee, self.dt_id, ali_draw_fee))
            wx_sql = sql.format('wx')
            self.db.executeSQL(wx_sql, (wx_draw_fee, self.dt_id, wx_draw_fee))

    @gen.coroutine
    def auth_password(self, password):
        valid = False
        selSql = "select password from dt_user where dt_id=%s"
        db_ret = self.db.selectSQL(selSql, (self.dt_id,))
        if db_ret:
            valid = yield common.bcrypt_pwd(password, db_ret[0])
        raise gen.Return(valid)

    def update_dt_inlet_info(self, change_inlet_info):
        sql = """update dt_inlet_info set """
        update_colums = []
        params_values = []
        for key in change_inlet_info:
            update_colums.append("""{}=%s""".format(key))
            params_values.append(change_inlet_info[key])
        sql = sql + ','.join(update_colums)
        where_str = " where dt_id=%s;"
        sql = sql + where_str
        params_values.append(self.dt_id)
        self.db.executeSQL(sql, tuple(params_values))

        if 'dt_name' in change_inlet_info:
            sql = """UPDATE dt_user SET dt_name=%s WHERE dt_id=%s;"""
            self.db.executeSQL(sql, (change_inlet_info['dt_name'], self.dt_id))

    def update_dt_active_status(self):
        sql = """select count(*) as active_counts from dt_payment where activated_status=2 and dt_id=%s;"""
        result = self.db.selectSQL(sql, (self.dt_id,))
        activeed_counts = result[0]
        activated_status = 2 if activeed_counts >= 1 else 1
        sql = """update dt_inlet_info set activated_status=%s where dt_id = %s;"""
        self.db.executeSQL(sql, (activated_status, self.dt_id))

    @gen.coroutine
    def update_dt_payments(self, payments):
        payment_cut_info = dict()
        changed_payments = dict()
        if isinstance(payments, list):
            for each_payment in payments:
                changed_payments[each_payment[0]] = {'pay_type': each_payment[0],
                                                     'pay_rate': each_payment[1], 'pre_status': each_payment[2]}
        else:
            changed_payments = payments

        for pay_type in changed_payments:
            payment_info = changed_payments[pay_type]
            payment_type = payment_info['pay_type']
            payment_rate = payment_info['pay_rate']
            exist_status = payment_info['pre_status']
            action_type = payment_info.get('action_type', 2)

            # 将老的payment_type转换成uline_payment_code
            if payment_type.isdigit():
                # if isinstance(payment_type, int):
                uline_payment_code = old_payment_relations.get(payment_type)
            else:
                uline_payment_code = payment_type
                payment_type = new_payment_relations.get(uline_payment_code)

            # 如果是更新
            if action_type == 2:
                activated_status = 1
                dt_id = self.dt_id

                # 查询支付方式的原有费率，如果有且等于更新的费率，则需要还原为原有的激活状态
                sql = """select activated_status, payment_rate from dt_payment where dt_id=%s and payment_type=%s;"""
                result = self.db.selectSQL(sql, (self.dt_id, payment_type))
                if result:
                    exist_rate = result[1]
                    # 如果与原有的费率一致，且原有状态为未激活或已激活，则保持原有状态
                    if exist_rate and exist_rate == payment_rate and exist_status == 2:
                        activated_status = exist_status

                    if self.open_daily_cut:
                        payment_cut_info[int(payment_type)] = {
                            'pre_payment_rate': exist_rate,
                            'pre_payment_status': exist_status,
                            'update_payment_rate': payment_rate,
                            'payment_type': int(payment_type),
                            'action_type': action_type
                        }
                    else:
                        # 更新支付费率的信息
                        self.db.executeSQL("""
                                update dt_payment set payment_type=%s, payment_rate=%s, activated_status=%s, settle_rate=%s
                                 where dt_id=%s
                                  and payment_type=%s;
                            """, (payment_type, payment_rate, activated_status, payment_rate, dt_id, payment_type))

                        # 判断修改后的费率是否大于本来的费率
                        if payment_rate > exist_rate:
                            # 查询判断是否渠道商修改后的费率大于旗下商户
                            query = """select mch_payment.mch_id from mch_payment inner join mch_inlet_info on
                              mch_inlet_info.mch_id = mch_payment.mch_id inner join dt_payment on
                              mch_inlet_info.dt_id = dt_payment.dt_id and dt_payment.payment_type = mch_payment.payment_type
                              where mch_payment.payment_rate < %s and dt_payment.dt_id=%s and
                              dt_payment.payment_type=%s;"""
                            mch_ids = self.db.selectSQL(
                                query, (payment_rate, self.dt_id, payment_type), fetchone=False)
                            tuple_mch_ids = tuple([mch_id[0] for mch_id in mch_ids])
                            if mch_ids:
                                self.db.executeSQL("""
                                update mch_payment set payment_rate=%s, settle_rate=%s where mch_id in %s
                                  and payment_type=%s;""", (payment_rate, payment_rate, tuple_mch_ids, payment_type))

                            query = """select dp_lower.dt_id from dt_payment as dp_lower inner join dt_inlet_info on
                                    dt_inlet_info.dt_id=dp_lower.dt_id inner join dt_payment dp_higher on
                                    dt_inlet_info.parent_id=dp_higher.dt_id and dp_lower.payment_type=dp_higher.payment_type
                                    where dp_lower.payment_rate<%s and dp_higher.dt_id=%s and dp_higher.payment_type=%s"""
                            chain_ids = self.db.selectSQL(
                                query, (payment_rate, self.dt_id, payment_type), fetchone=False)
                            tuple_chain_ids = tuple([chain_id[0] for chain_id in chain_ids])
                            if tuple_chain_ids:
                                sql = """update dt_payment set payment_rate=%s, settle_rate=%s where dt_id in %s and
                                          payment_type=%s;"""
                                self.db.executeSQL(sql, (payment_rate, payment_rate,
                                                         tuple_chain_ids, payment_type))
            # 新增支付方式
            elif action_type == 1:
                # 添加
                tmp_str = translate_payment_type.get(payment_type)
                uline_payment_id, uline_settle_id, trade_type,\
                    thirdparty_mch_id, uline_payment_code = tmp_str.split('|')

                sql = """INSERT INTO dt_payment(dt_id, settle_rate, uline_payment_id, uline_payment_code,
                                                uline_settle_id, trade_type,
                                                payment_type, payment_rate, activated_status,
                                                create_at, update_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
                self.db.executeSQL(sql, (self.dt_id, payment_rate, uline_payment_id, uline_payment_code,
                                         uline_settle_id, trade_type,
                                         payment_type, payment_rate, 1, self.create_at, self.create_at))

                # sql = """INSERT INTO activated_dt_info
                #         (dt_id, payment_type, comment, activated_user, activated_status, create_at)
                #         values(%s, %s,%s, %s, %s, %s)"""
                # self.db.executeSQL(sql, (
                # self.dt_id, payment_type, constants.ACTIVATED_STATUS['2'],
                # self.bk_email, 2, self.create_at))

            # 删除支付方式
            elif action_type == 3:
                sql = """DELETE FROM dt_payment WHERE dt_id=%s and payment_type=%s;"""
                self.db.executeSQL(sql, (self.dt_id, payment_type))

                # 删除旗下商户、门店的支付方式
                query = """update mch_payment set activated_status=1 where payment_type=%s and mch_payment.mch_id in
                          (select mch_id from mch_inlet_info where dt_id=%s);"""
                self.db.executeSQL(query, (payment_type, self.dt_id))
                # 删除旗下连锁商户的支付方式
                query = """update dt_payment set activated_status=1 where payment_type=%s and dt_payment.dt_id in
                          (select dt_id from dt_inlet_info where parent_id=%s);"""
                self.db.executeSQL(query, (payment_type, self.dt_id))

        # 修改变更记录表里面的状态
        raise gen.Return(payment_cut_info)

    @gen.coroutine
    def get_dt_wx_reg_payment(self):
        query = """select id from dt_payment where dt_id=%s and payment_type in (1,2,3);"""
        ret = self.db.selectSQL(query, (self.dt_id,))
        raise gen.Return(ret)

    @gen.coroutine
    def get_dt_wx_app_payment(self):
        query = """select id from dt_payment where dt_id=%s and payment_type=4;"""
        ret = self.db.selectSQL(query, (self.dt_id,))
        raise gen.Return(ret)

    @gen.coroutine
    def update_dt_user(self):
        query = """
            update dt_user set
            status=%s,
            update_at=%s where dt_id=%s
        """
        self.db.executeSQL(query, (self.status, self.update_at, self.dt_id))

    @gen.coroutine
    def auth_dt_inlet(self):
        query = """update dt_inlet_info set
            auth_status=%s,
            update_at=%s where dt_id=%s"""
        self.db.executeSQL(query, (self.status, self.update_at, self.dt_id))

    @gen.coroutine
    def add_auth_inlet_info(self):
        auth_user = yield self.get_bk_email()
        query = """
            insert into auth_dt_info (
            dt_id,
            comment,
            auth_user,
            auth_status,
            create_at)
            values (%s, %s, %s, %s, %s);"""
        self.db.executeSQL(
            query,
            (
                self.dt_id,
                AUTH_STATUS[str(self.status)],
                auth_user,
                self.status,
                self.create_at
            )
        )

    @gen.coroutine
    def get_bk_email(self):
        # query = """select email from bk_user where bk_id=%s"""
        # ret = self.db.selectSQL(query, (self.current_user,))
        # raise gen.Return(ret[0])
        employee_id = self.session["employee_id"]
        employee = uline_session.query(Employee).filter(Employee.id == employee_id).one()
        user_profile = uline_session.query(UserProfile).filter(UserProfile.id == employee.user_id).one()
        email = user_profile.email
        raise gen.Return(email)

    @gen.coroutine
    def get_dt_user_wx_id(self):
        query = """select
                wx_sub_mch_id,
                wx_app_sub_mch_id
                from dt_user
                where dt_id=%s"""
        ret = self.db.selectSQL(query, (self.dt_id,))
        raise gen.Return(ret)

    @gen.coroutine
    def get_dt_inlet_info(self):
        query = """select
                dt_name,
                contact,
                mobile,
                email,
                old_ind_code,
                wx_ind_code,
                service_phone,
                wx_channel_id,
                wx_app_channel_id,
                parent_id
                from
                dt_inlet_info
                where dt_id=%s;"""
        ret = self.db.selectSQL(query, (self.dt_id,))
        raise gen.Return(ret)

    @gen.coroutine
    def get_dt_wx_config(self):
        query = """select rate from dt_user where dt_id=%s;"""
        ret = self.db.selectSQL(query, (self.dt_id,))
        if ret[0] == 1:
            raise gen.Return((WX_0_WX_MCH_ID, WX_0_WXPAY_KEY, WX_0_APPID))
        else:
            raise gen.Return((WX_MCH_ID, WXPAY_KEY, APPID))
        raise gen.Return(ret[0])

    @gen.coroutine
    def get_update_wx_sub_info(self):
        query = """
            select dt_inlet_info.dt_id,
            dt_inlet_info.mobile,
            dt_user.wx_sub_mch_id,
            dt_inlet_info.service_phone
            from
            dt_inlet_info
            inner join dt_user on dt_user.dt_id=dt_inlet_info.dt_id
            where dt_inlet_info.dt_id=%s;"""
        ret = self.db.selectSQL(query, (self.dt_id,))
        raise gen.Return(ret)

    @gen.coroutine
    def create_wx_sub_dt_id(self, dt_inlet_info, channel_id, APPID, WX_MCH_ID, WXPAY_KEY, WX_PRIVATE_KEY, WX_PUB_KEY,
                            WX_ROOT_CA):
        wx_business_no = dt_inlet_info[
            5] if dt_inlet_info[5] else dt_inlet_info[4]
        query_args = {
            "appid": APPID,
            "mch_id": WX_MCH_ID,
            "merchant_name": dt_inlet_info[0],
            "merchant_shortname": dt_inlet_info[0],
            "service_phone": dt_inlet_info[6] if dt_inlet_info[6] else dt_inlet_info[2],
            'contact': dt_inlet_info[1],
            "contact_phone": dt_inlet_info[2],
            "contact_email": dt_inlet_info[3],
            "business": wx_business_no,
            "merchant_remark": self.dt_id,
            'channel_id': channel_id
        }
        result = yield create_wx_mch(query_args, WXPAY_KEY, WX_PRIVATE_KEY, WX_PUB_KEY, WX_ROOT_CA)
        if not result:
            result = dict(result_code='FAIL')
        raise gen.Return(result)

    @gen.coroutine
    def update_wx_sub_dt_id(
            self, dt_inlet_info, APPID, WX_MCH_ID, WXPAY_KEY,
            WX_PRIVATE_KEY, WX_PUB_KEY, WX_ROOT_CA):
        mchInletToWx = UpdateMerchantInletToWx(APPID, WX_MCH_ID, WXPAY_KEY)

        merchant_shorname = u'{}微信支付商户'.format(BANK_NAME)
        service_phone = dt_inlet_info[3] if dt_inlet_info[3] else dt_inlet_info[1]
        data = mchInletToWx.handle()(
            merchant_shortname=merchant_shorname,
            service_phone=service_phone,
            sub_mch_id=dt_inlet_info[2],
        )

        is_success = True
        # 当从微信获取的商户信息不同现有信息时，才进行修改
        if self.merchant_info_in_wx and ((self.merchant_info_in_wx['merchant_shortname'] != merchant_shorname) or (
                self.merchant_info_in_wx['service_phone'] != service_phone)):
            http_client = AsyncHTTPClient()
            response = yield http_client.fetch(
                "https://api.mch.weixin.qq.com/secapi/mch/submchmanage?action=modify",
                method='POST', body=data,
                client_key=WX_PRIVATE_KEY,
                client_cert=WX_PUB_KEY, ca_certs=WX_ROOT_CA
            )
            ret = xml_to_dict(response.body).get('root')
            log.detail.info(response.body)
            is_success = (ret.get('return_code', '') ==
                          'SUCCESS') if ret else False
            raise gen.Return(is_success)
        elif not self.merchant_info_in_wx:
            # 如果没有从微信获取有效信息 ，应该不会发生
            log.exception.info('update_wx_sub_dt_id no merchant_info from wx')
            raise gen.Return(False)
        else:
            # 如果有信息且与现有的有效
            raise gen.Return(True)

    @gen.coroutine
    def add_wx_sub_dt_id(self):
        query = """update dt_user set wx_sub_mch_id=%s,
        update_at=%s where dt_id=%s"""
        self.db.executeSQL(
            query, (self.wx_sub_dt_id, self.update_at, self.dt_id))

    @gen.coroutine
    def add_wx_app_sub_dt_id(self):
        query = """update dt_user set wx_app_sub_mch_id=%s,
            update_at=%s where dt_id=%s"""
        self.db.executeSQL(query, (self.wx_app_sub_dt_id,
                                   self.update_at, self.dt_id))

    @gen.coroutine
    def save_dt_inlet_to_wx(self, ret):
        query = """
            insert into dt_inlet_to_wx_info (
            dt_id, return_code, return_msg,
            result_code, result_msg, create_at
            ) values (%s, %s, %s, %s, %s, %s);"""
        self.db.executeSQL(
            query,
            (
                self.dt_id,
                ret.get('result_code', 'FAIL'),
                ret.get('return_msg', 'FAIL'),
                ret.get('result_code', 'FAIL'),
                ret.get('result_msg', 'FAIL'),
                self.create_at
            )
        )

    @gen.coroutine
    def update_app_info2wx(self):
        """更新app商户信息到微信
        :return:
            更新到微信，微信返回的结果，一个dict
        """
        # 获取更新相关信息
        dt_inlet_info = yield self.get_update_wx_app_sub_info()
        service_phone = dt_inlet_info[3] if dt_inlet_info[3] else dt_inlet_info[1]

        merchant_name = dt_inlet_info[4]
        merchant_shorname = u'{}微信支付商户'.format(BANK_NAME)
        search_info = {
            'merchant_name': merchant_name,
            'sub_mch_id': dt_inlet_info[2]
        }
        self.app_merchant_info_in_wx = yield self.get_mch_info_from_wx(search_info, WX_APP_APPID, WX_APP_MCH_ID,
                                                                       WXPAY_APP_KEY, WX_APP_PRIVATE_KEY,
                                                                       WX_APP_PUB_KEY, WX_ROOT_CA)

        is_success = True
        # 同步至微信
        # 当从微信获取的商户信息不同现有信息时，才进行修改
        if self.app_merchant_info_in_wx and (
            (self.app_merchant_info_in_wx['merchant_shortname'] != merchant_shorname) or (
                self.app_merchant_info_in_wx['service_phone'] != service_phone)):
            updateinfo = {
                'short_name': merchant_shorname,
                'service_phone': service_phone,
                'wx_mch_id': dt_inlet_info[2]
            }
            result = yield self.update_mch_info2wx(updateinfo, WX_APP_APPID, WX_APP_MCH_ID, WXPAY_APP_KEY,
                                                   WX_APP_PRIVATE_KEY, WX_APP_PUB_KEY, WX_ROOT_CA)

            log.exception.info('update wx app mch info result:{}'.format(
                json.dumps(result, ensure_ascii=False)))
            is_success = result.get(
                'return_code', '') == 'SUCCESS' if result else False
            if not is_success:
                log.exception.info('update wx app mch failed,result_code : {}'.format(
                    result.get('return_code', '')))
        elif not self.app_merchant_info_in_wx:
            # 微信中没有商户信息，添加日志，修改失败
            log.exception.info('update_app_info2wx no merchant info from wx, app_sub_id:{0}, merchant name:{1}'.format(
                dt_inlet_info[2], merchant_shorname))
            is_success = False
        else:
            # 没有变化，表示修改成功
            is_success = True
        raise gen.Return(is_success)

    @gen.coroutine
    def get_update_wx_app_sub_info(self):
        query = """
                select dt_inlet_info.dt_id,
                dt_inlet_info.mobile,
                dt_user.wx_app_sub_mch_id,
                dt_inlet_info.service_phone,
                dt_inlet_info.dt_name
                from  dt_inlet_info
                inner join dt_user on dt_user.dt_id=dt_inlet_info.dt_id
                where dt_inlet_info.dt_id=%s;"""
        ret = self.db.selectSQL(query, (self.dt_id,))
        raise gen.Return(ret)

    @gen.coroutine
    def add_fail_auth_inlet_info(self, show_comment):
        auth_user = yield self.get_bk_email()
        query = """
            insert into auth_dt_info (
            dt_id,
            comment,
            auth_user,
            auth_status,
            create_at)
            values (%s, %s, %s, %s, %s);"""
        self.db.executeSQL(
            query,
            (
                self.dt_id,
                show_comment,
                auth_user,
                self.status,
                self.create_at
            )
        )

    def latest_status(self, cursor):
        query = """
            SELECT auth_status, auth_user
            from auth_dt_info where dt_id = %s
             order by create_at desc
             LIMIT 1;"""
        cursor.execute(query, (self.dt_id,))
        ret = cursor.fetchone()
        return ret

    def auth_user_email(self, bk_id):
        selSql = """select email from bk_user where bk_id=%s"""
        db_ret = self.db.selectSQL(selSql, (bk_id,))
        if db_ret:
            return db_ret[0]

    def get_chain_parent_info(self, parent_id):
        query = """SELECT wx_channel_id, wx_app_channel_id FROM dt_inlet_info where dt_id=%s"""
        result = self.db.selectSQL(query, (parent_id,))
        return result

    def has_authed(self):
        sql = """select * from auth_dt_info where dt_id=%s and auth_status=2"""
        result = self.db.selectSQL(sql, (self.dt_id,), fetchone=True)
        return bool(result)

    def add_daily_cut_record(self, cut_record):
        sql = """insert into daily_cut_record(role_id, role_type, record_json, status) values(%s,%s,%s,1)"""
        self.db.executeSQL(sql, (self.dt_id, 'dt', json.dumps(cut_record)))

    def activated_all_payment(self):
        sql = """select payment_type from dt_payment where dt_id=%s"""
        payments_db = self.db.selectSQL(sql, (self.dt_id,), use_dict=True, fetchone=False)
        for payment in payments_db:
            payment_type = payment['payment_type']
            update_sql = """update dt_payment set activated_status=2 where dt_id=%s and payment_type=%s"""
            self.db.executeSQL(update_sql, (self.dt_id, payment_type))

            sql = """INSERT INTO activated_dt_info (dt_id, payment_type, comment, activated_user, activated_status, create_at)
                                     values(%s, %s,%s, %s, %s, %s)"""
            self.db.executeSQL(sql, (
                self.dt_id, payment_type, constants.ACTIVATED_STATUS['2'], self.bk_email, 2, self.create_at))

    def invalid_past_record(self):
        sql = """update daily_cut_record set status=%s,update_at=%s where role_id=%s and role_type=%s and status=1"""
        self.db.executeSQL(sql, (4, self.create_at, self.dt_id, 'dt'))
        sql = """update change_record set status=%s,update_at=%s where dt_id=%s and status=4"""
        self.db.executeSQL(sql, (5, self.create_at, self.dt_id))
