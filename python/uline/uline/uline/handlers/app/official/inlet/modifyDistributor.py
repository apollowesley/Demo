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
from uline.model.uline.base import uline_session
from uline.model.uline.user import BkUser
import os
from tornado import gen
from tornado.web import authenticated, asynchronous
from uline.settings import DEFAULT_BANK_ID
from uline.handlers.baseHandlers import OfclAdminHandler
from uline.public import common
from uline.public.constants import PAYMENT, old_payment_relations, AVAILABLE_PAYMENTS
from uline.utils.record import record_utils
from uline.public.constants import PAY_TYPES, BANK_TYPE
from .form import ModifyDistributorlnlet
from datetime import datetime, date
from decimal import Decimal
from uline.settings import FEATURE_SWITCH
from uline.utils.dayzero import form_verify
from uline.public.permit import check_permission


class ModifyDistributorInletHandler(OfclAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        self.open_d0 = FEATURE_SWITCH.get('OPEN_D0')
        # 是否支持h5支付
        self.h5 = FEATURE_SWITCH.get('H5')
        self.jd_pay = FEATURE_SWITCH.get('JD_PAY')
        self.open_dine = FEATURE_SWITCH.get('DINE_TOGETHER')
        self.WX_0_RATE = FEATURE_SWITCH.get('0_RATE')
        self.ALI_0_RATE = FEATURE_SWITCH.get('ALI_0_RATE')
        self.NEW_INLET = FEATURE_SWITCH.get('NEW_INLET')
        self.form = ModifyDistributorlnlet(self)
        if self.request.files.get('imgCardFront'):
            self.form.imgCardFront.raw_data = self.request.files.get(
                'imgCardFront', None)
        if self.request.files.get('imgCardBack'):
            self.form.imgCardBack.raw_data = self.request.files.get(
                'imgCardBack', None)
        if self.request.files.get('licenseImg'):
            self.form.licenseImg.raw_data = self.request.files.get(
                'licenseImg', None)

        # if self.u_ind_code:
        #     self.industry_name = self.get_industry_name()
        #     setattr(self.form, 'industryName', self.industry_name)
        self.bk_profile = uline_session.query(BkUser.bk_id, BkUser.bk_name).filter(BkUser.bk_type == 2).all()
        self.bank_no = self.form.bankNo.data
        if self.bank_no:
            bankName = self.get_bank_name()
            setattr(self.form, 'bankName', bankName)

        self.has_ali_payment = False
        self.dt_id = self.form.dt_id.data
        self.wx_channel_id, self.wx_app_channel_id, self.unionpay_id = self.get_wx_channel_id()
        self.has_been_authed = self.has_authed()
        self.bankType = self.form.bankType.data
        # self.bk_id = self.form.bk_id.data
        self.u_ind_code = self.form.jobType.data
        with self.db.get_db() as cursor:
            self.dt_infos = self.get_uline_dt_infos(cursor)

        if not self.u_ind_code and self.dt_infos:
            self.industry_name = self.dt_infos[3]
            self.form.jobType.data = self.dt_infos[0]
            self.u_ind_code = self.dt_infos[0]
            if self.industry_name:
                setattr(self.form, 'industryName', self.industry_name)
                area, cmbProvince, cmbCity, cmbArea = (
                    self.industry_name).split('-')
                self.form.area.data = area
                self.form.cmbProvince.data = cmbProvince
                self.form.cmbCity.data = cmbCity
                self.form.cmbArea.data = cmbArea

        self.dt_name = self.form.dtName.data
        if not self.dt_name and self.dt_infos:
            self.dt_name = self.dt_infos[1]
            self.form.dtName.data = self.dt_name

        self.dt_type = self.form.dtType.data
        if not self.dt_type and self.dt_infos:
            self.dt_type = self.dt_infos[2]
            self.form.dtType.data = self.dt_type

        self.use_dine = True if self.form.use_dine.data else False
        default_dine_value = 0 if self.open_dine and self.use_dine else None
        self.form.checkItem11.data = default_dine_value
        self.form.checkItem12.data = default_dine_value
        self.form.checkItem13.data = default_dine_value

        self.bk_type = self.get_dt_bank_type()

        self.template = 'official/inlet/distributorModify.html' if FEATURE_SWITCH.get(
            'NEW_INLET') else 'official/inlet/old_distributorModify.html'

    def has_authed(self):
        query = """select 1 from auth_dt_info where dt_id=%s and auth_status=2;"""
        result = self.db.selectSQL(query, (self.dt_id,))
        return bool(result)

    def get_dt_bank_type(self):
        sql = """
            select bk_type from bk_user left join
            dt_inlet_info on dt_inlet_info.bk_id = bk_user.bk_id
            where dt_inlet_info.dt_id=%s
        """
        ret = self.db.selectSQL(sql, (self.dt_id,))
        if ret:
            if isinstance(ret, tuple):
                return ret[0]
        else:
            return BANK_TYPE.get("main")

    @asynchronous
    @gen.coroutine
    def get(self):
        # 更新老的费率字段
        # self.update_old_payment()
        # 以下字段经常出现特殊字符，暂时先后台直接给出，不需要前端拼接url
        ret = self.get_dt_license_scope_and_address()
        self.form.dtName.data = ret.get('dt_name')
        self.form.address.data = ret.get('address')
        self.form.idCard.data = ret.get('id_card_no')
        self.form.licenseScope.data = ret.get('license_scope')
        self.form.balanceName.data = ret.get('balance_name')

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

        self.add_field()
        error_inlet_info_html = self.render_string(
            'common/error_inlet_add_info.html', data=self.form)
        self.render(self.template, form=self.form,
                    rate_error=False, OPEN_D0=self.open_d0,
                    h5=self.h5, inter_bank=self.bk_profile,
                    bk_type=self.bk_type,
                    error_inlet_info_html=error_inlet_info_html, wx_channel_id=self.wx_channel_id,
                    has_been_authed=self.has_been_authed,
                    ALI_0_RATE=self.ALI_0_RATE, WX_0_RATE=self.WX_0_RATE,
                    OPEN_DINE=self.open_dine,
                    jd_pay=self.jd_pay,
                    unionpay_id=self.unionpay_id,
                    wx_app_channel_id=self.wx_app_channel_id)

    def update_old_payment(self):
        for payment_type in PAY_TYPES:
            payment_rate = getattr(
                self.form, 'checkItem' + str(payment_type)).data
            if payment_rate >= 0 and payment_type not in [11, 12, 13]:
                payment_code = old_payment_relations.get(payment_type)
                setattr(self.form, payment_code, payment_rate)

    def add_field(self):
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

    def generate_unchanged_render_params(self):
        return {
            'form': self.form,
            'OPEN_D0': self.open_d0,
            'has_been_authed': self.has_been_authed,
            'wx_channel_id': self.wx_channel_id,
            'wx_app_channel_id': self.wx_app_channel_id,
            'use_dine': self.open_dine and self.use_dine,
            'open_dine': self.open_dine,
        }

    @asynchronous
    @gen.coroutine
    def post(self):
        rate_error = False
        self.license_period = self.form.licensePeriod.data
        if self.license_period:
            self.form.licensePeriod.data = '2'
        self.wx_channel_id = self.form.wxChannelId.data
        self.wx_app_channel_id = self.form.wxAppChannelId.data
        self.wx_draw_fee = self.form.wx_draw_fee.data
        self.ali_draw_fee = self.form.ali_draw_fee.data

        self.validate_rate = False
        self.has_wx_offline = False
        self.has_wx_online = False
        self.has_wx_d0 = False
        self.has_ali_d0 = False

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

        self.add_field()
        self.unionpay_id = self.form.unionpay_id.data

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
        #         self.form.checkItem13.data >= 0
        # ):

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
            self.form.errors['alipay_pid'] = [u"支付宝PID不能为空"]

        if self.form.errors or not self.form.validate():
            error_inlet_info_html = self.render_string(
                'common/error_inlet_add_info.html', data=self.form)
            self.render(self.template, form=self.form,
                        error_inlet_info_html=error_inlet_info_html,
                        has_been_authed=self.has_been_authed,
                        wx_channel_id=self.wx_channel_id,
                        wx_app_channel_id=self.wx_app_channel_id,
                        unionpay_id=self.unionpay_id,
                        OPEN_D0=self.open_d0,
                        h5=self.h5, inter_bank=self.bk_profile,
                        ALI_0_RATE=self.ALI_0_RATE, WX_0_RATE=self.WX_0_RATE,
                        OPEN_DINE=self.open_dine,
                        bk_type=self.bk_type,
                        jd_pay=self.jd_pay,
                        rate_error=rate_error)
            # self.finish()
            return

        # 判断费率是否调整到高于下边商户费率
        force_update = self.form.force_update.data
        rate_error = False
        if not force_update:
            # result = self.checkout_dt_payment_rate()
            result = self.checkout_new_dt_payment_rate()
            if result:
                self.form.errors['checkItem'] = [u'渠道费率%s设置高于旗下部分商户费率值。修改并审核通过后，将同步调升该部分商户费率到渠道成本费' %
                                                 '、'.join(PAYMENT[str(i)] for i in result)]
                rate_error = True

        if not force_update:
            if self.NEW_INLET:
                wx_result, ali_result = self.new_check_dt_d0_with_draw_fee()
                if not wx_result:
                    self.form.errors['wx_draw_fee'] = [
                        u'渠道微信D0代付费用高于部分商户D0提现手续费：修改并审核通过后，将同步调升这部分商户D0代付费用到渠道成本手续费。']
                    rate_error = True
                if not ali_result:
                    self.form.errors['ali_draw_fee'] = [
                        u'渠道支付宝D0代付费用高于部分商户D0提现手续费：修改并审核通过后，将同步调升这部分商户D0代付费用到渠道成本手续费。']
                    rate_error = True

                wx_draw_rate, ali_draw_rate = self.check_dt_d0_with_draw_rate()
                if not wx_draw_rate:
                    self.form.errors['wx_draw_rate'] = [
                        u'渠道微信D0垫资费率高于部分商户D0垫资费率：修改并审核通过后，将同步调升该部分商户D0垫资费率到渠道成本费率。']
                    rate_error = True
                if not ali_draw_rate:
                    self.form.errors['ali_draw_rate'] = [
                        u'渠道支付宝D0垫资费率高于部分商户D0垫资费率：修改并审核通过后，将同步调升该部分商户D0垫资费率到渠道成本费率。']
                    rate_error = True
            else:
                wx_result, ali_result = self.check_dt_d0_with_draw_fee()
                if not wx_result:
                    self.form.errors['wx_draw_fee'] = [
                        u'渠道微信D0提现手续费高于部分商户D0提现手续费：修改并审核通过后，将同步调升这部分商户D0提现手续费到渠道成本手续费。']
                    rate_error = True
                if not ali_result:
                    self.form.errors['ali_draw_fee'] = [
                        u'渠道支付宝D0提现手续费高于部分商户D0提现手续费：修改并审核通过后，将同步调升这部分商户D0提现手续费到渠道成本手续费。']
                    rate_error = True

        if self.form.errors:
            # 费率错误的详细信息目前没有需求，怕以后有需求，留着吧 ┑(￣Д ￣)┍
            error_inlet_info_html = self.render_string(
                'common/error_inlet_add_info.html', data=self.form)
            self.render(self.template, form=self.form,
                        error_inlet_info_html=error_inlet_info_html,
                        has_been_authed=self.has_been_authed,
                        wx_channel_id=self.wx_channel_id,
                        wx_app_channel_id=self.wx_app_channel_id,
                        unionpay_id=self.unionpay_id,
                        OPEN_D0=self.open_d0,
                        h5=self.h5, inter_bank=self.bk_profile,
                        ALI_0_RATE=self.ALI_0_RATE, WX_0_RATE=self.WX_0_RATE,
                        OPEN_DINE=self.open_dine,
                        bk_type=self.bk_type,
                        jd_pay=self.jd_pay,
                        rate_error=rate_error)
            # self.finish()
            return

        self.dt_id = self.form.dt_id.data
        self.email = self.form.email.data
        self.dt_name = self.form.dtName.data
        self.dt_type = self.form.dtType.data

        self.province = self.form.province.data
        self.city = self.form.city.data
        self.district = self.form.district.data
        self.address = self.form.address.data
        self.servicePhone = self.form.servicePhone.data
        self.mobile = self.form.mobile.data

        self.license_num = self.form.licenseNum.data
        self.license_start_date = self.form.licenseStartDate.data
        self.license_end_date = self.form.licenseEndDate.data
        if self.license_period:
            self.license_period = 2
        else:
            self.license_period = 1
        self.license_scope = self.form.licenseScope.data

        self.balance_type = self.form.balanceType.data
        self.contact = self.form.contact.data
        self.balance_name = self.form.balanceName.data
        self.balance_account = self.form.balanceNo.data
        self.id_card_no = self.form.idCard.data

        imgFrontFile = self.request.files.get('imgCardFront')
        imgBackFile = self.request.files.get('imgCardBack')
        licenceImgFile = self.request.files.get('licenseImg')
        # img_with_id_card = self.request.files.get('img_with_id_card')

        self.id_card_img_f = self.save_idCard_img(imgFrontFile) if imgFrontFile else \
            self.form.imgCardFrontOld.data.split('/')[6]
        self.id_card_img_b = self.save_idCard_img(imgBackFile) if imgBackFile else \
            self.form.imgCardBackOld.data.split('/')[6]
        self.license_img = self.save_idCard_img(licenceImgFile) if licenceImgFile else \
            self.form.licenseImgOld.data.split('/')[6]
        # self.img_with_id_card = self.save_idCard_img(img_with_id_card) if img_with_id_card else \
        #     self.form.img_with_id_cardOld.data.split('/')[6]

        # 存储修改信息到 变更记录表
        self.change_dict = {}

        # 验证D0合法性
        # wx_alipay = form_verify.verification_d0(self)
        #
        # if not wx_alipay:
        #     error_inlet_info_html = self.render_string(
        #         'common/error_inlet_add_info.html', data=self.form)
        #     self.render('official/inlet/distributorModify.html', form=self.form,
        #                 h5=self.h5,
        #                 bk_type=self.bk_type,
        #                 error_inlet_info_html=error_inlet_info_html,
        #                 wx_channel_id=self.wx_channel_id,
        #                 wx_app_channel_id=self.wx_app_channel_id,
        #                 OPEN_D0=self.open_d0, inter_bank=self.bk_profile,
        #                 has_been_authed=self.has_been_authed,
        #                 rate_error=True if rate_error else False)
        #     return
        # wx_alipay = form_verify.verification_d0(self)
        #
        # if not wx_alipay:
        #     error_inlet_info_html = self.render_string(
        #         'common/error_inlet_add_info.html', data=self.form)
        #     self.render('official/inlet/distributorModify.html', form=self.form,
        #                 h5=self.h5,
        #                 bk_type=self.bk_type,
        #                 error_inlet_info_html=error_inlet_info_html,
        #                 wx_channel_id=self.wx_channel_id,
        #                 wx_app_channel_id=self.wx_app_channel_id,
        #                 OPEN_D0=self.open_d0, inter_bank=self.bk_profile,
        #                 has_been_authed=self.has_been_authed,
        #                 jd_pay=self.jd_pay,
        #                 rate_error=True if rate_error else False)
        #     return
        # wx_alipay = form_verify.verification_d0(self)
        #
        # if not wx_alipay:
        #     error_inlet_info_html = self.render_string(
        #         'common/error_inlet_add_info.html', data=self.form)
        #     self.render('official/inlet/distributorModify.html', form=self.form,
        #                 h5=self.h5,
        #                 bk_type=self.bk_type,
        #                 error_inlet_info_html=error_inlet_info_html,
        #                 wx_channel_id=self.wx_channel_id,
        #                 wx_app_channel_id=self.wx_app_channel_id,
        #                 unionpay_id=self.unionpay_id,
        #                 OPEN_D0=self.open_d0, inter_bank=self.bk_profile,
        #                 has_been_authed=self.has_been_authed,
        #                 jd_pay=self.jd_pay,
        #                 rate_error=True if rate_error else False)
        #     return

        self.auth_status = 1
        self.update_at = common.timestamp_now()

        with self.db.get_db() as cur:
            self.update_inlet_infos = self.get_update_inlet_infos(
                cur, self.update_at, self.auth_status)

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

        if self.form.errors:
            error_inlet_info_html = self.render_string(
                'common/error_inlet_add_info.html', data=self.form)
            self.render(self.template, form=self.form, rate_error=False,
                        h5=self.h5,
                        bk_type=self.bk_type,
                        has_been_authed=self.has_been_authed,
                        wx_app_channel_id=self.wx_app_channel_id,
                        unionpay_id=self.unionpay_id,
                        OPEN_D0=self.open_d0, inter_bank=self.bk_profile,
                        ALI_0_RATE=self.ALI_0_RATE, WX_0_RATE=self.WX_0_RATE,
                        OPEN_DINE=self.open_dine,
                        jd_pay=self.jd_pay,
                        error_inlet_info_html=error_inlet_info_html, wx_channel_id=self.wx_channel_id)
            # self.finish()
            return

        with self.db.get_db() as cur:
            yield self.update_balance_payment(cur)
            # if self.alipay is not None or self.wx is not None:
            yield self.update_d0_withdraw_fee(cur)
            yield self.update_inlet_info(cur)
            self.add_auth_inlet_info(cur)
        if self.change_dict:
            yield self.add_change_record()  # 存储变更信息逻辑结束
        self.redirect('/official/inlet/dt')

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
            if(
                self.form.checkItem107.data is not None or
                self.form.checkItem108.data is not None or
                self.form.checkItem109.data is not None
            ):
                return True
        return False

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
        select_change_record = yield record_utils.select_change_record_by_dt_id(self, fetchone=False)
        if len(select_change_record) == 0:
            # 插入新的数据
            record_utils.insert_change_record(
                self, (self.dt_id, json.dumps(self.change_dict, cls=ComplexEncoder)))
        elif len(select_change_record) == 1:
            # 更新信息
            record_utils.update_change_record(
                self, (json.dumps(self.change_dict, cls=ComplexEncoder), 1, self.dt_id))

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

    def get_wx_ali_ind_code(self, cursor, u_ind_code):
        query = """select wx_ind_code, ali_ind_code,industry_name from industry_uline_info where industry_code=%s and status=1;"""
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
            updates['dt_id'] = self.dt_id
            cursor.execute(sql, updates)
            # cursor.execute(query, query_dt_inlet_info_dict)

    def get_update_inlet_infos(self, cursor, update_at, auth_status):
        try:
            self.province = self.province.split('-')[1]
            # self.province = self.province
            self.city = self.city.split('-')[1]
            # self.city = self.city.split
        except Exception as err:
            print err
        may_update_keys = [
            'dt_name', 'province', 'city', 'district', 'address', 'contact', 'mobile', 'service_phone',
            'email', 'id_card_img_f', 'id_card_img_b', 'dt_id', 'license_num', 'wx_channel_id',
            'license_start_date', 'license_end_date', 'license_period', 'license_scope', 'license_img',
            'wx_app_channel_id', 'unionpay_id', 'dt_type', 'alipay_pid', 'u_ind_code',
        ]
        query_columns = ','.join(may_update_keys)
        query = """select {} from dt_inlet_info where dt_id=%s;""".format(query_columns)
        cursor.execute(query, (self.dt_id,))
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
            'dt_id': self.dt_id,
            'license_num': self.license_num,
            'update_at': update_at,
            'license_start_date': self.license_start_date,
            'license_end_date': self.license_end_date,
            'license_period': self.license_period,
            'license_scope': self.license_scope,
            'license_img': self.license_img,
            'wx_channel_id': self.wx_channel_id,
            'wx_app_channel_id': self.wx_app_channel_id,
            'unionpay_id': self.unionpay_id,
            'u_ind_code': self.u_ind_code,
            'dt_type': self.dt_type,
            'alipay_pid': self.alipay_pid,
        }
        # if self.form.bankType.data in [1, "1"]:
        #     bk_id = DEFAULT_BANK_ID
        # else:
        #     bk_id = self.form.bk_id.data
        # query_dt_inlet_info_dict.update({"bk_id": int(bk_id)})
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
        role = {}
        # 数据库只能存int
        wx_draw_fee = int(self.wx_draw_fee * 100) if self.wx_draw_fee else self.wx_draw_fee
        ali_draw_fee = int(self.ali_draw_fee * 100) if self.ali_draw_fee else self.ali_draw_fee

        wx_draw_rate = int(self.wx_draw_rate * 10) if self.wx_draw_rate else self.wx_draw_rate
        ali_draw_rate = int(self.ali_draw_rate * 10) if self.ali_draw_rate else self.ali_draw_rate
        if wx_draw_fee:
            role['wx_draw_fee'] = wx_draw_fee
        if ali_draw_fee:
            role['ali_draw_fee'] = ali_draw_fee
        if wx_draw_rate:
            role['wx_draw_rate'] = wx_draw_rate
        if ali_draw_rate:
            role['ali_draw_rate'] = ali_draw_rate

        self.change_dict['role'] = role

        # select_query = """
        #     select 1 from d0_withdraw_fee where role=%s and role_type='dt'
        # """
        # cursor.execute(select_query, (self.dt_id,))
        # ret = cursor.fetchone()
        # if ret:
        #     query = """
        #         update d0_withdraw_fee set wx=%s, alipay=%s where role=%s and role_type = %s
        #     """
        #     cursor.execute(query, (wx, alipay, self.dt_id, 'dt'))
        # else:
        #     query = """insert into d0_withdraw_fee(role, role_type, wx, alipay) values(%s,%s,%s,%s)"""
        #     cursor.execute(query, (self.dt_id, 'dt', wx, alipay))

    @gen.coroutine
    def update_balance_payment(self, cursor):
        # 渠道商结算账户表(dt_balance)
        # 渠道商支付方式表(dt_payment)
        sql = """select balance_type,balance_name,bank_no,balance_account,id_card_no from dt_balance where dt_id=%s"""
        cursor.execute(sql, (self.dt_id,))
        balance_in_db = cursor.fetchone()
        need_update_keys = ['balance_type', 'balance_name',
                            'bank_no', 'balance_account', 'id_card_no']
        balance_in_db = dict(zip(need_update_keys, balance_in_db))
        create_at = update_at = common.timestamp_now()

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

        payments = self.get_new_dt_payments(cursor)
        db_paytypes = {}
        self.change_dict['payment'] = {}
        form_paytypes = []
        for payment_type in AVAILABLE_PAYMENTS.keys():
            ret = payments.get(payment_type, None)
            payment_rate = getattr(self.form, payment_type).data
            if payment_rate >= 0:
                payment_rate = float(payment_rate) * 10
                form_paytypes.append(payment_type)
                # query = """select id, activated_status, payment_rate  from dt_payment where dt_id=%s and payment_type=%s"""
                # cursor.execute(query, (self.dt_id, payment_type))
                # ret = cursor.fetchone()

                # 如果支付方式的费率没变，则不需要存储
                exist_pay_rate = 0
                if ret:
                    exist_pay_rate = ret[2]
                    db_paytypes[payment_type] = ret
                if ret and exist_pay_rate == payment_rate:
                    continue

                if 'payment' not in self.change_dict:
                    self.change_dict['payment'] = {}
                if ret:
                    exist_status = ret[1]

                    change_status = 1
                    # 如果没有发生改变，则保持原有状态不变
                    if exist_status == 1:
                        # 如果之前状态为未激活,就应该保持为未激活
                        change_status = 1
                    else:
                        change_status = 3 if payment_rate != exist_pay_rate else exist_status

                    after_auth_status = 1 if payment_rate != exist_pay_rate else exist_status
                    update_info = {
                        'pay_type': payment_type,
                        'pay_rate': payment_rate,
                        'pre_status': exist_status,
                        'is_exist': 1,
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
                        'is_exist': 0,
                        'activated_status': 1,
                        'action_type': 1,  # 1为新增 2为更新 3为删除
                        'after_auth_status': 1,  # 审核通过之后的状态
                    }
                    self.change_dict['payment'][payment_type] = update_info

        to_delete_types = [paytype for paytype in payments if paytype not in form_paytypes]
        # delete_paytype_sql = """DELETE FROM dt_payment where payment_type=%s and dt_id=%s;"""
        for each_payment_type in to_delete_types:
            payment = payments[each_payment_type]
            update_info = {
                'pay_type': each_payment_type,
                'pay_rate': payment[2],
                'pre_status': payment[1],
                'is_exist': 1,
                'activated_status': 1,
                'action_type': 3,  # 1为新增 2为更新 3为删除
                'after_auth_status': 1,  # 审核通过之后的状态
            }
            self.change_dict['payment'][each_payment_type] = update_info

        # payments = self.get_dt_payments(cursor)
        # db_paytypes = {}
        # self.change_dict['payment'] = {}
        # for payment_type in PAY_TYPES:
        #     ret = payments.get(int(payment_type), None)
        #     payment_rate = getattr(
        #         self.form, 'checkItem' + str(payment_type)).data
        #     if payment_rate >= 0:
        #         payment_rate = float(payment_rate) * 10
        #         # query = """select id, activated_status, payment_rate  from dt_payment where dt_id=%s and payment_type=%s"""
        #         # cursor.execute(query, (self.dt_id, payment_type))
        #         # ret = cursor.fetchone()
        #
        #         # 如果支付方式的费率没变，则不需要存储
        #         exist_pay_rate = 0
        #         if ret:
        #             exist_pay_rate = ret[2]
        #             db_paytypes[payment_type] = ret
        #         if ret and exist_pay_rate == payment_rate:
        #             continue
        #
        #         if 'payment' not in self.change_dict:
        #             self.change_dict['payment'] = {}
        #         if ret:
        #             exist_status = ret[1]
        #
        #             change_status = 1
        #             # 如果没有发生改变，则保持原有状态不变
        #             if exist_status == 1:
        #                 # 如果之前状态为未激活,就应该保持为未激活
        #                 change_status = 1
        #             else:
        #                 change_status = 3 if payment_rate != exist_pay_rate else exist_status
        #
        #             after_auth_status = 1 if payment_rate != exist_pay_rate else exist_status
        #             update_info = {
        #                 'pay_type': payment_type,
        #                 'pay_rate': payment_rate,
        #                 'pre_status': exist_status,
        #                 'is_exist': 1,
        #                 'activated_status': change_status,
        #                 'action_type': 2,  # 1为新增 2为更新 3为删除
        #                 'after_auth_status': after_auth_status,
        #             }
        #             self.change_dict['payment'][payment_type] = update_info
        #         else:
        #             update_info = {
        #                 'pay_type': payment_type,
        #                 'pay_rate': payment_rate,
        #                 'pre_status': 1,
        #                 'is_exist': 0,
        #                 'activated_status': 1,
        #                 'action_type': 1,  # 1为新增 2为更新 3为删除
        #                 'after_auth_status': 1,  # 审核通过之后的状态
        #             }
        #             self.change_dict['payment'][payment_type] = update_info
        # to_delete_types = [paytype for paytype in payments if paytype not in db_paytypes]
        # # delete_paytype_sql = """DELETE FROM dt_payment where payment_type=%s and dt_id=%s;"""
        # for each_payment_type in to_delete_types:
        #     payment = payments[each_payment_type]
        #     update_info = {
        #         'pay_type': each_payment_type,
        #         'pay_rate': payment[2],
        #         'pre_status': payment[1],
        #         'is_exist': 1,
        #         'activated_status': 1,
        #         'action_type': 3,  # 1为新增 2为更新 3为删除
        #         'after_auth_status': 1,  # 审核通过之后的状态
        #     }
        #     self.change_dict['payment'][each_payment_type] = update_info

    def add_auth_inlet_info(self, cursor):
        auth_user = self.get_official_user(cursor)
        create_at = common.timestamp_now()
        query = """
                insert into auth_dt_info (dt_id, comment, auth_user, auth_status, create_at)
                values (%s, %s, %s, %s, %s);"""
        cursor.execute(query, (self.dt_id, u'提交修改', auth_user, 1, create_at))

    def get_official_user(self, cursor):
        query = """select ub_name from ub_user where ub_id=%s"""
        cursor.execute(query, (self.current_user,))
        ret = cursor.fetchone()
        return ret[0]

    def get_wx_channel_id(self):
        sql = """select wx_channel_id,wx_app_channel_id, unionpay_id from dt_inlet_info where dt_id=%s;"""
        result = self.db.selectSQL(sql, (self.dt_id,))
        wx_channel_id = ''
        wx_app_channel_id = ''
        unionpay_id = ''
        if result:
            if result[0]:
                wx_channel_id = result[0]
            if result[1]:
                wx_app_channel_id = result[1]
            if result[2]:
                unionpay_id = result[2]

        return wx_channel_id, wx_app_channel_id, unionpay_id

    def checkout_dt_payment_rate(self):
        checkout_payment_rate = {x: self.form.data.get(
            'checkItem' + str(x)) or 0 for x in PAY_TYPES}
        above_rate = []
        for key, payment_rate in checkout_payment_rate.items():
            if not payment_rate:
                continue
            query = """select DISTINCT(dt_payment.payment_type) from mch_payment inner join mch_inlet_info on
                          mch_inlet_info.mch_id = mch_payment.mch_id inner join dt_payment on
                          mch_inlet_info.dt_id = dt_payment.dt_id and dt_payment.payment_type = mch_payment.payment_type
                          where mch_payment.payment_rate < %s and dt_payment.dt_id=%s and
                          dt_payment.payment_type=%s;"""
            result = self.db.selectSQL(
                query, (float(payment_rate) * 10, self.dt_id, key))
            if result:
                above_rate.append(result[0])
        return above_rate

    def checkout_new_dt_payment_rate(self):
        # 新进件费率不在使用数字
        if self.NEW_INLET:
            checkout_payment_rate = {x: self.form.data.get(x) or 0 for x in AVAILABLE_PAYMENTS.keys()}
        else:
            checkout_payment_rate = {x: self.form.data.get(x) or 0 for x in PAY_TYPES}
        above_rate = []
        for uline_payment_code, payment_rate in checkout_payment_rate.items():
            if not payment_rate:
                continue
            if self.NEW_INLET:
                query = """select DISTINCT(dt_payment.payment_type) from mch_payment inner join mch_inlet_info on
                          mch_inlet_info.mch_id = mch_payment.mch_id inner join dt_payment on
                          mch_inlet_info.dt_id = dt_payment.dt_id
                          and dt_payment.uline_payment_code = mch_payment.uline_payment_code
                          where mch_payment.payment_rate < %s and dt_payment.dt_id=%s and
                          dt_payment.uline_payment_code=%s;"""
            else:
                query = """select DISTINCT(dt_payment.payment_type) from mch_payment inner join mch_inlet_info on
                          mch_inlet_info.mch_id = mch_payment.mch_id inner join dt_payment on
                          mch_inlet_info.dt_id = dt_payment.dt_id
                          and dt_payment.uline_payment_code = mch_payment.uline_payment_code
                          where mch_payment.payment_rate < %s and dt_payment.dt_id=%s and
                          dt_payment.payment_type=%s;"""
            result = self.db.selectSQL(
                query, (float(payment_rate) * 10, self.dt_id, uline_payment_code))
            if result:
                above_rate.append(result[0])
        return above_rate

    def force_update_rate(self):
        pass

    def get_uline_dt_infos(self, cursor):
        sql = """select dt_inlet_info.u_ind_code, dt_inlet_info.dt_name, dt_inlet_info.dt_type,
                            industry_uline_info.industry_name
                    from dt_inlet_info
                    INNER JOIN industry_uline_info ON dt_inlet_info.u_ind_code=industry_uline_info.industry_code
                    where dt_inlet_info.dt_id=%s"""
        cursor.execute(sql, (self.dt_id,))
        result = cursor.fetchone()
        return result

    def get_dt_license_scope_and_address(self):
        query = """select dt_inlet_info.dt_name, dt_inlet_info.dt_short_name,
                      dt_inlet_info.address, dt_balance.id_card_no, dt_inlet_info.license_scope,
                      dt_balance.balance_name
                      from dt_inlet_info INNER JOIN dt_balance on dt_balance.dt_id = dt_inlet_info.dt_id
                      WHERE dt_inlet_info.dt_id=%s;
            """
        ret = self.db.selectSQL(query, (self.dt_id,))
        _field = ['dt_name', 'dt_short_name', 'address',
                  'id_card_no', 'license_scope', 'balance_name']
        return {k: v for k, v in zip(_field, ret)}

    def check_dt_d0_with_draw_fee(self):
        sql = """select 1 from d0_withdraw_fee as df1 inner join mch_inlet_info on mch_inlet_info.mch_id = df1.role
                         where mch_inlet_info.dt_id=%s and df1.role_type='mch'
                         and df1.{0}<%s and df1.{0} NOTNULL"""
        ali_valid, wx_valid = True, True
        if self.wx_draw_fee:
            wx_sql = sql.format('wx')
            result = self.db.selectSQL(wx_sql, (self.dt_id, self.wx_draw_fee * 100))
            if result:
                wx_valid = False
        if self.ali_draw_fee:
            alipay_sql = sql.format('alipay')
            result = self.db.selectSQL(
                alipay_sql, (self.dt_id, self.ali_draw_fee * 100))
            if result:
                ali_valid = False
        return wx_valid, ali_valid

    def new_check_dt_d0_with_draw_fee(self):
        ali_valid, wx_valid = True, True
        if self.wx_draw_rate:
            sql = """select 1 from mch_payment WHERE dt_id=%s and
                 withdraw_rate is not NULL and withdraw_fee < %s and payment_type in (1, 2, 3, 4, 5)"""
            result = self.db.selectSQL(sql, (self.dt_id, self.wx_draw_fee * 100))
            if result:
                wx_valid = False
        if self.ali_draw_rate:
            sql = """select 1 from mch_payment WHERE dt_id=%s and
                 withdraw_rate is not NULL and withdraw_fee < %s and payment_type in (7, 8, 9)"""
            result = self.db.selectSQL(sql, (self.dt_id, self.ali_draw_fee * 100))
            if result:
                ali_valid = False
        return wx_valid, ali_valid

    def check_dt_d0_with_draw_rate(self):
        ali_valid, wx_valid = True, True
        if self.wx_draw_rate:
            sql = """select 1 from mch_payment WHERE dt_id=%s and
                 withdraw_rate is not NULL and withdraw_rate < %s and payment_type in (1, 2, 3, 4, 5)"""
            result = self.db.selectSQL(sql, (self.dt_id, self.wx_draw_rate * 10))
            if result:
                wx_valid = False
        if self.ali_draw_rate:
            sql = """select 1 from mch_payment WHERE dt_id=%s and
                 withdraw_rate is not NULL and withdraw_rate < %s and payment_type in (7, 8, 9)"""
            result = self.db.selectSQL(sql, (self.dt_id, self.ali_draw_rate * 10))
            if result:
                ali_valid = False
        return wx_valid, ali_valid

    def get_dt_payments(self, cursor):
        query = """select id, activated_status, payment_rate, payment_type  from dt_payment where dt_id=%s"""
        cursor.execute(query, (self.dt_id,))
        payments = cursor.fetchall()
        payments_dict = {}
        for each_payment in payments:
            payments_dict[each_payment[3]] = each_payment
        return payments_dict

    def get_new_dt_payments(self, cursor):
        query = """select id, activated_status, payment_rate, uline_payment_code, uline_settle_id
                    from dt_payment where dt_id=%s"""
        cursor.execute(query, (self.dt_id,))
        payments = cursor.fetchall()
        payments_dict = {}
        for each_payment in payments:
            # 表示d0
            # if each_payment[-1] == 2:
            #     payments_dict[each_payment[3] + '_D0'] = each_payment
            # else:
            #     payments_dict[each_payment[3]] = each_payment
            payments_dict[each_payment[3]] = each_payment
        return payments_dict


class ComplexEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)
