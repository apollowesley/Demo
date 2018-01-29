#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @author: leiyutian
# @createTime: 2017-05-31, 09:51:17 GMT+0800
# @description: 新增连锁总店

import os
import datetime
import uuid
from decimal import Decimal

from tornado import gen
from uline.handlers.baseHandlers import DtAdminHandler
from uline.public import common, generate_employee_profile
from tornado.web import authenticated, asynchronous
from uline.handlers.app.distributor.inlet.form import AddChainGeneralForm
from uline.settings import FEATURE_SWITCH, MIN_ALI_LEVEL
from uline.model.uline.base import uline_session
from uline.public.db import uline_session_scope
from uline.model.uline.user import DtUser
from uline.model.uline.other import AuthDtInfo
from uline.model.uline.info import DtInletInfo, IndustryUlineInfo, DtPayment, DtBalance, BalanceBankInfo, D0WithdrawFee
from uline.public.constants import CHAIN_PAY_TYPES
from uline.public.permit import check_permission
from uline.public.constants import CHAIN_PAY_TYPES, translate_payment_type

from uline.backend.risk import query_mch_risk_info


class AddChainGeneralHandler(DtAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        self.open_wx_app_pay = FEATURE_SWITCH.get('APP_PAY', False)
        self.chain_d0 = FEATURE_SWITCH.get('CHAIN_D0')
        self.form = AddChainGeneralForm(self)
        setattr(self.form, 'dt_id', self.current_user)
        # 用于记录当前角色的上级是谁，方便通用接口
        setattr(self.form, 'father_name', 'dt')
        self.create_at = self.update_at = datetime.datetime.now()
        wx_app_payment = self.uline_session.query(DtPayment).filter(DtPayment.dt_id == self.current_user,
                                                                    DtPayment.payment_type.in_((4, 104))).first()
        self.can_use_wx_app = True if wx_app_payment else False

    def generate_unchanged_render_params(self):
        return {
            'form': self.form,
            'OPEN_D0': self.chain_d0,
            'error_inlet_info_html': self.render_string('common/error_inlet_add_info.html', data=self.form),
            'open_wx_app_pay': self.open_wx_app_pay and self.can_use_wx_app,
            'need_m3': MIN_ALI_LEVEL.upper() >= 'M3'
        }

    @gen.coroutine
    def get(self):
        self.render('distributor/inlet/chainAdd.html')

    @asynchronous
    @gen.coroutine
    def post(self):
        self.total_d1_rate = 0
        self.total_d0_rate = 0
        self.generate_payment_infos()
        # 是否有支付宝的支付方式
        self.has_alipay = any(payment_info['uline_payment_code'].startswith("ALI")
                              for payment_info in self.payment_infos)
        if not (self.total_d1_rate + self.total_d0_rate):
            self.form.errors['payment_type'] = [u'费率不能为空']

        self.wx = self.form.wx.data
        self.alipay = self.form.alipay.data

        # 检查d0手续费匹配
        self.check_d0_withdraw_fee()

        # 检查d0和d1并存情况
        if self.total_d0_rate and self.total_d1_rate:
            self.form.errors['payment_type'] = [u'不能同时选择d0费率和的费率']

        # 行业信息获取
        self.u_ind_code = self.form.industry_no.data
        if self.u_ind_code:
            self.industry_name = self.get_industry_name()
            setattr(self.form, 'industryName', self.industry_name)
            area, cmbProvince, cmbCity, cmbArea = (
                self.industry_name).split('-')
            self.form.area.data = area
            self.form.cmbProvince.data = cmbProvince
            self.form.cmbCity.data = cmbCity
            self.form.cmbArea.data = cmbArea

        bank_no = self.form.bank_no.data
        bankName = self.get_bank_name(bank_no) if bank_no else ''
        setattr(self.form, 'bankName', bankName)

        # 图片验证
        self.form.id_card_img_f.raw_data = self.request.files.get(
            'id_card_img_f', None)
        self.form.id_card_img_b.raw_data = self.request.files.get(
            'id_card_img_b', None)
        self.form.license_img.raw_data = self.request.files.get(
            'license_img', None)
        # 判断是否有3张照片
        if (self.form.id_card_img_f.raw_data is None) or (
                self.form.id_card_img_b.raw_data is None) or (
                self.form.license_img.raw_data is None):
            self.form.errors['img'] = [u'必须传入照片']

        if self.has_alipay and MIN_ALI_LEVEL == "M3":
            if not self.form.license_type.data:
                self.form.errors['license_type'] = [u'请填写营业执照类型']
            if not self.form.head_name.data:
                self.form.errors['head_name'] = [u'请填写负责人姓名']
            if not self.form.head_mobile.data:
                self.form.errors['head_mobile'] = [u'请填写负责人联系电话']
            if not self.form.head_type.data:
                self.form.errors['head_type'] = [u'请填写负责人类型']
            if not self.form.district.data:
                self.form.errors['district'] = [u'请填写区域信息']

        if self.form.errors or not self.form.validate():
            self.render('distributor/inlet/chainAdd.html')
            return

        self.dt_sub_id = self.form.dt_sub_id.data
        self.generate_inlet_data()
        self._password = yield common.bcrypt_pwd(str(self.mobile))

        with uline_session_scope() as session:
            yield self.add_chain_user(session)
            self.add_chain_inlet_info(session)
            self.save_balance_payment(session)
            self.add_auth_inlet_info(session)
            if self.alipay is not None or self.wx is not None:
                self.save_d0_withdraw_fee(session)
            yield generate_employee_profile.employee_profile("mr", self.dt_id, self.email,
                                                             self._password, self.chain_name,
                                                             phone1=self.mobile, city=self.city, sex=None)
        chain_info = {
            'id_card_no': self.id_card_no,
            'balance_account': self.balance_account,
            'license_num': self.license_num,
        }
        gen.Task(query_mch_risk_info.query_merchant_risk_info.apply_async,
                 args=[self.dt_id, 'chain', chain_info])
        self.redirect('/dist/inlet/chain')

    def check_d0_withdraw_fee(self):
        self.wx = self.form.wx.data
        self.alipay = self.form.alipay.data

        wx_alipay = True

        wx_d0_total_rate = 0
        ali_d0_total_rate = 0

        for each_payment in self.payment_infos:
            if each_payment['payment_type'] in [101, 102, 103, 104]:
                wx_d0_total_rate += each_payment['payment_rate']
            elif each_payment['payment_type'] in [107, 108, 109]:
                ali_d0_total_rate += each_payment['payment_rate']

        if self.wx:
            if not isinstance(self.wx, Decimal):
                wx_alipay = False
                self.form.errors['wx'] = [u'微信提现手续费异常']
            elif not wx_d0_total_rate >= 0:
                wx_alipay = False
                self.form.errors['checkItem'] = [u'微信D0费率不能为空']

        if self.alipay:
            if not isinstance(self.alipay, Decimal):
                wx_alipay = False
                self.form.errors['alipay'] = [u'支付宝提现手续费异常']
            elif not ali_d0_total_rate:
                wx_alipay = False
                self.form.errors['checkItem'] = [u'支付宝D0费率不能为空']
        return wx_alipay

    def generate_inlet_data(self):
        self.contact = self.form.contact.data
        self.email = self.form.email.data
        self.mobile = self.form.mobile.data
        self.activate_email_tag = self.form.activate_email_tag.data
        self.chain_shortname = self.form.chain_shortname.data
        self.u_ind_code = self.form.industry_no.data
        self.service_phone = self.form.service_phone.data

        self.chain_name = self.form.chain_name.data
        self.province = self.form.province.data
        self.city = self.form.city.data
        self.district = self.form.district.data
        self.address = self.form.address.data

        self.license_num = self.form.license_num.data
        self.license_start_date = self.form.license_start_date.data
        self.license_period = self.form.licensePeriod.data
        if self.license_period:
            self.license_period = 2
        else:
            self.license_period = 1
        if self.license_period == 1:
            self.license_end_date = self.form.licenseEndDate.data
        else:
            self.license_end_date = None
        self.license_scope = self.form.license_scope.data
        self.dt_id = common.create_dt_id()

        licence_img_file = self.request.files.get('license_img')
        self.license_img = self.save_id_card_img(licence_img_file)

        self.id_card_no = self.form.id_card_no.data
        img_front_file = self.request.files.get('id_card_img_f')
        img_back_file = self.request.files.get('id_card_img_b')
        self.id_card_img_f = self.save_id_card_img(img_front_file)
        self.id_card_img_b = self.save_id_card_img(img_back_file)

        self.bank_no = self.form.bank_no.data
        self.balance_type = self.form.balance_type.data
        self.balance_name = self.form.balance_name.data
        self.balance_account = self.form.balance_account.data

        self.wx = self.form.wx.data
        self.alipay = self.form.alipay.data

        self.license_type = self.form.license_type.data
        self.head_name = self.form.head_name.data
        self.head_mobile = self.form.head_mobile.data
        self.head_type = self.form.head_type.data

    def generate_payment_infos(self):
        self.payment_infos = list()
        for payment_type in CHAIN_PAY_TYPES:
            payment_rate = getattr(
                self.form, 'payment_type' + str(payment_type)).data
            if payment_rate >= 0:
                payment_info = {
                    'payment_type': payment_type,
                    'payment_rate': payment_rate * 10,
                    'settle_rate': payment_rate * 10,
                    'activated_status': 1,
                    'create_at': self.create_at,
                    'update_at': self.update_at,
                }
                tmp_str = translate_payment_type.get(payment_type)
                if tmp_str:
                    uline_payment_id, uline_settle_id, trade_type,\
                        thirdparty_mch_id, uline_payment_code = tmp_str.split('|')
                    payment_info['uline_payment_id'] = uline_payment_id
                    payment_info['uline_settle_id'] = uline_settle_id
                    payment_info['trade_type'] = trade_type
                    payment_info['uline_payment_code'] = uline_payment_code
                self.payment_infos.append(payment_info)
                if payment_type < 100:
                    self.total_d1_rate += payment_rate
                elif payment_type < 200:
                    self.total_d0_rate += payment_rate

    @gen.coroutine
    def add_chain_user(self, session):
        # 新建一个商户,默认密码123456
        # _password = yield common.bcrypt_pwd(str(self.mobile))
        self.mch_pay_key = os.urandom(16).encode('hex').upper()
        mch_pay_key = common.gen_randown_mch_pkey(32)

        userinfo = {
            'dt_id': self.dt_id,
            'dt_name': self.chain_name,
            'email': self.email,
            'password': self._password,
            'create_at': self.create_at,
            'update_at': self.update_at,
            'status': 1,  # 创建
            'mch_pay_key': mch_pay_key
        }
        dt_user = DtUser(**userinfo)
        session.add(dt_user)
        session.flush()

    def add_chain_inlet_info(self, session):
        industry_info = session.query(IndustryUlineInfo).filter(
            IndustryUlineInfo.industry_code == self.u_ind_code).first()
        bk_id = uline_session.query(DtInletInfo.bk_id).filter(DtInletInfo.dt_id == self.current_user).first()
        bk_id = bk_id[0]
        dt_inlet_info = {
            'dt_id': self.dt_id,
            'dt_name': self.chain_name,
            'province': self.province,
            'city': self.city,
            'district': self.district,
            'address': self.address,
            'contact': self.contact,
            'mobile': self.mobile,
            'service_phone': self.service_phone,
            'email': self.email,
            'id_card_img_f': self.id_card_img_f,
            'id_card_img_b': self.id_card_img_b,
            'auth_status': 1,
            'activated_status': 1,
            'u_ind_code': self.u_ind_code,
            'wx_ind_code': industry_info.wx_ind_code,
            'ali_ind_code': industry_info.new_ali_ind_code,
            'create_at': self.create_at,
            'update_at': self.update_at,
            'license_num': self.license_num,
            'license_start_date': self.license_start_date,
            'license_end_date': self.license_end_date,
            'license_period': self.license_period,
            'license_scope': self.license_scope,
            'license_img': self.license_img,
            'dt_short_name': self.chain_shortname,
            'parent_id': self.current_user,
            'dt_sub_id': self.dt_sub_id,
            'bk_id': bk_id,
            'activate_email_tag': self.activate_email_tag,
            'head_name': self.head_name,
            'head_mobile': self.head_mobile,
            'license_type': self.license_type,
            'head_type': self.head_type,
        }
        inlet_info = DtInletInfo(**dt_inlet_info)
        session.add(inlet_info)
        session.flush()

    def save_balance_payment(self, session):
        balance_info = {
            'dt_id': self.dt_id,
            'balance_way': 1,
            'balance_type': self.balance_type,
            'balance_name': self.balance_name,
            'bank_no': self.bank_no,
            'balance_account': self.balance_account,
            'id_card_no': self.id_card_no,
            'create_at': self.create_at,
            'update_at': self.update_at
        }
        dt_balance = DtBalance(**balance_info)
        session.add(dt_balance)

        for each_payment in self.payment_infos:
            each_payment['dt_id'] = self.dt_id
            dt_payment = DtPayment(**each_payment)
            session.add(dt_payment)
        session.flush()

    def add_auth_inlet_info(self, session):
        auth_user = session.query(DtUser).filter(
            DtUser.dt_id == self.current_user).first()
        auth_info = {
            'dt_id': self.dt_id,
            'comment': u'提交审核',
            'auth_user': auth_user.dt_name,
            'auth_status': 1,
            'create_at': self.create_at
        }
        dt_auth_info = AuthDtInfo(**auth_info)
        session.add(dt_auth_info)

    def get_industry_name(self):
        industry_name = ''
        industry_info = self.uline_session.query(IndustryUlineInfo).filter(
            IndustryUlineInfo.industry_code == self.u_ind_code).first()
        if industry_info:
            industry_name = industry_info.industry_name
        return industry_name

    def get_bank_name(self, bankno):
        bankinfo = uline_session.query(BalanceBankInfo).filter(
            BalanceBankInfo.bank_no == bankno).first()
        return bankinfo.bank_name if bankinfo else ""

    def save_id_card_img(self, imgFile):
        # 不需要根据环境判断存入目录
        base_dir = os.path.join(self.application.base_dir,
                                'static/uploads/dt/idcard')
        file_dir = os.path.join(base_dir, '{}'.format(self.dt_id))
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

    def save_d0_withdraw_fee(self, session):
        withdraw_info = {
            "role": self.dt_id,
            "role_type": 'chain',
            "wx": self.wx * 100 if self.wx else self.wx,
            "alipay": self.alipay * 100 if self.alipay else self.alipay
        }
        session.add(D0WithdrawFee(**withdraw_info))
        session.flush()
