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
import os
import uuid
from tornado import gen
from uline.public import log
from uline.handlers.baseHandlers import OfclAdminHandler
from uline.public import common, generate_employee_profile
from tornado.web import authenticated, HTTPError
from .form import AddDistributorlnlet
from decimal import Decimal
from uline.public.constants import PAY_TYPES, translate_payment_type, AVAILABLE_PAYMENTS, new_payment_relations
from uline.settings import FEATURE_SWITCH, DEFAULT_BANK_ID
from uline.utils.dayzero import form_verify
from uline.model.uline.user import BkUser
from uline.model.uline.base import uline_session
from uline.public.permit import check_permission


class AddDistributorInletHandler(OfclAdminHandler):

    @authenticated
    def prepare(self):
        self.open_d0 = FEATURE_SWITCH.get('OPEN_D0')
        # 是否使用新版进件
        self.NEW_INLET = FEATURE_SWITCH.get('NEW_INLET')
        self.WX_0_RATE = FEATURE_SWITCH.get('0_RATE')
        self.ALI_0_RATE = FEATURE_SWITCH.get('ALI_0_RATE')
        # 是否支持h5支付
        self.h5 = FEATURE_SWITCH.get('H5')
        self.jd_pay = FEATURE_SWITCH.get('JD_PAY')
        # 围餐
        self.form = AddDistributorlnlet(self)
        self.bk_profile = uline_session.query(BkUser.bk_id, BkUser.bk_name).filter(BkUser.bk_type == 2).all()
        self.open_dine = FEATURE_SWITCH.get('DINE_TOGETHER')
        self.use_dine = True if self.form.use_dine.data else False
        default_dine_value = 0 if self.open_dine and self.use_dine else None
        self.form.checkItem11.data = default_dine_value
        self.form.checkItem12.data = default_dine_value
        self.form.checkItem13.data = default_dine_value
        self.has_ali_payment = False

    def generate_unchanged_render_params(self):
        return {
            'open_dine': self.open_dine
        }

    @authenticated
    @check_permission
    def get(self):
        template = 'official/inlet/distributorAdd.html' if FEATURE_SWITCH.get(
            'NEW_INLET') else 'official/inlet/old_distributorAdd.html'

        # 提现手续费
        self.wx_draw_fee = self.ali_draw_fee = None
        if self.form.wx_draw_fee.data:
            self.wx_draw_fee = self.form.wx_draw_fee.data
        elif self.form.wx.data:
            self.wx_draw_fee = self.form.wx.data
        if self.form.ali_draw_fee.data:
            self.ali_draw_fee = self.form.ali_draw_fee.data
        elif self.form.alipay.data:
            self.ali_draw_fee = self.form.alipay.data
        # 提现垫资费
        self.wx_draw_rate = self.form.wx_draw_rate.data
        self.ali_draw_rate = self.form.ali_draw_rate.data

        self.add_filed()
        error_inlet_info_html = self.render_string(
            'common/error_inlet_add_info.html', data=self.form)
        self.render(template, form=self.form, NEW_INLET=self.NEW_INLET,
                    inter_bank=self.bk_profile,
                    ALI_0_RATE=self.ALI_0_RATE, WX_0_RATE=self.WX_0_RATE, OPEN_DINE=self.open_dine,
                    error_inlet_info_html=error_inlet_info_html, OPEN_D0=self.open_d0, h5=self.h5, jd_pay=self.jd_pay)

    def add_filed(self):
        keys = ['WX', 'WX_OFFLINE', 'WX_ONLINE', 'WX_DINE', 'WX_ZERO', 'WX_D0', 'WX_D1',
                'ALI', 'ALI_D1', 'ALI_D0', 'ALI_ZERO', 'ALI_OFFLINE', 'JD']
        for key in keys:
            setattr(self.form, key, '')
        for payment_type in AVAILABLE_PAYMENTS.keys():
            payment_rate = getattr(self.form, payment_type).data
            if payment_rate >= 0:
                self.validate_rate = True
                # 方便前端显示，添加一些字段
                # 支付通道判断
                if payment_type.startswith('WX'):
                    setattr(self.form, 'WX', True)
                    # 通道判断
                    if payment_type.startswith('WX_OFFLINE'):
                        self.has_wx_offline = True
                        setattr(self.form, 'WX_OFFLINE', True)
                    elif payment_type.startswith('WX_ONLINE'):
                        self.has_wx_online = True
                        setattr(self.form, 'WX_ONLINE', True)
                    elif payment_type.startswith('WX_DINE'):
                        setattr(self.form, 'WX_DINE', True)
                    elif payment_type.startswith('WX_ZERO'):
                        setattr(self.form, 'WX_ZERO', True)

                    # 结算方式判断
                    if payment_type.endswith('D0'):
                        self.has_wx_d0 = True
                        # setattr(self.form, 'WX_D0', True)
                    else:
                        setattr(self.form, 'WX_D1', True)
                elif payment_type.startswith('ALI'):
                    setattr(self.form, 'ALI', True)
                    self.has_ali_payment = True
                    if payment_type.startswith('ALI_OFFLINE'):
                        setattr(self.form, 'ALI_OFFLINE', True)
                    elif payment_type.startswith('ALI_ZERO'):
                        setattr(self.form, 'ALI_ZERO', True)
                    if payment_type.endswith('D0'):
                        self.has_ali_d0 = True
                        # setattr(self.form, 'ALI_D0', True)
                    else:
                        setattr(self.form, 'ALI_D1', True)
                elif payment_type.startswith('JD'):
                    setattr(self.form, 'JD', True)

        if self.wx_draw_fee or self.wx_draw_rate:
            setattr(self.form, 'WX_D0', True)
        if self.ali_draw_fee or self.ali_draw_rate:
            setattr(self.form, 'ALI_D0', True)

    @gen.coroutine
    @authenticated
    @check_permission
    def post(self):
        template = 'official/inlet/distributorAdd.html' if FEATURE_SWITCH.get(
            'NEW_INLET') else 'official/inlet/old_distributorAdd.html'
        self.form.imgCardFront.raw_data = self.request.files.get(
            'imgCardFront', None)
        self.form.imgCardBack.raw_data = self.request.files.get(
            'imgCardBack', None)
        self.form.licenseImg.raw_data = self.request.files.get(
            'licenseImg', None)
        # self.form.img_with_id_card.raw_data = self.request.files.get(
        #     'img_with_id_card', None)

        self.u_ind_code = self.form.jobType.data
        if self.u_ind_code:
            self.industry_name = self.get_industry_name()
            setattr(self.form, 'industryName', self.industry_name)
            area, cmbProvince, cmbCity, cmbArea = (
                self.industry_name).split('-')
            self.form.area.data = area
            self.form.cmbProvince.data = cmbProvince
            self.form.cmbCity.data = cmbCity
            self.form.cmbArea.data = cmbArea

        self.bank_no = self.form.bankNo.data
        if self.bank_no:
            bankName = self.get_bank_name()
            setattr(self.form, 'bankName', bankName)

        self.wx_channel_id = self.form.wxChannelId.data
        self.wx_app_channel_id = self.form.wxAppChannelId.data
        # 提现手续费
        self.wx_draw_fee = self.ali_draw_fee = None
        if self.form.wx_draw_fee.data:
            self.wx_draw_fee = self.form.wx_draw_fee.data
        elif self.form.wx.data:
            self.wx_draw_fee = self.form.wx.data
        if self.form.ali_draw_fee.data:
            self.ali_draw_fee = self.form.ali_draw_fee.data
        elif self.form.alipay.data:
            self.ali_draw_fee = self.form.alipay.data
        # 提现垫资费
        self.wx_draw_rate = self.form.wx_draw_rate.data
        self.ali_draw_rate = self.form.ali_draw_rate.data

        # 新版的手续费和垫资费，两个都为空或者两个都不为空
        if FEATURE_SWITCH.get('NEW_INLET'):
            if (self.wx_draw_fee and not self.wx_draw_rate) or (not self.wx_draw_fee and self.wx_draw_rate):
                self.form.errors['wx_draw_fee'] = [u'微信D0垫资费率不能只填一项']
            if (self.ali_draw_fee and not self.ali_draw_rate) or (not self.ali_draw_fee and self.ali_draw_rate):
                self.form.errors['ali_draw_fee'] = [u'支付宝D0垫资费率不能只填一项']

        self.validate_rate = False
        self.has_wx_offline = False
        self.has_wx_online = False
        self.has_wx_d0 = False
        self.has_ali_d0 = False

        self.add_filed()

        if not self.validate_rate:
            self.form.errors['checkItem'] = [u'费率不能为空']
        if not self.wx_channel_id and self.has_wx_offline:
            self.form.errors['wxChannelId'] = [u'微信线下渠道号不能为空']
        if not self.wx_app_channel_id and self.has_wx_online:
            self.form.errors['wxAppChannelId'] = [u'微信线上渠道号不能为空']
        if not self.wx_app_channel_id and self.has_wx_online:
            self.form.errors['wxAppChannelId'] = [u'微信线上渠道号不能为空']
        if not self.wx_draw_fee and self.has_wx_d0:
            self.form.errors['wx_draw_fee'] = [u'微信提现手续费异常']
        if not self.ali_draw_fee and self.has_ali_d0:
            self.form.errors['ali_draw_fee'] = [u'支付宝提现手续费异常']

        # if not (
        #         self.form.checkItem1.data >= 0 or
        #         self.form.checkItem2.data >= 0 or
        #         self.form.checkItem3.data >= 0 or
        #         self.form.checkItem4.data >= 0 or
        #         self.form.checkItem5.data >= 0 or
        #         self.form.checkItem7.data >= 0 or
        #         self.form.checkItem8.data >= 0 or
        #         self.form.checkItem9.data >= 0 or
        #         self.form.checkItem11.data >= 0 or
        #         self.form.checkItem12.data >= 0 or
        #         self.form.checkItem13.data >= 0):
        #     self.form.errors['checkItem'] = [u'费率不能为空']

        # 判断有没有微信0费率
        data1 = self.form.checkItem1.data
        data2 = self.form.checkItem2.data
        data3 = self.form.checkItem3.data
        wx_zero_payments = [(data is not None and data == 0)
                            for data in [data1, data2, data3]]

        # 说明是微信0费率
        has_wx_d0_rate = self.is_has_d0_rate("wx")
        if has_wx_d0_rate and True in wx_zero_payments:
            self.form.errors['checkItem'] = [u'微信0费率渠道商，不支持开通微信D0结算']

        # 判断有没有支付宝0费率
        data7 = self.form.checkItem7.data
        data8 = self.form.checkItem8.data
        data9 = self.form.checkItem9.data
        ali_zero_payments = [(data is not None and data == 0)
                             for data in [data7, data8, data9]]

        # 说明是支付宝0费率
        has_ali_d0_rate = self.is_has_d0_rate('ali')
        if has_ali_d0_rate and True in ali_zero_payments:
            self.form.errors['checkItem'] = [u'支付宝0费率渠道商，不支持开通支付宝D0结算']

        # if not self.wx_channel_id and (
        #         self.form.checkItem1.data >= 0 or self.form.checkItem2.data >= 0 or self.form.checkItem3.data >= 0):
        #     self.form.errors['wxChannelId'] = [u'微信渠道号不能为空']
        #
        # if not self.wx_app_channel_id and (self.form.checkItem4.data >= 0 or self.form.checkItem5.data >= 0):
        #     self.form.errors['wxAppChannelId'] = [u'微信APP渠道号不能为空']

        if self.form.checkItem33.data is not None and self.form.unionpay_id.data is None:
            self.form.errors['unionpay_id'] = [u'银联机构号不能为空']

        self.alipay_pid = self.form.alipay_pid.data
        if self.has_ali_payment and not self.alipay_pid:
            self.form.errors['alipay_pid'] = [u'请填入支付宝PID']

        if self.form.errors or not self.form.validate():
            error_inlet_info_html = self.render_string(
                'common/error_inlet_add_info.html', data=self.form)
            self.render(template, form=self.form, NEW_INLET=self.NEW_INLET,
                        inter_bank=self.bk_profile,
                        ALI_0_RATE=self.ALI_0_RATE, WX_0_RATE=self.WX_0_RATE, OPEN_DINE=self.open_dine,
                        error_inlet_info_html=error_inlet_info_html, OPEN_D0=self.open_d0, h5=self.h5,
                        jd_pay=self.jd_pay)
            # self.finish()
            return

        self.dt_id = common.create_dt_id()
        self.dt_type = self.form.dtType.data
        self.email = self.form.email.data
        self.dt_name = self.form.dtName.data
        self.province = self.form.province.data
        self.city = self.form.city.data
        self.district = self.form.district.data
        self.address = self.form.address.data
        self.servicePhone = self.form.servicePhone.data
        self.mobile = self.form.mobile.data
        self.wx_channel_id = self.form.wxChannelId.data
        self.wx_app_channel_id = self.form.wxAppChannelId.data
        # 银联号
        self.unionpay_id = self.form.unionpay_id.data
        self.bankType = self.form.bankType.data
        self.bk_id = self.form.bk_id.data
        self.license_num = self.form.licenseNum.data
        self.license_start_date = self.form.licenseStartDate.data
        self.license_period = self.form.licensePeriod.data
        if self.license_period:
            self.license_period = 2
        else:
            self.license_period = 1
        if self.license_period == 1:
            self.license_end_date = self.form.licenseEndDate.data
        else:
            self.license_end_date = None
        self.license_scope = self.form.licenseScope.data

        self.balance_type = self.form.balanceType.data
        self.contact = self.form.contact.data
        self.balance_name = self.form.balanceName.data
        self.balance_account = self.form.balanceNo.data
        self.id_card_no = self.form.idCard.data

        imgFrontFile = self.request.files.get('imgCardFront')
        imgBackFile = self.request.files.get('imgCardBack')
        licenceImgFile = self.request.files.get('licenseImg')
        self.id_card_img_f = self.save_idCard_img(imgFrontFile)
        self.id_card_img_b = self.save_idCard_img(imgBackFile)
        self.license_img = self.save_idCard_img(licenceImgFile)

        # 验证D0合法性
        # wx_alipay = form_verify.verification_d0(self)
        #
        # if not wx_alipay:
        #     error_inlet_info_html = self.render_string(
        #         'common/error_inlet_add_info.html', data=self.form)
        #     self.render('official/inlet/distributorAdd.html', form=self.form, NEW_INLET=self.NEW_INLET,
        #                 inter_bank=self.bk_profile,
        #                 error_inlet_info_html=error_inlet_info_html, OPEN_D0=self.open_d0, h5=self.h5)
        #     return
        # wx_alipay = form_verify.verification_d0(self)
        #
        # if not wx_alipay:
        #     error_inlet_info_html = self.render_string(
        #         'common/error_inlet_add_info.html', data=self.form)
        #     self.render('official/inlet/distributorAdd.html', form=self.form, inter_bank=self.bk_profile,
        #                 error_inlet_info_html=error_inlet_info_html, OPEN_D0=self.open_d0, h5=self.h5, jd_pay=self.jd_pay)
        #     return

        self._password = yield common.bcrypt_pwd(str(self.mobile))

        with self.db.get_db() as cur:
            yield self.create_dt_user(cur)
            yield self.save_inlet_info(cur)
            if self.wx_draw_fee is not None or self.ali_draw_fee is not None:
                yield self.save_d0_withdraw_fee(cur)
            yield self.save_balance_payment(cur)
            yield self.add_auth_inlet_info(cur)
            yield generate_employee_profile.employee_profile("dt", self.dt_id,
                                                             self.email, self._password,
                                                             self.dt_name, self.mobile,
                                                             city=self.city, sex=None)
        self.redirect('/official/inlet/dt')

    def get_industry_name(self):
        query = """select industry_name from industry_uline_info where industry_code=%s;"""
        ret = self.db.selectSQL(query, (self.u_ind_code,))
        industry_name = ret[0] if ret else ''
        return industry_name

    def get_bank_name(self):
        query = """select bank_name from balance_bank_info where bank_no=%s;"""
        ret = self.db.selectSQL(query, (self.bank_no,))
        bank_name = ret[0] if ret else ''
        return bank_name

    def save_idCard_img(self, imgFile):
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

    @gen.coroutine
    def create_dt_user(self, cursor):
        # 新建一个商户,默认密码123456
        # _password = yield common.bcrypt_pwd(str(self.mobile))
        status = 1  # 创建
        create_at = update_at = common.timestamp_now()
        mch_pay_key = common.gen_randown_mch_pkey(32)
        wx_is_0_fee = (
            self.form.checkItem1.data == Decimal(0)
        ) or (
            self.form.checkItem2.data == Decimal(0)
        ) or (self.form.checkItem3.data == Decimal(0))
        if wx_is_0_fee:
            rate = 1  # 0费率分类为1
        else:
            rate = 3  # 默认费率分类为3: 2/1000
        cursor.execute(
            """
            INSERT INTO dt_user(
            dt_id, dt_name, email, password, status,
            create_at, update_at, mch_pay_key, rate)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""",
            (
                self.dt_id, self.dt_name, self.email, self._password, status,
                create_at, update_at, mch_pay_key, rate
            )
        )

    @gen.coroutine
    def get_wx_ali_ind_code(self, cursor):
        query = """select wx_ind_code, ali_ind_code from industry_uline_info where industry_code=%s;"""
        cursor.execute(query, (self.u_ind_code,))
        ret = cursor.fetchone()
        raise gen.Return(ret)

    @gen.coroutine
    def save_d0_withdraw_fee(self, cursor):
        # 数据库只能存int
        wx = self.wx_draw_fee * 100 if self.wx_draw_fee else self.wx_draw_fee
        alipay = self.ali_draw_fee * 100if self.ali_draw_fee else self.ali_draw_fee
        query = """insert into d0_withdraw_fee(role, role_type, wx, alipay) values(%s,%s,%s,%s)"""
        cursor.execute(query, (self.dt_id, 'dt', wx, alipay))

    @gen.coroutine
    def save_inlet_info(self, cursor):
        # 添加的商户的基本信息,下一步保存支付信息
        auth_status = 1
        activated_status = 1
        create_at = update_at = common.timestamp_now()
        province = self.province
        # province = self.province.split('-')[1]
        city = self.city
        # city = self.city.split('-')[1]
        bk_id = DEFAULT_BANK_ID if self.form.bankType.data in [1, "1"] else self.form.bk_id.data
        ret_code = yield self.get_wx_ali_ind_code(cursor)
        wx_ind_code, ali_ind_code = ret_code[0], ret_code[1]
        cursor.execute(
            """
            INSERT INTO dt_inlet_info(
            dt_id, dt_name, dt_type, province, city,district, address,
            contact, mobile, service_phone, email, id_card_img_f,
            id_card_img_b, auth_status, activated_status,
            u_ind_code, wx_ind_code, ali_ind_code, create_at, update_at,
            license_num,
            license_start_date, license_end_date,
            license_period,
            license_scope, license_img,wx_channel_id, wx_app_channel_id, unionpay_id, bk_id, alipay_pid
            )
            VALUES (
            %s, %s, %s, %s, %s, %s,%s,
            %s, %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s,
            %s, %s,
            %s, %s, %s, %s, %s,%s,%s,%s
            )""",
            (
                self.dt_id, self.dt_name, self.dt_type, province, city, self.district, self.address,
                self.contact, self.mobile, self.servicePhone, self.email, self.id_card_img_f,
                self.id_card_img_b, auth_status, activated_status,
                self.u_ind_code, wx_ind_code, ali_ind_code, create_at, update_at,
                self.license_num,
                self.license_start_date, self.license_end_date,
                self.license_period, self.license_scope, self.license_img, self.wx_channel_id, self.wx_app_channel_id,
                self.unionpay_id, bk_id, self.alipay_pid
            )
        )

    @gen.coroutine
    def save_balance_payment(self, cursor):
        # 转成分
        wx_draw_fee = self.wx_draw_fee * 100 if self.wx_draw_fee else ''
        ali_draw_fee = self.ali_draw_fee * 100 if self.ali_draw_fee else ''

        wx_draw_rate = self.wx_draw_rate * 10 if self.wx_draw_rate else ''
        ali_draw_rate = self.ali_draw_rate * 10 if self.ali_draw_rate else ''

        # 商户结算账户表(mch_balance)
        # 商户支付方式表(mch_payment)
        create_at = update_at = common.timestamp_now()
        cursor.execute("""
            INSERT INTO dt_balance(
            dt_id, balance_way, balance_type, balance_name, bank_no, balance_account, id_card_no, create_at, update_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                       (self.dt_id, 1, self.balance_type, self.balance_name,
                        self.bank_no, self.balance_account, self.id_card_no, create_at, update_at))

        use_old_payment_type = False
        # 支持多种支付类型 万分率
        for payment_type in PAY_TYPES:
            payment_rate = getattr(
                self.form, 'checkItem' + str(payment_type)).data
            if payment_rate >= 0:
                use_old_payment_type = True
                tmp_str = translate_payment_type.get(payment_type)
                uline_payment_id, uline_settle_id, trade_type,\
                    thirdparty_mch_id, uline_payment_code = tmp_str.split('|')
                cursor.execute("""
                    INSERT INTO dt_payment(
                    dt_id, settle_rate, uline_payment_id, uline_payment_code, uline_settle_id, trade_type,
                    payment_type, payment_rate, activated_status, create_at, update_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                               (self.dt_id, payment_rate * 10, uline_payment_id, uline_payment_code, uline_settle_id,
                                trade_type, payment_type, payment_rate * 10, 1, create_at, update_at))
        # 保存新的费率
        if not use_old_payment_type:
            for payment_type in AVAILABLE_PAYMENTS.keys():
                payment_rate = getattr(self.form, payment_type).data
                if payment_rate >= 0:
                    old_paymnet_type = new_payment_relations.get(payment_type)
                    # 判断d0 or d1
                    if payment_type.endswith('D0'):
                        uline_settle_id = 2
                        payment_type = payment_type[:-3]
                    else:
                        uline_settle_id = 1
                    # 保存手续费和垫资费
                    if payment_type.startswith('WX'):
                        draw_fee = wx_draw_fee if wx_draw_fee else ''
                        draw_rate = wx_draw_rate if wx_draw_rate else ''
                    else:
                        draw_fee = ali_draw_fee if ali_draw_fee else ''
                        draw_rate = ali_draw_rate if ali_draw_rate else ''
                    data = self.get_payment_info(payment_type, cursor)
                    if draw_fee and draw_rate:
                        cursor.execute("""
                        INSERT INTO dt_payment(
                    dt_id, settle_rate, uline_payment_id, uline_payment_code, uline_settle_id, trade_type,
                    payment_type, payment_rate, withdraw_rate, withdraw_fee, activated_status, create_at, update_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                                       (self.dt_id, payment_rate * 10, data.get('uline_payment_id'),
                                        data.get('uline_payment_code'), uline_settle_id,
                                        data.get('trade_type'), old_paymnet_type,
                                        payment_rate * 10, draw_rate, draw_fee, 1,
                                        create_at, update_at))
                    else:
                        cursor.execute("""
                        INSERT INTO dt_payment(
                    dt_id, settle_rate, uline_payment_id, uline_payment_code, uline_settle_id, trade_type,
                    payment_type, payment_rate, activated_status, create_at, update_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                                       (self.dt_id, payment_rate * 10, data.get('uline_payment_id'),
                                        data.get('uline_payment_code'), uline_settle_id,
                                        data.get('trade_type'), old_paymnet_type,
                                        payment_rate * 10, 1,
                                        create_at, update_at))

    def get_payment_info(self, payment_type, cursor):
        query = """select id, payment_code, trade_type from uline_payment where payment_code=%s"""
        cursor.execute(query, (payment_type,))
        ret = cursor.fetchone()
        fields = ['uline_payment_id', 'uline_payment_code', 'trade_type']
        data = dict(zip(fields, ret))
        return data

    @gen.coroutine
    def add_auth_inlet_info(self, cursor):
        auth_user = yield self.get_official_user(cursor)
        create_at = common.timestamp_now()
        query = """
            insert into auth_dt_info (dt_id, comment, auth_user, auth_status, create_at)
            values (%s, %s, %s, %s, %s);"""
        cursor.execute(query, (self.dt_id, u'提交审核', auth_user, 1, create_at))

    @gen.coroutine
    def get_official_user(self, cursor):
        query = """select ub_name from ub_user where ub_id=%s"""
        cursor.execute(query, (self.current_user,))
        ret = cursor.fetchone()
        raise gen.Return(ret[0])

    def is_has_d0_rate(self, rate_type):
        if rate_type == 'wx':
            if (
                self.form.checkItem101.data is not None or
                self.form.checkItem102.data is not None or
                self.form.checkItem103.data is not None or
                self.form.checkItem104.data is not None
            ):
                return True
        elif rate_type == 'ali':
            if (
                self.form.checkItem107.data is not None or
                self.form.checkItem108.data is not None or
                self.form.checkItem109.data is not None
            ):
                return True
        return False
