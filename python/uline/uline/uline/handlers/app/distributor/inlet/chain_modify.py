# -*- coding: utf-8 -*-
'''
BEGIN
添加商户进件信息
    必选参数:

    可选参数:

    成功:
        {"code": 200, "msg": "成功"}
    失败:
        {"code": 406, "msg": "失败"}
END
'''
import json
import uuid
from datetime import date

import os
from tornado import gen
from tornado.web import authenticated, asynchronous

from uline.handlers.baseHandlers import DtAdminHandler
from uline.public import common
from uline.public.constants import old_payment_relations
from uline.utils.record import record_utils
from uline.public.constants import CHAIN_PAY_TYPES
from .form import ModifyChainlnletForm
from decimal import Decimal
from uline.settings import FEATURE_SWITCH, MIN_ALI_LEVEL
from uline.model.uline.info import DtPayment
from uline.public import log
from uline.public.permit import check_permission
from uline.backend.risk import query_mch_risk_info


class ModifyChainGeneralHandler(DtAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        self.open_wx_app_pay = FEATURE_SWITCH.get('APP_PAY', False)
        self.chain_d0 = FEATURE_SWITCH.get('CHAIN_D0')
        self.dt_id = self.current_user
        self.form = ModifyChainlnletForm(self)
        self.form.dt_id = self.dt_id

        if self.request.files.get('id_card_img_f'):
            self.form.id_card_img_f.raw_data = self.request.files.get(
                'id_card_img_f', None)

        if self.request.files.get('id_card_img_b'):
            self.form.id_card_img_b.raw_data = self.request.files.get(
                'id_card_img_b', None)

        if self.request.files.get('license_img'):
            self.form.license_img.raw_data = self.request.files.get(
                'license_img', None)

        self.bank_no = self.form.bank_no.data
        if self.bank_no:
            bankName = self.get_bank_name()
            setattr(self.form, 'bankName', bankName)

        self.chain_id = self.form.chain_id.data
        self.has_been_authed = self.has_authed()

        self.u_ind_code = self.form.industry_no.data
        with self.db.get_db() as cursor:
            self.dt_infos = self.get_uline_dt_infos(cursor)

        if not self.u_ind_code and self.dt_infos:
            self.industry_name = self.dt_infos[3]
            self.form.industry_no.data = self.dt_infos[0]
            self.u_ind_code = self.dt_infos[0]
            if self.industry_name:
                setattr(self.form, 'industryName', self.industry_name)
                area, cmbProvince, cmbCity, cmbArea = (
                    self.industry_name).split('-')
                self.form.area.data = area
                self.form.cmbProvince.data = cmbProvince
                self.form.cmbCity.data = cmbCity
                self.form.cmbArea.data = cmbArea

        self.chain_name = self.form.chain_name.data
        if not self.chain_name and self.dt_infos:
            self.chain_name = self.dt_infos[1]
            self.form.chain_name.data = self.chain_name
        self.chain_shortname = self.form.chain_shortname.data
        if not self.chain_shortname and self.dt_infos:
            self.chain_shortname = self.dt_infos[4]
            self.form.chain_shortname.data = self.chain_shortname

        wx_app_payment = self.uline_session.query(DtPayment).filter(DtPayment.dt_id == self.current_user,
                                                                    DtPayment.payment_type.in_((4, 104))).first()
        self.can_use_wx_app = True if wx_app_payment else False
        self.dt_sub_id = self.form.dt_sub_id.data

    def has_authed(self):
        query = """select 1 from auth_dt_info where dt_id=%s and auth_status=2;"""
        result = self.db.selectSQL(query, (self.chain_id,))
        return bool(result)

    def generate_unchanged_render_params(self):
        return {
            'form': self.form,
            'OPEN_D0': self.chain_d0,
            'error_inlet_info_html': self.render_string('common/error_inlet_add_info.html', data=self.form),
            'open_wx_app_pay': self.open_wx_app_pay and self.can_use_wx_app,
            'has_been_authed': self.has_been_authed,
            'need_m3': MIN_ALI_LEVEL.upper() >= "M3",
        }

    @asynchronous
    @gen.coroutine
    def get(self):
        # 有3个字段经常出现特殊字符，暂时先后台直接给出，不需要前端拼接url
        address, id_card_no, license_scope, balance_name, name, shortname = self.get_dt_license_scope_and_address()
        self.form.address.data = address
        self.form.id_card_no.data = id_card_no
        self.form.license_scope.data = license_scope
        self.form.balance_name.data = balance_name
        self.form.chain_name.data = name
        self.form.chain_shortname.data = shortname

        if not self.dt_sub_id:
            self.dt_sub_id = self.dt_infos[5]
            self.form.dt_sub_id.data = self.dt_infos[5]
        self.render('distributor/inlet/chainModify.html', rate_error=False)

    @asynchronous
    @gen.coroutine
    def post(self):
        rate_error = False
        self.license_period = self.form.licensePeriod.data
        if self.license_period:
            self.form.licensePeriod.data = '2'
        if not (
                self.form.checkItem1.data >= 0 or
                self.form.checkItem2.data >= 0 or
                self.form.checkItem3.data >= 0 or
                self.form.checkItem4.data >= 0 or
                self.form.checkItem7.data >= 0 or
                self.form.checkItem8.data >= 0 or
                self.form.checkItem9.data >= 0):
            self.form.errors['checkItem'] = [u'费率不能为空']

        self.has_alipay = self.form.checkItem7.data or self.form.checkItem8.data or self.form.checkItem9.data
        log.exception.info('self.has_alipay={}'.format(self.has_alipay))
        log.exception.info(self.form.checkItem7.data, self.form.checkItem8.data, self.form.checkItem9.data)

        if self.form.errors or not self.form.validate():
            error_inlet_info_html = self.render_string(
                'common/error_inlet_add_info.html', data=self.form)
            self.render('distributor/inlet/chainModify.html',
                        rate_error=rate_error)
            self.finish()
            return

        # 判断费率是否调整到高于下边商户费率

        self.email = self.form.email.data
        self.dt_name = self.form.chain_name.data
        self.chain_shortname = self.form.chain_shortname.data

        self.province = self.form.province.data
        self.city = self.form.city.data
        self.address = self.form.address.data
        self.district = self.form.district.data
        self.servicePhone = self.form.service_phone.data
        self.mobile = self.form.mobile.data

        self.license_num = self.form.license_num.data
        self.license_start_date = self.form.license_start_date.data
        self.license_end_date = self.form.licenseEndDate.data
        if self.license_period:
            self.license_period = 2
        else:
            self.license_period = 1
        self.license_scope = self.form.license_scope.data

        self.balance_type = self.form.balance_type.data
        self.contact = self.form.contact.data
        self.balance_name = self.form.balance_name.data
        self.balance_account = self.form.balance_account.data
        self.id_card_no = self.form.id_card_no.data

        imgFrontFile = self.request.files.get('id_card_img_f')
        imgBackFile = self.request.files.get('id_card_img_b')
        licenceImgFile = self.request.files.get('license_img')

        self.id_card_img_f = self.save_idCard_img(imgFrontFile) if imgFrontFile else \
            self.form.imgCardFrontOld.data.split('/')[6]
        self.id_card_img_b = self.save_idCard_img(imgBackFile) if imgBackFile else \
            self.form.imgCardBackOld.data.split('/')[6]
        self.license_img = self.save_idCard_img(licenceImgFile) if licenceImgFile else \
            self.form.licenseImgOld.data.split('/')[6]

        # 存储修改信息到 变更记录表
        self.change_dict = {}

        self.wx = self.form.wx.data
        self.alipay = self.form.alipay.data

        wx_alipay = True

        if self.wx:
            if not isinstance(self.wx, Decimal):
                wx_alipay = False
                self.form.errors['wx'] = [u'微信提现手续费异常']
            else:
                if not (
                    self.form.checkItem101.data >= 0 or
                    self.form.checkItem102.data >= 0 or
                    self.form.checkItem103.data >= 0 or
                    self.form.checkItem104.data >= 0
                ):
                    wx_alipay = False
                    self.form.errors['checkItem'] = [u'微信D0费率不能为空']

        if self.alipay:
            if not isinstance(self.alipay, Decimal):
                wx_alipay = False
                self.form.errors['alipay'] = [u'支付宝提现手续费异常']
            else:
                if not (
                    self.form.checkItem107.data >= 0 or
                    self.form.checkItem108.data >= 0 or
                    self.form.checkItem109.data >= 0
                ):
                    wx_alipay = False
                    self.form.errors['checkItem'] = [u'支付宝D0费率不能为空']

        if not wx_alipay:
            error_inlet_info_html = self.render_string(
                'common/error_inlet_add_info.html', data=self.form)
            self.render('distributor/inlet/chainModify.html',
                        rate_error=True if rate_error else False)
            return
        self.auth_status = 1
        self.update_at = common.timestamp_now()

        self.license_type = self.form.license_type.data
        self.head_name = self.form.head_name.data
        self.head_mobile = self.form.head_mobile.data
        self.head_type = self.form.head_type.data

        with self.db.get_db() as cur:
            self.update_inlet_infos = self.get_update_inlet_infos(cur, self.update_at, self.auth_status)

            if self.update_inlet_infos:
                if self.update_inlet_infos.get('error_ind_code', False):
                    self.form.errors['invalid_ind_code'] = ["无效的行业信息"]
                else:
                    u_ind_code = self.update_inlet_infos.get('u_ind_code', '')
                    if u_ind_code:
                        wx_ind_code = self.update_inlet_infos.get(
                            'wx_ind_code', '')
                        ali_ind_code = self.update_inlet_infos.get(
                            'ali_ind_code', '')
                        ali_ind_name, wx_ind_name = self.get_industry_name(
                            cur, ali_ind_code, wx_ind_code)
                        self.change_dict['ali_ind_name'] = ali_ind_name
                        self.change_dict['wx_ind_name'] = wx_ind_name

        mutable_fields = self.get_not_mutable_feilds()
        if mutable_fields:
            self.form.errors['not_mutable'] = [
                ','.join(mutable_fields) + u'不支持修改']

        if self.has_alipay and MIN_ALI_LEVEL == "M3":
            if not self.license_type:
                self.form.errors['license_type'] = [u'请填入营业执照类型']
            if not self.head_name:
                self.form.errors['head_name'] = [u'请填入负责人姓名']
            if not self.head_mobile:
                self.form.errors['head_mobile'] = [u'请填入负责人联系电话']
            if not self.head_type:
                self.form.errors['head_type'] = [u'请填入负责人类型']
            if not self.district:
                self.form.errors['district'] = [u'请填入区域信息']

        if self.form.errors:
            error_inlet_info_html = self.render_string(
                'common/error_inlet_add_info.html', data=self.form)
            self.render('distributor/inlet/chainModify.html', form=self.form, rate_error=False,
                        has_been_authed=self.has_been_authed,
                        error_inlet_info_html=error_inlet_info_html)
            self.finish()
            return

        with self.db.get_db() as cur:
            yield self.update_balance_payment(cur)
            if self.alipay is not None or self.wx is not None:
                yield self.update_d0_withdraw_fee(cur)
            yield self.update_inlet_info(cur)
            self.add_auth_inlet_info(cur)
        if self.change_dict:
            yield self.add_change_record()  # 存储变更信息逻辑结束
        chain_info = {
            'id_card_no': self.id_card_no,
            'balance_account': self.balance_account,
            'license_num': self.license_num,
        }
        gen.Task(query_mch_risk_info.query_merchant_risk_info.apply_async,
                 args=[self.chain_id, 'chain', chain_info])
        self.redirect('/dist/inlet/chain')

    def get_industry_name(self, cursor, ali_code, wx_code):
        sql = """select industry_name from industry_ali_info where industry_code=%s;"""
        cursor.execute(sql, (ali_code,))
        ali_ind_name = cursor.fetchone()
        ali_ind_name = ali_ind_name[0] if ali_ind_name else ''

        query = """select industry_name from industry_uline_info where wx_ind_code=%s and status=2;"""
        cursor.execute(query, (wx_code,))
        wx_ind_name = cursor.fetchone()
        wx_ind_name = wx_ind_name[0] if wx_ind_name else ''
        return ali_ind_name, wx_ind_name

    def get_not_mutable_feilds(self):
        fields = {
            'dt_name': u'渠道商名称',
            'dt_type': u'渠道商类型',
            'u_ind_code': u'经营类目'
        }
        if self.has_been_authed:
            return [fields[each_filed] for each_filed in fields if each_filed in self.update_inlet_infos]

    @gen.coroutine
    def add_change_record(self):
        # 存储变更信息逻辑开始
        select_change_record = yield record_utils.select_change_record_by_dt_id(self, fetchone=False, change_type=3)
        if len(select_change_record) == 0:
            # 插入新的数据
            record_utils.insert_change_record(
                self, (self.chain_id, json.dumps(self.change_dict, cls=ComplexEncoder)))
        elif len(select_change_record) == 1:
            # 更新信息
            record_utils.update_change_record(
                self, (json.dumps(self.change_dict, cls=ComplexEncoder), 1, self.chain_id))

    # def get_industry_name(self):
    #     query = """select industry_name from industry_uline_info where industry_code=%s;"""
    #     ret = self.db.selectSQL(query, (self.u_ind_code,))
    #     industry_name = ret[0] if ret else ''
    #     return industry_name

    def get_bank_name(self):
        query = """select bank_name from balance_bank_info where bank_no=%s;"""
        ret = self.db.selectSQL(query, (self.bank_no,))
        bank_name = ret[0] if ret else ''
        return bank_name

    def save_idCard_img(self, imgFile):
        base_dir = os.path.join(self.application.base_dir,
                                'static/uploads/dt/idcard')
        file_dir = os.path.join(base_dir, '{}'.format(self.chain_id))
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        file_name = '{}.jpg'.format(uuid.uuid4().hex)
        file_path = os.path.join(file_dir, file_name)

        try:
            with open(file_path, 'wb') as f:
                f.write(imgFile[0]['body'])
        except Exception as err:
            raise err
        return file_name

    def get_wx_ali_ind_code(self, cursor, u_ind_code):
        query = """select wx_ind_code, ali_ind_code,industry_name
                   from industry_uline_info where industry_code=%s and status=1;"""
        cursor.execute(query, (u_ind_code,))
        ret = cursor.fetchone()
        return ret

    # @gen.coroutine
    # def get_old_ind_code(self, cursor):
    #     query = """select old_ind_code from dt_inlet_info where dt_id=%s;"""
    #     cursor.execute(query, (self.dt_id,))
    #     ret = cursor.fetchone()
    #     raise gen.Return(ret)

    @gen.coroutine
    def update_inlet_info(self, cursor):
        # 更新的渠道商的基本信息,下一步更新支付信息
        # activated_status = 1
        # ret_code = yield self.get_wx_ali_ind_code(cursor)
        # wx_ind_code, ali_ind_code = ret_code[0], ret_code[1]

        if self.update_inlet_infos:
            self.change_dict.update(self.update_inlet_infos)
        # 如果有修改的内容
        # if self.change_dict:
        if True:
            updates = {}
            updates['update_at'] = self.update_at
            updates['auth_status'] = self.auth_status

            update_str = ','.join(["{0}=%({0})s".format(key)
                                   for key in updates])
            sql = """update dt_inlet_info set """ + \
                  update_str + ' where dt_id=%(dt_id)s'
            updates['dt_id'] = self.chain_id
            cursor.execute(sql, updates)
            # cursor.execute(query, query_dt_inlet_info_dict)

    def get_update_inlet_infos(self, cursor, update_at, auth_status):
        try:
            self.province = self.province.split('-')[1]
            self.city = self.city.split('-')[1]
        except Exception as err:
            print err
        may_update_keys = ['dt_name', 'province', 'city', 'district', 'address', 'contact', 'mobile', 'service_phone',
                           'email', 'id_card_img_f', 'id_card_img_b', 'dt_id', 'license_num',
                           'license_start_date', 'license_end_date', 'license_period', 'license_scope', 'license_img',
                           'u_ind_code', 'dt_short_name', 'dt_sub_id', 'license_type', 'head_name', 'head_mobile', 'head_type']

        query_columns = ','.join(may_update_keys)
        query = """select {} from dt_inlet_info where dt_id=%s;""".format(
            query_columns)
        cursor.execute(query, (self.chain_id,))
        result = cursor.fetchone()
        dt_inlet_info = {}
        if result:
            dt_inlet_info = dict(zip(may_update_keys, result))
        query_dt_inlet_info_dict = {
            'dt_name': self.dt_name,
            'province': self.province,
            'city': self.city,
            'district': self.district,
            'address': self.address,
            'contact': self.contact,
            'mobile': self.mobile,
            'service_phone': self.servicePhone,
            'email': self.email,
            'id_card_img_f': self.id_card_img_f,
            'id_card_img_b': self.id_card_img_b,
            'auth_status': auth_status,
            'dt_id': self.chain_id,
            'license_num': self.license_num,
            'update_at': update_at,
            'license_start_date': self.license_start_date,
            'license_end_date': self.license_end_date,
            'license_period': self.license_period,
            'license_scope': self.license_scope,
            'license_img': self.license_img,
            'u_ind_code': self.u_ind_code,
            'dt_sub_id': self.dt_sub_id,
            'dt_short_name': self.chain_shortname,
            'license_type': self.license_type,
            'head_name': self.head_name,
            'head_mobile': self.head_mobile,
            'head_type': self.head_type,
        }
        need_update_infos = {key: query_dt_inlet_info_dict[key] for key in dt_inlet_info if
                             key in query_dt_inlet_info_dict and
                             dt_inlet_info[key] != query_dt_inlet_info_dict[key]}

        # 更新行业信息
        u_ind_code = need_update_infos.get('u_ind_code', '')
        if u_ind_code:

            wx_ali_ind_code = self.get_wx_ali_ind_code(cursor, u_ind_code)
            if wx_ali_ind_code:
                need_update_infos['wx_ind_code'], need_update_infos['ali_ind_code'], need_update_infos[
                    'u_ind_name'] = wx_ali_ind_code
            else:
                need_update_infos['error_ind_code'] = True
        if need_update_infos:
            self.change_dict.update(need_update_infos)
        return need_update_infos

    @gen.coroutine
    def update_d0_withdraw_fee(self, cursor):
        # 数据库只能存int
        wx = int(self.wx * 100) if self.wx else self.wx
        alipay = int(self.alipay * 100) if self.alipay else self.alipay
        role = {
            'wx': wx,
            'alipay': alipay
        }

        self.change_dict['role'] = role

    @gen.coroutine
    def update_balance_payment(self, cursor):
        # 渠道商结算账户表(dt_balance)
        # 渠道商支付方式表(dt_payment)
        sql = """select balance_type,balance_name,bank_no,balance_account,id_card_no from dt_balance where dt_id=%s"""
        cursor.execute(sql, (self.chain_id,))
        balance_in_db = cursor.fetchone()
        need_update_keys = ['balance_type', 'balance_name',
                            'bank_no', 'balance_account', 'id_card_no']
        balance_in_db = dict(zip(need_update_keys, balance_in_db))

        query_dt_balance_dict = {
            'balance_type': self.balance_type,
            'balance_name': self.balance_name,
            'bank_no': self.bank_no,
            'balance_account': self.balance_account,
            'id_card_no': self.id_card_no,
            # 'update_at': update_at,
            # 'dt_id': self.dt_id
        }

        update_infos = {key: query_dt_balance_dict[key] for key in query_dt_balance_dict if key in balance_in_db and
                        query_dt_balance_dict[key] != balance_in_db[key]}
        self.change_dict['balance_info'] = update_infos
        # query = """update dt_balance set
        #     balance_type=%(balance_type)s, balance_name=%(balance_name)s, bank_no=%(bank_no)s,
        #     balance_account=%(balance_account)s, id_card_no=%(id_card_no)s,
        #     update_at=%(update_at)s where dt_id=%(dt_id)s;"""
        #
        # cursor.execute(query, query_dt_balance_dict)

        # 转变成[[checkItem,payment_rate]] for循环
        for payment_type in CHAIN_PAY_TYPES:
            payment_rate = getattr(
                self.form, 'checkItem' + str(payment_type)).data
            if payment_rate >= 0:
                payment_rate = float(payment_rate) * 10
                query = """select id, activated_status, payment_rate
                           from dt_payment where dt_id=%s and payment_type=%s"""
                cursor.execute(query, (self.chain_id, payment_type))
                ret = cursor.fetchone()

                # 如果支付方式的费率没变，则不需要存储
                exist_pay_rate = 0
                if ret:
                    exist_pay_rate = ret[2]
                log.exception.info("chain modify paytypes:{},{}，{}".format(
                    payment_type, exist_pay_rate, payment_rate))
                if ret and exist_pay_rate == payment_rate:
                    continue

                if 'payment' not in self.change_dict:
                    self.change_dict['payment'] = {}

                if ret:
                    # query = """update dt_payment set
                    #     payment_type=%(payment_type)s, activated_status=%(activated_status)s,
                    #      update_at=%(update_at)s where dt_id=%(dt_id)s
                    #     and payment_type=%(payment_type)s;"""

                    exist_status = ret[1]

                    # payment_type 转成uline_payment_code

                    payment_type = old_payment_relations.get(str(payment_type))

                    change_status = 1
                    # 如果没有发生改变，则保持原有状态不变
                    if exist_status == 1:
                        # 如果之前状态为未激活,就应该保持为未激活
                        change_status = 1
                    else:
                        change_status = 3 if payment_rate != exist_pay_rate else exist_status

                    # 用作change_record表，为了和查询数据保持一致
                    # payment_query_dict = {
                    #     'payment_type': payment_type,
                    #     'activated_status': change_status,
                    #     'update_at': update_at,
                    #     'dt_id': self.chain_id
                    # }
                    # cursor.execute(query, payment_query_dict)

                    after_auth_status = 1 if payment_rate != exist_pay_rate else exist_status
                    update_info = {
                        'pay_type': payment_type,
                        'pay_rate': payment_rate,
                        'pre_status': exist_status,
                        'activated_status': change_status,
                        'action_type': 2,  # 1为新增 2为更新 3为删除
                        'after_auth_status': after_auth_status,
                    }
                    self.change_dict['payment'][payment_type] = update_info
                else:
                    update_info = {
                        'pay_type': payment_type,
                        'pay_rate': payment_rate,
                        'pre_status': 1,
                        'activated_status': 1,
                        'action_type': 1,  # 1为新增 2为更新 3为删除
                        'after_auth_status': 1,  # 审核通过之后的状态
                    }
                    self.change_dict['payment'][payment_type] = update_info

    def add_auth_inlet_info(self, cursor):
        auth_user = self.get_current_user_name(cursor)
        create_at = common.timestamp_now()
        query = """
            insert into auth_dt_info (dt_id, comment, auth_user, auth_status, create_at)
            values (%s, %s, %s, %s, %s);"""
        cursor.execute(
            query, (self.chain_id, u'提交修改', auth_user, 1, create_at))

    def get_current_user_name(self, cursor):
        query = """select dt_name from dt_user where dt_id=%s"""
        cursor.execute(query, (self.current_user,))
        ret = cursor.fetchone()
        return ret[0]

    def checkout_dt_payment_rate(self):
        checkout_payment_rate = map(lambda x: self.form.data.get(
            'payment_type' + str(x)) or 0, range(1, 10))
        above_rate = []
        for i, payment_rate in enumerate(checkout_payment_rate):
            if not payment_rate:
                continue
            query = """select DISTINCT(dt_payment.payment_type) from mch_payment inner join mch_inlet_info on
                      mch_inlet_info.mch_id = mch_payment.mch_id inner join dt_payment on
                      mch_inlet_info.dt_id = dt_payment.dt_id and dt_payment.payment_type = mch_payment.payment_type
                      where mch_payment.payment_rate < %s and dt_payment.dt_id=%s and
                      dt_payment.payment_type=%s;"""
            result = self.db.selectSQL(
                query, (float(payment_rate) * 10, self.chain_id, i + 1))
            if result:
                above_rate.append(result[0])
        return above_rate

    def force_update_rate(self):
        pass

    def get_uline_dt_infos(self, cursor):
        print self.chain_id
        sql = """select dt_inlet_info.u_ind_code, dt_inlet_info.dt_name, dt_inlet_info.dt_type,
                        industry_uline_info.industry_name, dt_short_name, dt_sub_id
                from dt_inlet_info
                INNER JOIN industry_uline_info ON dt_inlet_info.u_ind_code=industry_uline_info.industry_code
                where dt_inlet_info.dt_id=%s"""
        cursor.execute(sql, (self.chain_id,))
        result = cursor.fetchone()
        return result

    def get_dt_license_scope_and_address(self):
        query = """select dt_inlet_info.address, dt_balance.id_card_no, dt_inlet_info.license_scope,
                    dt_balance.balance_name,dt_inlet_info.dt_name, dt_inlet_info.dt_short_name
                  from dt_inlet_info INNER JOIN dt_balance on dt_balance.dt_id = dt_inlet_info.dt_id
                  WHERE dt_inlet_info.dt_id=%s;
        """
        ret = self.db.selectSQL(query, (self.chain_id,))
        return ret


class ComplexEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)
