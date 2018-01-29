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
from uline.public import common
from uline.public import log, constants
from uline.public.constants import AUTH_STATUS
from uline.settings import FEATURE_SWITCH
from uline.settings import (
    WX_MCH_ID, WXPAY_KEY, APPID, WX_PUB_KEY, WX_PRIVATE_KEY, WX_ROOT_CA,
    WX_APP_MCH_ID, WXPAY_APP_KEY, WX_APP_APPID, WX_APP_PUB_KEY,
    WX_APP_PRIVATE_KEY, WX_APP_ROOT_CA,
    WX_0_WX_MCH_ID, WX_0_WXPAY_KEY, WX_0_APPID, ALI_PID, MIN_ALI_LEVEL
)
from uline.utils.alipay.get_code_by_name import query_code_by_name
from uline.utils.alipay.query_alipay import create_alipay_mch_common
from uline.utils.alipay.query_alipay import create_alipay_mch_common_m1, create_alipay_mch_common_m3
from uline.utils.record import record_utils
from uline.utils.wxpay.merchantInletToWxV2 import UpdateMerchantInletToWx
from uline.utils.wxpay.query_wx import create_wx_mch
from uline.utils.wxpay.util import xml_to_dict, deal_with_wx_result
from .form import AuthDistributorInfo
from uline.public.permit import check_permission
from uline.model.uline.user import Employee
from uline.model.uline.info import UserProfile
from uline.model.uline.base import uline_session


class AuthChainInletStatusHandler(IntBkAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        print 'chain auth'
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
                    self.add_auth_inlet_info(cur)
                    self.auth_dt_inlet(cur)
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

    @asynchronous
    @gen.coroutine
    def get(self):
        # http_client = AsyncHTTPClient()
        # url = AUTH_URL + '/v1/chainauth'
        # data = {'chain_id': self.dt_id, 'bk_id': self.current_user}
        # response = yield http_client.fetch(url, body=json.dumps(data), method='POST')
        # if response.body == '1':
        #     # fail
        #     self.rsp = common.f_rsp(code=406, msg='fail')
        # else:
        #     # success
        #     self.rsp = common.scc_rsp(code=200, msg='inleting')
        # self.write(self.rsp)
        # self.finish()
        # return
        # print self.get_arguments()
        wx_reg_flag, wx_app_flag, ali_flag = True, True, True
        self.wx_sub_dt_id = None
        self.wx_app_sub_dt_id = None
        self.ali_sub_mch_id = None
        with self.db.get_db(use_dict=True) as cur:
            try:
                wx_reg_pay = self.get_dt_wx_reg_payment(cur)
                wx_app_pay = self.get_dt_wx_app_payment(cur)
                ali_pays = self.get_dt_ali_payment(cur)
                wx_id = self.get_dt_user_wx_id(cur)

                db_payments = self.get_all_db_payments(cur)
                db_payments_paytypes = list()
                for each_payment in db_payments:
                    db_payments_paytypes.append(each_payment[0])

                dt_inlet_info = self.get_dt_inlet_info(cur)
                alipay_category_id = dt_inlet_info[11]
                self.dt_inlet_info = dt_inlet_info
                # 由于微信端渠道商进件有调整，不对其进行api进件，但保留原始信息
                wx_reg, wx_app = "success", "success"
                # 是否是新添加的微信子商户
                self.new_wx_sub_dt_id = False
                self.new_wx_app_sub_dt_id = False
                self.new_ali_id = False

                self.change_record = self.get_change_record(cur)
                self.changed_dt_name = self.change_record.get('dt_name', dt_inlet_info[0])
                self.changed_dt_shortname = self.change_record.get('dt_short_name', dt_inlet_info[10])
                self.changed_service_phone = self.change_record.get('service_phone', dt_inlet_info[6])
                self.changed_contact = self.change_record.get('contact', dt_inlet_info[1])
                self.changed_mobile = self.change_record.get('mobile', dt_inlet_info[2])
                self.changed_email = self.change_record.get('email', dt_inlet_info[3])
                self.changed_license_type = self.change_record.get("license_type", dt_inlet_info['license_type'])
                self.changed_head_name = self.change_record.get("head_name", dt_inlet_info['head_name'])
                self.changed_head_mobile = self.change_record.get("head_mobile", dt_inlet_info['head_mobile'])
                self.changed_license_num = self.change_record.get("license_num", dt_inlet_info['license_num'])
                self.changed_head_type = self.change_record.get('head_type', dt_inlet_info['head_type'])

                balance_info = self.get_balance_info(cur)
                change_balance_info = self.change_record.get("balance_info", {})
                self.changed_id_card_no = change_balance_info.get("id_card_no", balance_info['id_card_no'])
                self.changed_balance_account = change_balance_info.get(
                    'balance_account', balance_info['balance_account'])
                self.changed_balance_name = change_balance_info.get("balance_name", balance_info['balance_name'])

                changed_payments = self.change_record.get('payment', {})
                for payment_type in changed_payments:
                    payment = changed_payments[payment_type]
                    payment_type = int(payment.get('pay_type', 0))
                    action_type = payment.get('action_type', 2)
                    if action_type == 1:
                        db_payments_paytypes.append(payment_type)
                    elif action_type == 2 and payment_type not in db_payments_paytypes:
                        db_payments_paytypes.append(payment_type)
                    elif action_type == 3:
                        db_payments_paytypes.remove(payment_type)

                for payment_type in db_payments_paytypes:
                    if payment_type in constants.OFFLINE_D1_WX_PAY_TYPES + constants.OFFLINE_D0_WX_PAY_TYPES:
                        wx_reg_pay = True
                    if payment_type in constants.ONLINE_D1_WX_PAY_TYPES + constants.ONLINE_D0_WX_PAY_TYPES:
                        wx_app_pay = True
                    if payment_type in constants.D1_ALI_PAY_TYPES + constants.D0_ALI_PAY_TYPES:
                        ali_pays = True

                # 如果是连锁商户， 进件到微信、支付宝
                if dt_inlet_info and dt_inlet_info[9]:
                    parent_info = self.get_chain_parent_info(cur, dt_inlet_info[9])
                    wx_channel_id = parent_info[0]
                    wx_app_channel_id = parent_info[1]
                    # 如果连锁商户的上级渠道商有微信商户号且该商户有普通微信支付
                    if wx_channel_id and wx_reg_pay:
                        wx_mch_id, wxpay_key, appid = self.get_dt_wx_config(cur)
                        wx_sub_id = wx_id[0]
                        self.wx_sub_dt_id = wx_sub_id
                        if not wx_sub_id:
                            # 有扫码支付等信息且没有对应的数据，则新进件到微信
                            log.exception.info('start chain create wx reg')
                            ret = yield self.create_wx_sub_dt_id(
                                dt_inlet_info, wx_channel_id, appid, wx_mch_id, wxpay_key,
                                WX_PRIVATE_KEY, WX_PUB_KEY, WX_ROOT_CA
                            )
                            self.save_dt_inlet_to_wx(cur, ret)
                            default_err_msg = '进件到微信支付出现未知错误,请联系客服!'
                            self.wx_sub_dt_id, wx_reg = deal_with_wx_result(
                                ret, 'sub_mch_id', default_err_msg)
                            log.exception.info(
                                'create chain wx reg info,result:{}, msg:{}'.format(self.wx_sub_dt_id, wx_reg))
                            if not self.wx_sub_dt_id:
                                wx_reg_flag = False
                            else:
                                self.add_wx_sub_dt_id(cur)
                                self.new_wx_sub_dt_id = True
                        else:
                            wx_reg_flag = True
                            # 修改渠道商微信信息(扫码支付／刷卡支付／公众账号支付)
                            inlet_info = self.get_update_wx_sub_info(cur)
                            # 获取微信端的商户信息
                            search_info = {'sub_mch_id': wx_sub_id}
                            wx_mch_id, wxpay_key, appid = self.get_dt_wx_config(cur)
                            # 从微信获取微信现有的商户信息
                            self.merchant_info_in_wx = yield self.get_mch_info_from_wx(search_info, appid, wx_mch_id,
                                                                                       wxpay_key,
                                                                                       WX_PRIVATE_KEY, WX_PUB_KEY,
                                                                                       WX_ROOT_CA)

                            update_result, wx_reg = yield self.update_wx_sub_dt_id(cur,
                                                                                   inlet_info, appid, wx_mch_id,
                                                                                   wxpay_key,
                                                                                   WX_PRIVATE_KEY, WX_PUB_KEY,
                                                                                   WX_ROOT_CA
                                                                                   )
                            log.exception.info(
                                'update chain wx reg,result:{},msg:{}'.format(update_result, wx_reg))
                            if not update_result:
                                wx_reg_flag = False
                            self.wx_sub_dt_id = inlet_info[2]

                    wx_app_sub_dt_id = wx_id[1]
                    self.wx_app_sub_dt_id = wx_app_sub_dt_id
                    if wx_app_pay and not wx_app_sub_dt_id and wx_app_channel_id:
                        # 有app支付方式且没有对应的微信商户sub_mch_id,则进件到微信
                        log.exception.info('start chain create wx app')
                        ret = yield self.create_wx_sub_dt_id(
                            dt_inlet_info, wx_app_channel_id, WX_APP_APPID, WX_APP_MCH_ID, WXPAY_APP_KEY,
                            WX_APP_PRIVATE_KEY, WX_APP_PUB_KEY, WX_APP_ROOT_CA)
                        self.save_dt_inlet_to_wx(cur, ret)
                        default_err_msg = '进件到微信APP支付发生未知错误,请联系客服!'
                        self.wx_app_sub_dt_id, wx_app = deal_with_wx_result(
                            ret, 'sub_mch_id', default_err_msg)
                        log.exception.info(
                            'create chain wx app info,result:{}, msg:{}'.format(self.wx_app_sub_dt_id, wx_app))
                        if not self.wx_app_sub_dt_id:
                            log.exception.info('create wx app mch failed,no wx_app_sub_dt_id')
                            wx_app_flag = False
                        else:
                            self.add_wx_app_sub_dt_id(cur)
                            self.new_wx_app_sub_dt_id = True
                    # 渠道商不在进件到微信
                    elif wx_app_channel_id and wx_app_pay and wx_app_sub_dt_id:
                        # 修改渠道商信息 app 支付(有使用app支付且app支付的wx_app_sub_dt_id不为空
                        wx_app_flag, wx_app = yield self.update_app_info2wx(cur)
                        log.exception.info('update chain wx app,result:{},msg:{}'.format(wx_app_flag, wx_app))

                ali_id = wx_id[2]
                self.ali_sub_mch_id = ali_id

                alipay_pid = parent_info[2]
                if not alipay_pid:
                    alipay_pid = ALI_PID

                ali_flag, msg_ali = yield self.mch_inlet_to_ali_reg(cur, ali_flag, ali_pays, ali_id, dt_inlet_info,
                                                                    alipay_category_id, alipay_pid)
                if not wx_reg_flag or not wx_app_flag or not ali_flag:
                    log.exception.info('进件到微信失败 wx_reg_flag:{}, wx_app_flag:{}, ali_flag'.format(
                        wx_reg_flag, wx_app_flag, ali_flag))

                    comment_news = [wx_reg, wx_app, msg_ali]
                    field = ["微信支付进件:{}", "微信APP支付进件:{}", "支付宝进件:{}"]
                    show_comment = "  ".join(_f.format(_com)
                                             for _f, _com in zip(field, comment_news) if _com != "success")

                    self.status = 3
                    self.add_fail_auth_inlet_info(cur, show_comment)
                    yield record_utils.rollback(self)

                    self.auth_dt_inlet(cur)
                    self.rsp = common.f_rsp(code=407, msg=show_comment)
                else:
                    self.update_dt_user(cur)
                    self.auth_dt_inlet(cur)
                    self.add_auth_inlet_info(cur)
                    yield self.update_changes(cur)

                    self.update_cs_wx_sub_id(cur)

                self.update_dt_active_status(cur)
            except Exception as err:
                import traceback
                log.exception.info(traceback.format_exc())
                cur.connection.rollback()
                self.rsp = common.f_rsp(code=406, msg='fail')
            else:
                try:
                    cur.connection.commit()
                except Exception as err:
                    log.exception.info(err)
                    cur.connection.rollback()
        self.write(self.rsp)
        self.finish()

    @gen.coroutine
    def mch_inlet_to_ali_reg(
        self, cur, ali_flag, mch_ali_payment, ali_id, dt_inlet_info, alipay_category_id, alipay_pid
    ):
        msg_ali = "success"
        if mch_ali_payment and alipay_pid:
            ret = yield self.create_alipay_sub_mch_id(dt_inlet_info, alipay_pid, update=False)
            self.save_inlet_to_ali(cur, ret)
            self.ali_sub_mch_id = ret.get('sub_merchant_id') if ret.get('code') in ['10000', 10000] else ''
            if not self.ali_sub_mch_id:
                ali_flag = False
                msg_ali = ret.get('sub_msg', '进件到支付宝发生未知错误,请联系客服!')
            else:
                self.add_ali_sub_mch_id(cur)
                self.new_ali_id = True
        ali_reg = [ali_flag, msg_ali]
        raise gen.Return(ali_reg)

    def save_inlet_to_ali(self, cursor, ret):
        query = """insert into
                          dt_inlet_to_wx_info (
                          dt_id, return_code, return_msg,
                          result_code, result_msg, create_at)
                          values (%s, %s, %s, %s, %s, %s);"""
        cursor.execute(
            query,
            (
                self.dt_id,
                ret.get('code', 'FAIL'),
                ret.get('msg', 'FAIL'),
                ret.get('sub_code', 'FAIL'),
                ret.get('sub_msg', 'FAIL'),
                self.create_at
            )
        )

    @gen.coroutine
    def create_alipay_sub_mch_id(self, dt_inlet_info, alipay_pid, update=False):
        # dt_inlet_info = [dt_name, contact, mobile, email, old_ind_code, wx_ind_code, service_phone, wx_channel_id,
        # wx_app_channel_id, parent_id, dt_short_name, ali_ind_code, address,
        # province, city, district]

        query_dict = {
            'external_id': self.dt_id,
            'name': self.changed_dt_name,
            'alias_name': self.changed_dt_shortname,
            'service_phone': self.changed_service_phone or self.changed_mobile,
            'category_id': dt_inlet_info['ali_ind_code'],
            'source': alipay_pid
        }

        level = 'M1'
        if dt_inlet_info['district']:
            province_code, city_code, district_code = query_code_by_name(
                dt_inlet_info['province'],
                dt_inlet_info['city'],
                dt_inlet_info['district'])

            # 如果有填区域信息，则以M2等级进件
            if province_code and city_code and district_code:
                query_dict['address_info'] = [{
                    'province_code': province_code,
                    'city_code': city_code,
                    'district_code': district_code,
                    'address': dt_inlet_info['address'],
                    'type': 'BUSINESS_ADDRESS'
                }]
                level = 'M2'
        if MIN_ALI_LEVEL.upper() >= "M3":
            level = 'M3'
            check_key = {
                'license_num': '营业执照编号',
                'license_type': '营业执照类型',
                'id_card_no': "身份证号码",
                'head_name': "负责人姓名",
                'head_mobile': '负责人电话号码',
                'email': '邮箱',
                'balance_account': "银行卡号",
                'balance_name': "持卡人名称",
                'head_type': '负责人类型',
            }
            error_msg = []
            for key in check_key:
                if not getattr(self, 'changed_{}'.format(key), None):
                    error_msg.append("{}信息为空".format(check_key[key]))
            if error_msg:
                raise gen.Return({'code': 11111111, 'sub_msg': ",".join(error_msg)})

            m3_infos = {
                'business_license': self.changed_license_num,
                'business_license_type': self.changed_license_type,
                'contact_info': [{
                    "name": self.changed_head_name,
                    "type": self.changed_head_type or 'OTHER',  # ;:法人，CONTROLLER:控制人, AGENT:代理人，OTHER：其他，
                    "id_card_no": self.changed_id_card_no,
                    "mobile": self.changed_head_mobile,
                    # "phone": 座机,
                    "email": self.changed_email,
                }],
                'bankcard_info': [{
                    "card_no": self.changed_balance_account,
                    "card_name": self.changed_balance_name,
                }],

            }
            query_dict.update(m3_infos)

        level_method_map = {
            'M1': create_alipay_mch_common_m1,
            'M2': create_alipay_mch_common,
            'M3': create_alipay_mch_common_m3
        }
        level_method = level_method_map.get(level)
        if level_method:
            ali_ret = yield level_method(query_dict)
        else:
            ali_ret = {}

        raise gen.Return(ali_ret)

    def add_ali_sub_mch_id(self, cursor):
        query = """update dt_user set ali_sub_mch_id=%s,update_at=%s where dt_id=%s"""
        cursor.execute(query, (self.ali_sub_mch_id,
                               self.update_at, self.dt_id))

    @gen.coroutine
    def update_changes(self, cur):
        # 检查这个商户是否有变更金额
        query_change_record = self.change_record
        employee = uline_session.query(Employee).filter(Employee.login_name == str(self.dt_id) + ".mr").one()
        if self.status in [2, "2"]:
            uline_session.query(Employee).filter(Employee.id == employee.id).update({'status': 1})
            uline_session.query(UserProfile).filter(UserProfile.id == employee.user_id).update({'status': 1})
            uline_session.commit()
        # 验证数据的合法性
        if query_change_record:
            if 'payment' in query_change_record:
                payments = query_change_record['payment']
                self.update_dt_payments(cur, payments)

            if 'role' in query_change_record:
                role = query_change_record['role']
                self.apply_d0_withdraw_fee(cur, role)
                # 账户信息修改
            if 'balance_info' in query_change_record:
                balance_update_info = query_change_record['balance_info']
                update_keys = ['balance_type', 'balance_name', 'bank_no', 'balance_account',
                               'id_card_no']
                change_balance_info = {key: balance_update_info[key] for key in update_keys if
                                       key in balance_update_info}
                change_balance_info['update_at'] = self.update_at
                self.update_balance_info(cur, change_balance_info)

            need_update_keys = ['dt_name', 'province', 'city', 'address', 'contact', 'mobile', 'service_phone', 'email',
                                'id_card_img_f', 'id_card_img_b', 'dt_id', 'license_num',
                                'license_start_date', 'license_end_date', 'license_period', 'license_scope',
                                'license_img', 'wx_channel_id', 'wx_app_channel_id', 'dt_type', 'u_ind_code',
                                'wx_ind_code', 'ali_ind_code', 'dt_short_name', "dt_sub_id"]
            change_inlet_info = {key: query_change_record[key] for key in need_update_keys if
                                 key in query_change_record}

            # 判断联系电话是否修改
            new_mobile = query_change_record.get('mobile')
            if new_mobile:
                # _password = common.bcrypt_pwd_new(str(self.get_dt_user_mobile()))
                result = yield self.auth_password(cur, str(self.get_dt_user_mobile(cur)))
                # 如果reesult为True,说明该渠道商还未登录，mobile已经被修改了
                if result:
                    # 将密码修改为新的联系电话
                    new_password = common.bcrypt_pwd_new(str(new_mobile))
                    _query = """update dt_user set password=%s where dt_id=%s;"""
                    cur.execute(_query, (new_password, self.dt_id))
                    uline_session.query(Employee).filter(Employee.login_name == str(self.dt_id) + ".dt").update(
                        {'login_passwd': new_password})
            if change_inlet_info:
                self.update_dt_user_email(cur, change_inlet_info)
                self.update_dt_inlet_info(cur, change_inlet_info)

            query = """update change_record set status = %s, create_at = now() where dt_id = %s and status=1;"""
            cur.execute(query, (2, self.dt_id,))
            _employee = {"email": "email", "mobile": "phone1", "city": "city", "dt_name": "name"}
            employee_update = {_employee[i]: change_inlet_info[i] for i in _employee.keys() if change_inlet_info.get(i)}
            if employee_update:
                uline_session.query(UserProfile).filter(UserProfile.id == employee.user_id).update(employee_update)
                uline_session.commit()

    def get_change_record(self, cur):
        query_change_record = dict()
        sql = """select data_json from change_record where status=1 and dt_id = %s;"""
        cur.execute(sql, (self.dt_id,))
        query_change_record_json = cur.fetchone()
        if query_change_record_json:
            query_change_record = json.loads(query_change_record_json[0])
        return query_change_record

    def get_balance_info(self, cur):
        query_balance_info = {}
        sql = """select balance_name, balance_account, id_card_no from dt_balance where dt_id=%s;"""
        cur.execute(sql, (self.dt_id,))
        query_balance_info = cur.fetchone()
        return query_balance_info or {}

    def update_balance_info(self, cur, change_balance_info):
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
        cur.execute(sql, tuple(params_values))

    def get_dt_user_mobile(self, cur):
        sql = "select mobile from dt_inlet_info where dt_id=%s"

        cur.execute(sql, (self.dt_id,))
        ret = cur.fetchone()
        return ret[0]

    def update_dt_user_email(self, cur, change_info):
        change_keys = ['email', 'dt_name']
        set_params = {key: change_info[key] for key in change_info if key in change_keys}
        if set_params:
            set_clauses = list()
            params = list()
            for each_key in set_params:
                set_clauses.append('{}=%s'.format(each_key))
                params.append(set_params[each_key])

            sql = "update dt_user set {} where dt_id = %s".format(','.join(set_clauses))
            params.append(self.dt_id)
            cur.execute(sql, tuple(params))

    def apply_d0_withdraw_fee(self, cur, role):
        wx = role.get('wx')
        alipay = role.get('alipay')

        select_query = """select 1 from d0_withdraw_fee where role=%s and role_type='dt' """

        cur.execute(select_query, (self.dt_id,))
        ret = cur.fetchone()
        # 如果没有ret是None
        if ret:
            query = """update d0_withdraw_fee set wx=%s, alipay=%s where role=%s and role_type = %s"""
            cur.execute(query, (wx, alipay, self.dt_id, 'dt'))
        else:
            query = """insert into d0_withdraw_fee(role, role_type, wx, alipay) values(%s,%s,%s,%s)"""
            cur.execute(query, (self.dt_id, 'dt', wx, alipay))

        select_mch = """
            select dwf.wx, dwf.alipay, mii.mch_id from d0_withdraw_fee as dwf
            inner join mch_inlet_info as mii on mii.mch_id = dwf.role
            where mii.dt_id = %s and dwf.role_type='mch'
            and (dwf.wx < %s or dwf.alipay < %s)
        """
        cur.execute(select_mch, (self.dt_id, wx, alipay))
        ret_mchs = cur.fetchall()
        if ret_mchs:
            for ret_mch in ret_mchs:
                mch_wx = ret_mch[0]
                mch_alipay = ret_mch[1]
                mch_id = ret_mch[2]

                # mch_wx 可能是 None 小于任何自然数，所以要用大于
                mch_wx = mch_wx if mch_wx > wx else wx
                mch_alipay = mch_alipay if mch_alipay > alipay else alipay

                cur.execute("""
                    update d0_withdraw_fee set wx=%s, alipay=%s where role=%s and role_type = 'mch'
                """, (mch_wx, mch_alipay, mch_id))

    @gen.coroutine
    def auth_password(self, cur, password):
        valid = False
        selSql = "select password from dt_user where dt_id=%s"
        cur.execute(selSql, (self.dt_id,))
        db_ret = cur.fetchone()
        if db_ret:
            valid = yield common.bcrypt_pwd(password, db_ret[0])
        raise gen.Return(valid)

    def update_dt_inlet_info(self, cur, change_inlet_info):
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
        cur.execute(sql, tuple(params_values))

    def update_dt_active_status(self, cur):
        sql = """select count(*) as active_counts from dt_payment where activated_status=2 and dt_id=%s;"""
        cur.execute(sql, (self.dt_id,))
        result = cur.fetchone()
        activeed_counts = result[0]
        activated_status = 2 if activeed_counts >= 1 else 1
        sql = """update dt_inlet_info set activated_status=%s where dt_id = %s;"""
        cur.execute(sql, (activated_status, self.dt_id))

    def update_dt_payments(self, cur, payments):
        changed_payments = dict()
        if isinstance(payments, list):
            for each_payment in payments:
                changed_payments[each_payment[0]] = {'pay_type': each_payment[0],
                                                     'pay_rate': each_payment[1], 'pre_status': each_payment[2]}
        else:
            changed_payments = payments

        sub_mch_ids = list()
        for pay_type in changed_payments:
            payment_info = changed_payments[pay_type]
            payment_type = payment_info['pay_type']
            payment_rate = payment_info['pay_rate']
            exist_status = payment_info['pre_status']
            is_exist = payment_info.get('is_exist', 1)
            action_type = payment_info.get('action_type', 2)
            if action_type == 2:
                activated_status = 1
                dt_id = self.dt_id

                # 查询支付方式的原有费率，如果有且等于更新的费率，则需要还原为原有的激活状态
                sql = """select activated_status, payment_rate
                                                from dt_payment where dt_id=%s and payment_type=%s;"""
                cur.execute(sql, (self.dt_id, payment_type))
                result = cur.fetchone()
                if result:
                    exist_rate = result[1]
                    # 如果与原有的费率一致，且原有状态为未激活或已激活，则保持原有状态
                    if exist_rate and exist_rate == payment_rate and exist_status == 2:
                        activated_status = exist_status

                    # 更新支付费率的信息
                    cur.execute("""
                            update dt_payment set payment_type=%s, payment_rate=%s, activated_status=%s
                             where dt_id=%s
                              and payment_type=%s;
                        """, (payment_type, payment_rate, activated_status, dt_id, payment_type))

                    # 判断修改后的费率是否大于本来的费率
                    if payment_rate != exist_rate:
                        # 查询不为现有费率的连锁门店
                        query = """select mch_payment.mch_id from mch_payment inner join mch_inlet_info on
                          mch_inlet_info.mch_id = mch_payment.mch_id inner join dt_payment on
                          mch_inlet_info.cs_id = dt_payment.dt_id and dt_payment.payment_type = mch_payment.payment_type
                          where mch_payment.payment_rate != %s and dt_payment.dt_id=%s and
                          dt_payment.payment_type=%s;"""
                        cur.execute(
                            query, (payment_rate, self.dt_id, payment_type))
                        mch_ids = cur.fetchall()
                        tuple_mch_ids = tuple([mch_id[0] for mch_id in mch_ids])
                        if mch_ids:
                            cur.execute("""update mch_payment set payment_rate=%s where mch_id in %s
                              and payment_type=%s;""", (payment_rate, tuple_mch_ids, payment_type))
            elif action_type == 1:
                query = """insert into dt_payment
                            (dt_id, payment_type, payment_rate, activated_status, create_at, update_at)
                            values (%s, %s, %s, %s, %s, %s);"""
                cur.execute(query, (self.dt_id, payment_type, payment_rate, 1, self.create_at, self.update_at))
            elif action_type == 3:
                # 如果是删除操作
                query = """DELETE FROM dt_payment WHERE dt_id=%s and payment_type=%s;"""
                cur.execute(query, (self.dt_id, payment_type))
                if not sub_mch_ids:
                    sub_mch_ids = self.get_cs_ids(cur)
                for mch_id in sub_mch_ids:
                    query = """DELETE FROM mch_payment WHERE mch_id=%s and payment_type=%s;"""
                    cur.execute(query, (mch_id, payment_type))

            # 新增支付方式
            if not is_exist or action_type == 1:
                if not sub_mch_ids:
                    sub_mch_ids = self.get_cs_ids(cur)
                for mch_id in sub_mch_ids:
                    real_mch_id = mch_id[0] if mch_id else None
                    if not real_mch_id:
                        continue
                    query = """insert into mch_payment
                        (mch_id, payment_type, payment_rate, activated_status, create_at, update_at)
                        values (%s, %s, %s, 1, %s, %s);"""
                    cur.execute(query, (real_mch_id, payment_type, payment_rate, self.create_at, self.create_at))

    def get_cs_ids(self, cur):
        query = """select mch_inlet_info.mch_id from mch_inlet_info where mch_inlet_info.cs_id=%s;"""
        cur.execute(query, (self.dt_id,))
        mch_ids = cur.fetchall()
        return mch_ids

    def get_dt_wx_reg_payment(self, cur):
        query = """select id from dt_payment where dt_id=%s and payment_type in (1,2,3,101,102,103);"""
        cur.execute(query, (self.dt_id,))
        ret = cur.fetchone()
        return ret

    def get_dt_wx_app_payment(self, cur):
        query = """select id from dt_payment where dt_id=%s and payment_type in (4, 104);"""
        cur.execute(query, (self.dt_id,))
        ret = cur.fetchone()
        return ret

    def get_dt_ali_payment(self, cur):
        query = """select id from dt_payment where dt_id=%s and payment_type in (7,8,9,107,108,109);"""
        cur.execute(query, (self.dt_id,))
        ret = cur.fetchone()
        return ret

    def update_dt_user(self, cur):
        query = """
            update dt_user set
            status=%s,
            update_at=%s where dt_id=%s
        """
        cur.execute(query, (self.status, self.update_at, self.dt_id))

    def auth_dt_inlet(self, cur):
        query = """update dt_inlet_info set
            auth_status=%s,
            update_at=%s where dt_id=%s"""
        cur.execute(query, (self.status, self.update_at, self.dt_id))

    def add_auth_inlet_info(self, cur):
        auth_user = self.get_bk_email()
        query = """
            insert into auth_dt_info (
            dt_id,
            comment,
            auth_user,
            auth_status,
            create_at)
            values (%s, %s, %s, %s, %s);"""
        cur.execute(
            query,
            (
                self.dt_id,
                AUTH_STATUS[str(self.status)],
                auth_user,
                self.status,
                self.create_at
            )
        )

    def get_bk_email(self):
        # query = """select email from bk_user where bk_id=%s"""
        # cur.execute(query, (self.current_user,))
        # ret = cur.fetchone()
        # return ret[0]
        employee_id = self.session["employee_id"]
        employee = uline_session.query(Employee).filter(Employee.id == employee_id).one()
        user_profile = uline_session.query(UserProfile).filter(UserProfile.id == employee.user_id).one()
        email = user_profile.email
        return email

    def get_dt_user_wx_id(self, cur):
        query = """select wx_sub_mch_id, wx_app_sub_mch_id, ali_sub_mch_id
                   from dt_user where dt_id=%s"""
        cur.execute(query, (self.dt_id,))
        ret = cur.fetchone()
        return ret

    def get_dt_inlet_info(self, cur):
        query = """select dt_name, contact, mobile, email, old_ind_code, wx_ind_code, service_phone, wx_channel_id,
                          wx_app_channel_id, parent_id, dt_short_name, ali_ind_code, address, province, city, district, dt_sub_id
                          head_name, head_mobile, license_type, license_num, head_type
                   from dt_inlet_info
                   where dt_id=%s;"""
        cur.execute(query, (self.dt_id,))
        ret = cur.fetchone()
        return ret

    def get_dt_wx_config(self, cur):
        query = """select rate from dt_user where dt_id=%s;"""
        cur.execute(query, (self.dt_id,))
        ret = cur.fetchone()
        if ret and ret[0] == 1:
            return (WX_0_WX_MCH_ID, WX_0_WXPAY_KEY, WX_0_APPID)
        else:
            return (WX_MCH_ID, WXPAY_KEY, APPID)

    def get_update_wx_sub_info(self, cur):
        query = """
            select dt_inlet_info.dt_id,
            dt_inlet_info.mobile,
            dt_user.wx_sub_mch_id,
            dt_inlet_info.service_phone
            from
            dt_inlet_info
            inner join dt_user on dt_user.dt_id=dt_inlet_info.dt_id
            where dt_inlet_info.dt_id=%s;"""
        cur.execute(query, (self.dt_id,))
        ret = cur.fetchone()
        return ret

    @gen.coroutine
    def create_wx_sub_dt_id(self, dt_inlet_info, channel_id, APPID, WX_MCH_ID, WXPAY_KEY, WX_PRIVATE_KEY, WX_PUB_KEY,
                            WX_ROOT_CA):
        wx_business_no = dt_inlet_info[5] if dt_inlet_info[5] else dt_inlet_info[4]

        query_args = {
            "appid": APPID,
            "mch_id": WX_MCH_ID,
            "merchant_name": self.changed_dt_name,
            "merchant_shortname": self.changed_dt_shortname,
            "service_phone": self.changed_service_phone if self.changed_service_phone else self.changed_mobile,
            'contact': self.changed_contact,
            "contact_phone": self.changed_mobile,
            "contact_email": self.changed_email,
            "business": wx_business_no,
            "merchant_remark": self.dt_id,
            'channel_id': channel_id
        }
        result = yield create_wx_mch(query_args, WXPAY_KEY, WX_PRIVATE_KEY, WX_PUB_KEY, WX_ROOT_CA)
        if not result:
            result = dict(result_code='FAIL')
        raise gen.Return(result)

    @gen.coroutine
    def update_wx_sub_dt_id(self, cur, dt_inlet_info, APPID, WX_MCH_ID, WXPAY_KEY, WX_PRIVATE_KEY, WX_PUB_KEY,
                            WX_ROOT_CA):
        mchInletToWx = UpdateMerchantInletToWx(APPID, WX_MCH_ID, WXPAY_KEY)

        merchant_shorname = self.changed_dt_shortname
        service_phone = self.changed_service_phone if self.changed_service_phone else self.changed_mobile
        data = mchInletToWx.handle()(
            merchant_shortname=merchant_shorname,
            service_phone=service_phone,
            sub_mch_id=dt_inlet_info[2],
        )
        log.exception.info(
            'update reg info to wx, shortname:{}, service_phone:{}'.format(merchant_shorname, service_phone))
        wx_reg = ""
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
            self.save_dt_inlet_to_wx(cur, ret)
            default_err_msg = '更新微信支付出现未知错误,请联系客服!'
            deal_result, wx_reg = deal_with_wx_result(ret, 'result_code', default_err_msg)
            if deal_result != 'SUCCESS':
                is_success = False
        elif not self.merchant_info_in_wx:
            # 如果没有从微信获取有效信息 ，应该不会发生
            log.exception.info('chain update_wx_sub_dt_id no merchant_info from wx')
            is_success = False
            wx_reg = '微信侧没有对应的商户，请联系客服解决'
        else:
            wx_reg = '不需要更新到微信'
        raise gen.Return((is_success, wx_reg))

    def add_wx_sub_dt_id(self, cur):
        query = """update dt_user set wx_sub_mch_id=%s,
        update_at=%s where dt_id=%s"""
        cur.execute(query, (self.wx_sub_dt_id, self.update_at, self.dt_id))

    def add_wx_app_sub_dt_id(self, cur):
        query = """update dt_user set wx_app_sub_mch_id=%s,
            update_at=%s where dt_id=%s"""
        cur.execute(query, (self.wx_app_sub_dt_id, self.update_at, self.dt_id))

    def save_dt_inlet_to_wx(self, cur, ret):
        query = """
            insert into dt_inlet_to_wx_info (
            dt_id, return_code, return_msg,
            result_code, result_msg, create_at
            ) values (%s, %s, %s, %s, %s, %s);"""
        cur.execute(
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
    def update_app_info2wx(self, cur):
        """更新app商户信息到微信
        :return:
            更新到微信，微信返回的结果，一个dict
        """
        # 获取更新相关信息
        dt_inlet_info = self.get_update_wx_app_sub_info(cur)

        # merchant_name = dt_inlet_info[4]
        # merchant_shorname = u'{}微信支付商户'.format(BANK_NAME)
        merchant_shorname = self.changed_dt_shortname
        service_phone = self.changed_service_phone if self.changed_service_phone else self.changed_mobile
        search_info = {
            # 'merchant_name': merchant_name,
            'sub_mch_id': dt_inlet_info[2]
        }
        self.app_merchant_info_in_wx = yield self.get_mch_info_from_wx(search_info, WX_APP_APPID, WX_APP_MCH_ID,
                                                                       WXPAY_APP_KEY, WX_APP_PRIVATE_KEY,
                                                                       WX_APP_PUB_KEY, WX_ROOT_CA)

        is_success = True
        wx_app_info = ''
        # 同步至微信
        # 当从微信获取的商户信息不同现有信息时，才进行修改
        if self.app_merchant_info_in_wx and (
            (self.app_merchant_info_in_wx['merchant_shortname'] != merchant_shorname) or (
                self.app_merchant_info_in_wx['service_phone'] != service_phone)):
            updateinfo = {
                'service_phone': service_phone,
                'wx_mch_id': dt_inlet_info[2],
                'short_name': merchant_shorname,
            }
            result = yield self.update_mch_info2wx(updateinfo, WX_APP_APPID, WX_APP_MCH_ID, WXPAY_APP_KEY,
                                                   WX_APP_PRIVATE_KEY, WX_APP_PUB_KEY, WX_ROOT_CA)

            log.exception.info('update wx app mch info result:{}'.format(
                json.dumps(result, ensure_ascii=False)))
            self.save_dt_inlet_to_wx(cur, result)
            default_err_msg = '进件到微信APP支付发生未知错误,请联系客服!'
            deal_result, wx_app_info = deal_with_wx_result(result, 'result_code', default_err_msg)
            if deal_result != 'SUCCESS':
                is_success = False
                log.exception.info('update wx app mch failed')
        elif not self.app_merchant_info_in_wx:
            # 微信中没有商户信息，添加日志，修改失败
            log.exception.info('update_app_info2wx no merchant info from wx, app_sub_id:{0}, merchant name:{1}'.format(
                dt_inlet_info[2], merchant_shorname))
            is_success = False
            wx_app_info = '微信侧没有对应的APP商户，请联系客服解决'
        else:
            wx_app_info = '不需要更新到微信'

        raise gen.Return((is_success, wx_app_info))

    def get_update_wx_app_sub_info(self, cur):
        query = """
                select dt_inlet_info.dt_id,
                dt_inlet_info.mobile,
                dt_user.wx_app_sub_mch_id,
                dt_inlet_info.service_phone,
                dt_inlet_info.dt_name
                from  dt_inlet_info
                inner join dt_user on dt_user.dt_id=dt_inlet_info.dt_id
                where dt_inlet_info.dt_id=%s;"""
        cur.execute(query, (self.dt_id,))
        ret = cur.fetchone()
        return ret

    def add_fail_auth_inlet_info(self, cur, show_comment):
        auth_user = self.get_bk_email()
        query = """
            insert into auth_dt_info (
            dt_id,
            comment,
            auth_user,
            auth_status,
            create_at)
            values (%s, %s, %s, %s, %s);"""
        cur.execute(
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

    def get_chain_parent_info(self, cur, parent_id):
        query = """SELECT wx_channel_id, wx_app_channel_id, alipay_pid FROM dt_inlet_info where dt_id=%s"""
        cur.execute(query, (parent_id,))
        result = cur.fetchone()
        return result

    def update_cs_wx_sub_id(self, cur):
        update_args = {}
        params = []
        columns = []

        if self.wx_sub_dt_id:
            update_args['wx_sub_mch_id'] = self.wx_sub_dt_id

        if self.wx_app_sub_dt_id:
            update_args['wx_app_sub_mch_id'] = self.wx_app_sub_dt_id

        if self.ali_sub_mch_id:
            update_args['ali_sub_mch_id'] = self.ali_sub_mch_id

        for each_column in update_args:
            columns.append("{}=%s".format(each_column))
            params.append(update_args[each_column])

        params.append(self.dt_id)
        sql = """UPDATE mch_user SET {} WHERE EXISTS
                 (select 1 from mch_inlet_info where mch_inlet_info.mch_id=mch_user.mch_id and mch_inlet_info.cs_id=%s)
             """
        sql = sql.format(','.join(columns))
        cur.execute(sql, tuple(params))

    def get_all_db_payments(self, cursor):
        query = """select payment_type from dt_payment where dt_id=%s"""
        cursor.execute(query, (self.dt_id,))
        return cursor.fetchall()
