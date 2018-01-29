#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/9/16'
import re

from wtforms import validators, fields, ValidationError
from wtforms.validators import NumberRange
from uline.utils.form import File, BaseForm
from uline.public.baseDB import DbClient
from datetime import date
from decimal import Decimal
from uline.public.constants import PAYMENT, AVAILABLE_PAYMENTS, AUTH_STATUS
from uline.settings import FEATURE_SWITCH
from uline.model.uline.base import uline_session
from uline.model.uline.user import BkUser

ZERO_RATE = FEATURE_SWITCH.get('0_RATE', False)

db = DbClient()


def auth_bank_id(form, field):
    if field.data in [2, "2"]:
        if not form.bk_id.data:
            raise ValidationError(u'如果渠道商属于同业银行,则同业银行字段为必选字段')
        else:
            if not str(form.bk_id.data).isdigit():
                raise ValidationError(u'银行账号不存在请重新输入')
            bk = uline_session.query(BkUser.bk_id).filter(BkUser.bk_id == form.bk_id.data).first()
            if not bk:
                raise ValidationError(u'银行账号不存在请重新输入')


def validate_email(form, field):
    ret = db.selectSQL(
        "select dt_id from dt_user where email=%s", (field.data,))
    if ret:
        raise ValidationError(u'该邮箱已存在,请重新输入')


def validate_bk_email(form, field):
    ret = db.selectSQL(
        "select 1 from bk_user where email=%s", (field.data,))
    if ret:
        raise ValidationError(u'该邮箱已存在,请重新输入')


def validate_dt_email(form, field):
    ret = db.selectSQL(
        "select dt_id from dt_inlet_info where email=%s", (field.data,))
    if ret:
        raise ValidationError(u'该邮箱已存在,请重新输入')


# def validate_mobile(form, field):
#     ret = db.selectSQL("select dt_id from dt_inlet_info where mobile=%s", (field.data,))
#     if ret:
#         raise ValidationError(u'该手机号已存在,请重新输入')

def validate_mch_id(form, field):
    ret = db.selectSQL("SELECT count(*) FROM mch_inlet_info WHERE mch_id=%s",
                       (field.data,))

    if not ret[0]:
        raise ValidationError(u'该商户号不存在,请确认输入')


def validate_dt_id(form, field):
    ret = db.selectSQL("SELECT count(*) FROM dt_inlet_info WHERE dt_id=%s",
                       (field.data,))
    if not ret[0]:
        raise ValidationError(u'该渠道商号不存在,请确认输入')


def validate_inter_bank_id(form, field):
    ret = db.selectSQL("SELECT count(*) FROM bk_user WHERE bk_id=%s and bk_type=2",
                       (field.data,))
    if not ret[0]:
        raise ValidationError(u'该同业银行不存在')


def validate_chain_id(form, field):
    ret = db.selectSQL("SELECT count(*) FROM dt_inlet_info WHERE dt_id=%s and parent_id NOTNULL",
                       (field.data,))
    if not ret[0]:
        raise ValidationError(u'该连锁商户号不存在,请确认输入')


def validate_license_period(form, field):
    if form.licenseEndDate.data is None and field.data in [None, 'False', '']:
        raise ValidationError(u'营业执照无效的结束时间')


def validate_license_end_date(form, field):
    if form.licensePeriod.data in [None, 'False', ''] and field.data in [None, '']:
        raise ValidationError(u'营业执照无效的结束时间')
    if form.licensePeriod.data in [None, 'False', ''] and (
            field.data - date.today()).days < 90:
        raise ValidationError(u'营业执照有效期不足3个月')

#
# def validate_check_item1(form, field):
#     if not field.data:
#         raise ValidationError(u'微信－扫码支付的费率大于0')
#
#
# def validate_check_item2(form, field):
#     if not field.data:
#         raise ValidationError(u'微信－刷卡支付的费率大于0')
#
#
# def validate_check_item3(form, field):
#     if not field.data:
#         raise ValidationError(u'微信－公众账号支付的费率大于0')
#
#
# def validate_check_item4(form, field):
#     if not field.data:
#         raise ValidationError(u'微信－APP支付的费率大于0')
#
#
# def validate_check_item7(form, field):
#     if not field.data:
#         raise ValidationError(u'支付宝－扫码支付的费率大于0')
#
#
# def validate_check_item8(form, field):
#     if not field.data:
#         raise ValidationError(u'支付宝－刷卡支付的费率大于0')
#
#
# def validate_check_item9(form, field):
#     if not field.data:
#         raise ValidationError(u'支付宝－JS支付的费率大于0')


def validate_mch_payment_rate1(form, field):
    data1 = float(field.data)

    if str(data1)[::-1].find('.') > 1:
        raise ValidationError(u'微信－扫码支付的费率小数不得超过1位')

    if isinstance(data1, float):
        if ZERO_RATE and data1 != 0.0 and 0 < data1 < 2:
            raise ValidationError(u'微信－扫码支付的费率设置错误, 需设置为大于等于2')
        elif not ZERO_RATE and data1 < 2:
            raise ValidationError(u'微信－扫码支付的费率设置错误, 需设置为大于等于2')

    data2 = form.checkItem2.data
    data3 = form.checkItem3.data
    zero_payments = [(data is not None and data == 0)
                     for data in [data1, data2, data3]]
    valid__zero_payments = [(data is None or data == 0)
                            for data in [data1, data2, data3]]
    if any(zero_payments) and not all(valid__zero_payments):
        raise ValidationError(u'微信－扫码支付的费率设置错误, 需设置为大于等于2')


def validate_mch_payment_rate2(form, field):
    data2 = field.data
    if str(data2)[::-1].find('.') > 1:
        raise ValidationError(u'微信－刷卡支付的费率小数不得超过1位')
    if ZERO_RATE and data2 != 0.0 and 0 < data2 < 2:
        raise ValidationError(u'微信－刷卡支付的费率设置错误, 需设置为大于等于2')
    elif not ZERO_RATE and data2 < 2:
        raise ValidationError(u'微信－刷卡支付的费率设置错误, 需设置为大于等于2')

    data1 = form.checkItem1.data
    data3 = form.checkItem3.data
    zero_payments = [(data is not None and data == 0)
                     for data in [data1, data2, data3]]
    valid__zero_payments = [(data is None or data == 0)
                            for data in [data1, data2, data3]]
    if any(zero_payments) and not all(valid__zero_payments):
        raise ValidationError(u'微信－刷卡支付的费率设置错误, 需设置为大于等于2')


def validate_mch_payment_rate3(form, field):
    data3 = field.data
    if str(data3)[::-1].find('.') > 1:
        raise ValidationError(u'微信－公众账号支付的费率小数不得超过1位')
    if ZERO_RATE and data3 != Decimal(0) and Decimal(0) < data3 < Decimal(2):
        raise ValidationError(u'微信－公众账号支付的费率设置错误, 需设置为大于等于2')
    elif not ZERO_RATE and Decimal(0) < data3 < Decimal(2):
        raise ValidationError(u'微信－公众账号支付的费率设置错误, 需设置为大于等于2')

    data1 = form.checkItem1.data
    data2 = form.checkItem3.data
    zero_payments = [(data is not None and data == 0)
                     for data in [data1, data2, data3]]
    valid__zero_payments = [(data is None or data == 0)
                            for data in [data1, data2, data3]]
    if any(zero_payments) and not all(valid__zero_payments):
        raise ValidationError(u'微信－公众账号支付的费率设置错误, 需设置为大于等于2')


def validate_mch_payment_rate4(form, field):
    data = None
    try:
        data = float(field.data)
    except:
        pass
    if str(data)[::-1].find('.') > 1:
        raise ValidationError(u'微信－APP支付的费率小数不得超过1位')
    if isinstance(data, float):
        if data < 6:
            raise ValidationError(u'微信－APP支付的费率设置错误, 需设置为大于等于6')


def validate_mch_payment_rate5(form, field):
    data = None
    try:
        data = float(field.data)
    except:
        pass
    if str(data)[::-1].find('.') > 1:
        raise ValidationError(u'微信－H5支付的费率小数不得超过1位')
    if isinstance(data, float):
        if data < 6:
            raise ValidationError(u'微信－H5支付的费率设置错误, 需设置为大于等于6')


def validate_mch_payment_rate7(form, field):
    data = None
    try:
        data = float(field.data)
    except:
        pass
    if str(data)[::-1].find('.') > 1:
        raise ValidationError(u'支付宝－扫码支付的费率小数不得超过1位')
    if isinstance(data, float):
        if data < 2:
            raise ValidationError(u'支付宝－扫码支付的费率设置错误, 需设置为大于等于2')


def validate_mch_payment_rate8(form, field):
    data = None
    try:
        data = float(field.data)
    except:
        pass
    if str(data)[::-1].find('.') > 1:
        raise ValidationError(u'支付宝－刷卡支付的费率小数不得超过1位')
    if isinstance(data, float):
        if data < 2:
            raise ValidationError(u'支付宝－刷卡支付的费率设置错误, 需设置为大于等于2')


def validate_mch_payment_rate9(form, field):
    data = None
    try:
        data = float(field.data)
    except:
        pass
    if str(data)[::-1].find('.') > 1:
        raise ValidationError(u'支付宝－JS支付的费率小数不得超过1位')
    if isinstance(data, float):
        if 0.0 < data < 2:
            raise ValidationError(u'支付宝－JS支付的费率设置错误, 需设置为大于等于2')


def validate_mch_payment_rate21(form, field):
    data = None
    try:
        data = float(field.data)
    except:
        pass
    if str(data)[::-1].find('.') > 1:
        raise ValidationError(u'京东－扫码支付的费率小数不得超过1位')
    if isinstance(data, float):
        if data < 2:
            raise ValidationError(u'京东－扫码支付的费率设置错误, 需设置为大于等于2')


def validate_mch_payment_rate22(form, field):
    data = None
    try:
        data = float(field.data)
    except:
        pass
    if str(data)[::-1].find('.') > 1:
        raise ValidationError(u'京东－刷卡支付的费率小数不得超过1位')
    if isinstance(data, float):
        if data < 2:
            raise ValidationError(u'京东－刷卡支付的费率设置错误, 需设置为大于等于2')


def validate_mch_payment_rate23(form, field):
    data = None
    try:
        data = float(field.data)
    except:
        pass
    if str(data)[::-1].find('.') > 1:
        raise ValidationError(u'京东－公众号支付的费率小数不得超过1位')
    if isinstance(data, float):
        if data < 2:
            raise ValidationError(u'京东－公众号支付的费率设置错误, 需设置为大于等于2')


# 验证字段是否有空格
def is_has_space(form, field):
    if re.search(r' ', str(field.data)):
        raise ValidationError(str(field.data) + u' 包含空格, 请修改！')

# 验证客服电话字段


def validate_service_phone(form, field):
    if not (re.match('((^\d{5}$)|(^\d{7,8}$)|(^\d{10,12}$)|(^\d{2,4}-\d{1,'
                     '5}$)|(^\d{2,4}-\d{7,8}$)|(^\d{5,8}-\d{1,5})|(^\d{3,'
                     '4}-\d{3,8}-\d{1,4}$))', str(field.data))):
        raise ValidationError(str(field.data) + u'客服电话无效, 请修改！')


class MerchantSearch(BaseForm):
    # 列出渠道商的商户
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    activated_status = fields.IntegerField(
        validators=[validators.AnyOf([0, 1, 2])])
    mch_name = fields.StringField()
    dt_name = fields.StringField()
    auth_status = fields.IntegerField(
        validators=[validators.AnyOf([0, 1, 2, 3, 4, 5, 6, 7])])
    total_num = fields.IntegerField()
    dt_id = fields.StringField()
    mch_id = fields.StringField()
    bk_name = fields.StringField()
    bk_id = fields.StringField()
    # 0 全部 1 主银行拓展 2 同业银行拓展
    expand_type = fields.IntegerField(validators=[validators.AnyOf([0, 1, 2])], default=0)


class CsSearch(BaseForm):
    # 列出渠道商的商户
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    activated_status = fields.IntegerField(
        validators=[validators.AnyOf([0, 1, 2])])
    short_name = fields.StringField()
    cs_name = fields.StringField()
    auth_status = fields.IntegerField(
        validators=[validators.AnyOf([0, 1, 2, 3, 4])])
    total_num = fields.IntegerField()
    cs_id = fields.StringField()
    mch_id = fields.StringField()


class DistributorSearch(BaseForm):
    # 列出渠道商的商户
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    activated_status = fields.IntegerField(
        validators=[validators.AnyOf([0, 1, 2])])
    dt_name = fields.StringField()
    auth_status = fields.IntegerField(
        validators=[validators.AnyOf([0, 1, 2, 3, 4])])
    total_num = fields.IntegerField()
    dt_id = fields.StringField()
    bk_name = fields.StringField()
    bk_id = fields.StringField()
    # 0 全部 1 主银行拓展 2 同业银行拓展
    expand_type = fields.IntegerField(validators=[validators.AnyOf([0, 1, 2])], default=0)


class InterBankSearch(BaseForm):
    # 列出官方的同业银行
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    bk_name = fields.StringField()
    bk_id = fields.StringField()


class BankInfo(BaseForm):
    # 列出银行的信息
    q = fields.StringField(
        validators=[validators.DataRequired(message=u'查询字符不能为空')])
    page = fields.IntegerField(
        validators=[validators.Optional(),
                    validators.NumberRange(min=1, max=1000)])


class GetMerchantInfo(BaseForm):
    # 获取商户信息ajax接口
    mch_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_mch_id])


class GetDistributorInfo(BaseForm):
    # 获取商户信息ajax接口
    dt_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_dt_id])


def validate_d0_mch_payment_rate(form, field):
    payment_type = re.search(r'(\d+)', field.name).groups()
    if not payment_type:
        # 为空说明前端页面没有按要求写dom元素的name
        raise ValidationError(u'费率类型错误')
    # 不为空就一定有第0个数据
    payment_type = int(payment_type[0])
    payment_name = PAYMENT[str(payment_type)]

    data = None
    try:
        data = float(field.data)
    except:
        pass
    if isinstance(data, float):
        if 0.0 < data < 2:
            raise ValidationError(
                u'{0}的费率设置错误, 需设置为0或大于等于2'.format(payment_name))


def validate_draw_rate(form, field):
    data = None
    try:
        data = float(field.data)
    except:
        pass
    if isinstance(data, float):
        if data < 0.0:
            raise ValidationError(
                u'垫资费率设置错误, 需设置大于0')


def validate_payment_rate(form, field):
    # eg: WX_OFFLINE_NATIVE or WX_OFFLINE_NATIVE_D0
    try:
        platform, channel, payment_type = re.split('_', field.name)
    except:
        platform, channel, payment_type, settle = re.split('_', field.name)
    if not platform and not channel and not payment_type:
        raise ValidationError(u'费率类型错误')

    payment_name = AVAILABLE_PAYMENTS.get(field.name)

    if not payment_name:
        raise ValidationError(u'无效支付类型-%s' % field.name)

    data = None
    try:
        data = float(field.data)
    except:
        pass

    if str(data)[::-1].find('.') > 1:
        raise ValidationError(u'%s的费率小数不得超过1位' % payment_name)

    # 微信线下费率不得低于千2
    if platform == 'WX' and channel == 'OFFLINE' and isinstance(data, float) and data < 2:
        raise ValidationError(u'%s的费率设置错误, 需设置为大于等于2' % payment_name)

    # 微信线上费率不得低于千6
    if platform == 'WX' and channel == 'ONLINE' and isinstance(data, float) and data < 6:
        raise ValidationError(u'%s的费率设置错误, 需设置为大于等于6' % payment_name)

    # 微信0费率/微信围餐，只能为0
    if platform == 'WX' and channel in ['ZERO', 'DINE'] and isinstance(data, float) and data not in [0, 0.0]:
        raise ValidationError(u'%s的费率设置错误, 必须为0' % payment_name)

    # 支付宝线上费率不得低于千2
    if platform == 'ALI' and channel == 'OFFLINE' and isinstance(data, float) and data < 2:
        raise ValidationError(u'%s的费率设置错误, 需设置为大于等于2' % payment_name)

    # 京东的h5支付费率不得低于4
    if platform == 'JD' and payment_type == 'H5' and not field.name.endswith('H5_DEBIT') \
            and isinstance(data, float) and data < 4:
        raise ValidationError(u'%s的费率设置错误, 需设置为大于等于4' % payment_name)

    # 支付宝线上费率不得低于千2
    if platform == 'JD' and isinstance(data, float) and data < 2:
        raise ValidationError(u'%s的费率设置错误, 需设置为大于等于2' % payment_name)


class AddDistributorlnlet(BaseForm):
    # TODO 有些需要做数据库验证
    # _xsrf:2 | 42423
    # bc9 | 5
    # bbffa0008d0cc6cb87e79d4f11f1645 | 1475897497
    # mchName:邹雷
    # jobType:4
    # province:42 - 天津
    # city:43 - 天津市
    # address:我是联系地址
    # contact:邹雷
    # mobile:18772318985
    # email:c4d @ outlook.com
    # balanceType:2
    # balanceName:邹雷
    # balanceNo:1234567890
    # idCard:420821199112203510
    # imgCardFront:black.png
    # imgCardBack:black.png
    # checkItem1:5
    # checkItem2:5
    # checkItem3:
    # wx_channel_id: sdfasdasdadsdfasdf
    dtName = fields.StringField(validators=[validators.Length(
        min=2, max=64, message=u'无效渠道商名称'), is_has_space])
    dtType = fields.IntegerField(
        validators=[validators.NumberRange(min=1, max=2, message=u'无效渠道商类型'), is_has_space])
    jobType = fields.StringField(validators=[validators.Length(
        min=15, max=15, message=u'无效行业类别'), is_has_space])
    area = fields.StringField()
    cmbProvince = fields.StringField()
    cmbCity = fields.StringField()
    cmbArea = fields.StringField()
    province = fields.StringField(validators=[validators.Length(
        min=2, max=32, message=u'无效省份'), is_has_space])
    city = fields.StringField(validators=[validators.Length(
        min=2, max=32, message=u'无效城市'), is_has_space])
    district = fields.StringField(validators=[validators.Length(
        min=2, max=32, message=u'无效区域'), is_has_space])
    address = fields.StringField(validators=[validators.Length(
        min=2, max=255, message=u'无效地址'), is_has_space])
    # 银联新字段
    # 负责人
    # head_name = fields.StringField(validators=[validators.Length(
    #     min=2, max=20, message=u'无效负责人姓名'), is_has_space])
    # 负责人电话
    # head_mobile = fields.StringField(validators=[validators.Length(min=5, max=15, message=u'负责人电话'),
    #                                              validate_service_phone, is_has_space])
    # 手持身份证照片
    # img_with_id_card = fields.FileField('img_with_id_card', validators=[File])
    contact = fields.StringField(validators=[validators.Length(
        min=2, max=20, message=u'无效联系人姓名'), is_has_space])
    mobile = fields.StringField(validators=[validators.Length(
        min=11, max=11, message=u'手机号必须为11位'), is_has_space])
    servicePhone = fields.StringField(validators=[validators.Length(min=5, max=15, message=u'无效客服电话'),
                                                  validate_service_phone, is_has_space])
    email = fields.StringField(validators=[validators.Email(
        message=u'无效邮箱'), validate_email, is_has_space])
    balanceType = fields.IntegerField(
        validators=[validators.NumberRange(min=1, max=2, message=u'无效结算账号类型'), is_has_space])
    balanceName = fields.StringField(
        validators=[validators.Length(min=1, max=25, message=u'无效结算户名'), is_has_space])
    bankNo = fields.StringField(validators=[validators.Length(
        min=12, max=13, message=u'无效银行名称'), is_has_space])
    balanceNo = fields.StringField(validators=[validators.Length(
        min=9, max=23, message=u'无效结算账户'), is_has_space])
    idCard = fields.StringField(validators=[validators.Length(
        min=1, max=20, message=u'无效身份证号码'), is_has_space])

    imgCardFront = fields.FileField('imgCardFront', validators=[File])
    imgCardBack = fields.FileField('imgCardBack', validators=[File])

    checkItem1 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'微信－扫码支付的费率为0~1000'),
            validate_mch_payment_rate1
        ],
        places=1)
    checkItem2 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'微信－刷卡支付的费率为0~1000'),
            validate_mch_payment_rate2
        ],
        places=1)
    checkItem3 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'微信－公众账号支付的费率为0~1000'),
            validate_mch_payment_rate3
        ],
        places=1)
    checkItem4 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'微信－APP支付的费率为0~1000'),
            validate_mch_payment_rate4
        ],
        places=1)
    checkItem5 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'微信－H5支付的费率为0~1000'),
            validate_mch_payment_rate5
        ],
        places=1)
    checkItem7 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'支付宝－扫码支付的费率为0~1000'),
            validate_mch_payment_rate7
        ],
        places=1)
    checkItem8 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'支付宝－刷卡支付的费率为0~1000'),
            validate_mch_payment_rate8
        ],
        places=1)
    checkItem9 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'D0-支付宝－JS支付的费率为0~1000'),
            validate_mch_payment_rate9
        ],
        places=1)

    checkItem21 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(2, 1000, message=u'京东－扫码支付的费率为2~1000'),
            validate_mch_payment_rate21
        ],
        places=1)
    checkItem22 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(2, 1000, message=u'京东－刷卡支付的费率为2~1000'),
            validate_mch_payment_rate22
        ],
        places=1)
    checkItem23 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(2, 1000, message=u'京东－公众账号支付的费率为2~1000'),
            validate_mch_payment_rate23
        ],
        places=1)

    checkItem101 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'D0-微信－扫码支付的费率为0~1000'),
            validate_d0_mch_payment_rate
        ],
        places=1)
    checkItem102 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'D0-微信－刷卡支付的费率为0~1000'),
            validate_d0_mch_payment_rate
        ],
        places=1)
    checkItem103 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'D0-微信－公众账号支付的费率为0~1000'),
            validate_d0_mch_payment_rate
        ],
        places=1)
    checkItem104 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'D0-微信－APP支付的费率为0~1000'),
            validate_d0_mch_payment_rate
        ],
        places=1)
    checkItem105 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'D0-微信－H5支付的费率为0~1000'),
            validate_d0_mch_payment_rate
        ],
        places=1)
    checkItem107 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'D0-支付宝－扫码支付的费率为0~1000'),
            validate_d0_mch_payment_rate
        ],
        places=1)
    checkItem108 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'D0-支付宝－刷卡支付的费率为0~1000'),
            validate_d0_mch_payment_rate
        ],
        places=1)
    checkItem109 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'D0-支付宝－JS支付的费率为0~1000'),
            validate_d0_mch_payment_rate
        ],
        places=1)

    # 微信线下
    WX_OFFLINE_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'微信－线下-扫码支付的费率为0~1000'),
            validate_payment_rate
        ],
        places=1)
    WX_OFFLINE_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'微信－线下-刷卡支付的费率为0~1000'),
            validate_payment_rate
        ],
        places=1)
    WX_OFFLINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'微信－线下-公众号支付的费率为0~1000'),
            validate_payment_rate
        ],
        places=1)

    # 微信线上
    WX_ONLINE_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(6, 1000, message=u'微信－线上-扫码支付的费率为6~1000'),
            validate_payment_rate
        ],
        places=1)
    WX_ONLINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(6, 1000, message=u'微信－线上-公众号支付的费率为6~1000'),
            validate_payment_rate
        ],
        places=1)

    WX_ONLINE_APP = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(6, 1000, message=u'微信－线上-APP支付的费率为6~1000'),
            validate_payment_rate
        ],
        places=1)
    WX_ONLINE_MWEB = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(6, 1000, message=u'微信－线上-H5支付的费率为6~1000'),
            validate_payment_rate
        ],
        places=1)

    # 微信围餐
    WX_DINE_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_DINE_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_DINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)

    # 微信0费率
    WX_ZERO_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_ZERO_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_ZERO_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)

    # 支付宝线下
    ALI_OFFLINE_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'支付宝－线下-扫码支付的费率为0~1000'),
            validate_payment_rate
        ],
        places=1)
    ALI_OFFLINE_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'支付宝－线下-刷卡支付的费率为0~1000'),
            validate_payment_rate
        ],
        places=1)

    ALI_OFFLINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'支付宝－线下-公众号支付的费率为0~1000'),
            validate_payment_rate
        ],
        places=1)

    UNIONPAY_OFFLINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'银联－线下-公众号支付的费率为0~1000'),
            validate_payment_rate
        ],
        places=1)

    # 支付宝0费率
    ALI_ZERO_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    ALI_ZERO_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)

    ALI_ZERO_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)

    # D0 临时方案
    # 微信线下
    WX_OFFLINE_NATIVE_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_OFFLINE_MICROPAY_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_OFFLINE_JSAPI_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)

    # 微信线上
    WX_ONLINE_NATIVE_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_ONLINE_JSAPI_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)

    WX_ONLINE_APP_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_ONLINE_MWEB_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)

    # 微信围餐
    WX_DINE_NATIVE_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_DINE_MICROPAY_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_DINE_JSAPI_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)

    # 微信0费率
    WX_ZERO_NATIVE_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_ZERO_MICROPAY_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_ZERO_JSAPI_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)

    # 支付宝线下
    ALI_OFFLINE_NATIVE_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    ALI_OFFLINE_MICROPAY_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)

    ALI_OFFLINE_JSAPI_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)

    # 京东线下
    JD_OFFLINE_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'京东－线下-扫码支付的费率为0~1000'),
            validate_payment_rate
        ],
        places=1)
    JD_OFFLINE_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'京东－线下-刷卡支付的费率为0~1000'),
            validate_payment_rate
        ],
        places=1)

    JD_OFFLINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'京东－线下-公众号支付的费率为0~1000'),
            validate_payment_rate
        ],
        places=1)

    JD_ONLINE_H5 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'京东－线上-h5支付的费率为4~1000'),
            validate_payment_rate
        ],
        places=1)

    JD_ONLINE_H5_DEBIT = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'京东－线上-h5支付(借记卡)的费率为2~1000'),
            validate_payment_rate
        ],
        places=1)

    # D0提现手续费(老的)
    wx = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000000, message=u'微信手续费设置错误')
        ]
    )

    alipay = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000000, message=u'支付宝手续费设置错误')
        ]
    )

    # D0提现手续费
    wx_draw_fee = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000000, message=u'微信手续费设置错误')
        ]
    )

    ali_draw_fee = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000000, message=u'支付宝手续费设置错误')
        ]
    )

    # D0提现垫资费
    wx_draw_rate = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_draw_rate
        ]
    )

    ali_draw_rate = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_draw_rate
        ]
    )

    # 是否使用D0提现
    bankRatePayWechat = fields.IntegerField(validators=[validators.Optional()])
    bankRatePayAlipay = fields.IntegerField(validators=[validators.Optional()])

    licenseNum = fields.StringField(
        validators=[
            validators.required(),
            validators.Length(min=1, max=32, message=u'无效营业执照注册号')
        ]
    )
    licenseStartDate = fields.DateField(validators=[validators.Required()])
    licenseEndDate = fields.DateField(
        validators=[
            validators.Optional(),
            validate_license_end_date
        ]
    )
    licensePeriod = fields.StringField(
        # 'licensePeriod',
        validators=[
            # validators.Optional(),
            validate_license_period
        ]
    )
    licenseScope = fields.TextAreaField(
        validators=[
            validators.Length(max=500, message=u'营业范围内容太长')
        ]
    )
    licenseImg = fields.FileField(
        'licenseImg',
        validators=[File]
    )
    wxChannelId = fields.StringField(validators=[
        validators.Optional(),
        validators.Length(min=1, max=32, message=u'请重新输入微信渠道号')
    ])
    wxAppChannelId = fields.StringField(validators=[
        validators.Optional(),
        validators.Length(min=1, max=32, message=u'请重新输入微信APP渠道号')
    ])

    # 银联机构号
    unionpay_id = fields.StringField(validators=[
        validators.Optional(),
        validators.Length(min=1, max=32, message=u'银联机构号')
    ])

    use_dine = fields.StringField(validators=[validators.optional()])

    # 围餐
    checkItem11 = fields.DecimalField(validators=[validators.Optional()])
    checkItem12 = fields.DecimalField(validators=[validators.Optional()])
    checkItem13 = fields.DecimalField(validators=[validators.Optional()])

    # 银联js支付
    checkItem33 = fields.DecimalField(validators=[validators.Optional()])
    wx_dinner_channel_id = fields.StringField(validators=[
        validators.Optional(),
        validators.Length(min=1, max=32, message=u'请重新输入微信围餐渠道号')
    ])
    bk_id = fields.IntegerField(validators=[validators.Optional()])
    bankType = fields.IntegerField(validators=[validators.required(), validators.AnyOf([1, 2]), auth_bank_id])

    alipay_pid = fields.StringField(validators=[
        validators.Optional(),
        validators.Length(min=1, max=32, message=u'请重新输入微信APP渠道号')
    ])

    # 平台
    WX = fields.StringField(default='')
    ALI = fields.StringField(default='')
    JD = fields.StringField(default='')

    # 微信通道
    WX_OFFLINE = fields.StringField(default='')
    WX_ONLINE = fields.StringField(default='')
    WX_DINE = fields.StringField(default='')
    WX_ZERO = fields.StringField(default='')

    # D0
    WX_D0 = fields.StringField(default='')
    ALI_D0 = fields.StringField(default='')

    # D1
    WX_D1 = fields.StringField(default='')
    ALI_D1 = fields.StringField(default='')

    # 支付宝通道
    ALI_ZERO = fields.StringField(default='')
    ALI_OFFLINE = fields.StringField(default='')


class AddInterBankInlet(BaseForm):
    bk_name = fields.StringField(validators=[validators.Length(
        min=2, max=64, message=u'无效的同业银行名称'), is_has_space])

    email = fields.StringField(validators=[validators.Email(
        message=u'无效邮箱'), validate_bk_email, is_has_space])


class ModifyInterBankInlet(BaseForm):
    bk_id = fields.IntegerField(validators=[validators.DataRequired(
        message=u'查询字符不能为空'), validate_inter_bank_id, is_has_space])
    email = fields.StringField(validators=[validators.Email(
        message=u'无效邮箱'), validate_bk_email, is_has_space])


class ModifyDistributorlnlet(BaseForm):
    # _xsrf:2 | 42423
    # bc9 | 5
    # bbffa0008d0cc6cb87e79d4f11f1645 | 1475897497
    # mchName:邹雷
    # jobType:4
    # province:42 - 天津
    # city:43 - 天津市
    # address:我是联系地址
    # contact:邹雷
    # mobile:18772318985
    # email:c4d @ outlook.com
    # balanceType:2
    # balanceName:邹雷
    # balanceNo:1234567890
    # idCard:420821199112203510
    # imgCardFront:black.png
    # imgCardBack:black.png
    # checkItem1:5
    # checkItem2:5
    # checkItem3:
    dt_id = fields.IntegerField(validators=[validators.DataRequired(
        message=u'查询字符不能为空'), validate_dt_id, is_has_space])
    dtName = fields.StringField(validators=[validators.Length(
        min=2, max=64, message=u'无效商户名'), is_has_space])
    # jobType = fields.StringField(validators=[validators.Length(min=15, max=15, message=u'无效行业类别')])
    # industryName = fields.StringField()
    province = fields.StringField(validators=[validators.Length(
        min=2, max=32, message=u'无效省份'), is_has_space])
    city = fields.StringField(validators=[validators.Length(
        min=2, max=32, message=u'无效城市'), is_has_space])
    district = fields.StringField(validators=[validators.Length(
        min=2, max=32, message=u'无效区域'), is_has_space])
    address = fields.StringField(validators=[validators.Length(
        min=2, max=255, message=u'无效地址'), is_has_space])
    contact = fields.StringField(validators=[validators.Length(
        min=2, max=20, message=u'无效联系人姓名'), is_has_space])
    mobile = fields.StringField(validators=[validators.Length(
        min=11, max=11, message=u'手机号必须为11位'), is_has_space])
    servicePhone = fields.StringField(validators=[validators.Length(min=5, max=15, message=u'无效客服电话'),
                                                  validate_service_phone, is_has_space])
    email = fields.StringField(
        validators=[validators.Email(message=u'无效邮箱'), is_has_space])

    balanceType = fields.IntegerField(
        validators=[validators.NumberRange(min=1, max=2, message=u'无效结算账号类型'), is_has_space])
    balanceName = fields.StringField(
        validators=[validators.Length(min=1, max=25, message=u'无效结算户名'), is_has_space])
    bankNo = fields.StringField(validators=[validators.Length(
        min=12, max=13, message=u'无效支联代码'), is_has_space])

    force_update = fields.StringField()

    # bankName = fields.StringField()
    balanceNo = fields.StringField(validators=[validators.Length(
        min=9, max=23, message=u'无效结算账户'), is_has_space])
    idCard = fields.StringField(validators=[validators.Length(
        min=1, max=20, message=u'无效身份证号码'), is_has_space])

    imgCardFrontOld = fields.StringField(
        validators=[validators.Length(min=4, max=255, message=u'无效文件名'), is_has_space])
    imgCardBackOld = fields.StringField(
        validators=[validators.Length(min=4, max=255, message=u'无效文件名'), is_has_space])

    imgCardFront = fields.FileField('imgCardFront')
    imgCardBack = fields.FileField('imgCardBack')

    # TODO 判断该商户是否有该支付权限,而且费率是否大于自身
    checkItem1 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'微信－扫码支付的费率为0~1000'),
            validate_mch_payment_rate1
        ],
        places=1)
    checkItem2 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'微信－刷卡支付的费率为0~1000'),
            validate_mch_payment_rate2
        ],
        places=1)
    checkItem3 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'微信－公众账号支付的费率为0~1000'),
            validate_mch_payment_rate3
        ],
        places=1)
    checkItem4 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'微信－APP支付的费率为0~1000'),
            validate_mch_payment_rate4,
        ],
        places=1)
    checkItem5 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'微信－H5支付的费率为0~1000'),
            validate_mch_payment_rate5,
        ],
        places=1)
    checkItem7 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'支付宝－扫码支付的费率为0~1000'),
            validate_mch_payment_rate7
        ],
        places=1)
    checkItem8 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'支付宝－刷卡支付的费率为0~1000'),
            validate_mch_payment_rate8
        ],
        places=1)
    checkItem9 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'支付宝－JS支付的费率为0~1000'),
            validate_mch_payment_rate9
        ],
        places=1)

    checkItem21 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(2, 1000, message=u'京东－扫码支付的费率为2~1000'),
            validate_mch_payment_rate21
        ],
        places=1)
    checkItem22 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(2, 1000, message=u'京东－刷卡支付的费率为2~1000'),
            validate_mch_payment_rate22
        ],
        places=1)
    checkItem23 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(2, 1000, message=u'京东－公众账号支付的费率为2~1000'),
            validate_mch_payment_rate23
        ],
        places=1)

    checkItem101 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'D0-微信－扫码支付的费率为0~1000'),
            validate_d0_mch_payment_rate
        ],
        places=1)
    checkItem102 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'D0-微信－刷卡支付的费率为0~1000'),
            validate_d0_mch_payment_rate
        ],
        places=1)
    checkItem103 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'D0-微信－公众账号支付的费率为0~1000'),
            validate_d0_mch_payment_rate
        ],
        places=1)
    checkItem104 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'D0-微信－APP支付的费率为0~1000'),
            validate_d0_mch_payment_rate
        ],
        places=1)
    checkItem105 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'D0-微信－H5支付的费率为0~1000'),
            validate_d0_mch_payment_rate
        ],
        places=1)
    checkItem107 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'D0-支付宝－扫码支付的费率为0~1000'),
            validate_d0_mch_payment_rate
        ],
        places=1)
    checkItem108 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'D0-支付宝－刷卡支付的费率为0~1000'),
            validate_d0_mch_payment_rate
        ],
        places=1)
    checkItem109 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'D0-支付宝－JS支付的费率为0~1000'),
            validate_d0_mch_payment_rate
        ],
        places=1)

    # 围餐
    checkItem11 = fields.DecimalField(validators=[validators.Optional()])
    checkItem12 = fields.DecimalField(validators=[validators.Optional()])
    checkItem13 = fields.DecimalField(validators=[validators.Optional()])

    # 微信线下
    WX_OFFLINE_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'微信－线下-扫码支付的费率为0~1000'),
            validate_payment_rate
        ],
        places=1)
    WX_OFFLINE_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'微信－线下-刷卡支付的费率为0~1000'),
            validate_payment_rate
        ],
        places=1)
    WX_OFFLINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'微信－线下-公众号支付的费率为0~1000'),
            validate_payment_rate
        ],
        places=1)

    # 微信线上
    WX_ONLINE_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(6, 1000, message=u'微信－线上-扫码支付的费率为6~1000'),
            validate_payment_rate
        ],
        places=1)
    WX_ONLINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(6, 1000, message=u'微信－线上-公众号支付的费率为6~1000'),
            validate_payment_rate
        ],
        places=1)

    WX_ONLINE_APP = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(6, 1000, message=u'微信－线上-APP支付的费率为6~1000'),
            validate_payment_rate
        ],
        places=1)
    WX_ONLINE_MWEB = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(6, 1000, message=u'微信－线上-H5支付的费率为6~1000'),
            validate_payment_rate
        ],
        places=1)

    UNIONPAY_OFFLINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'银联－线下-公众号支付的费率为0~1000'),
            validate_payment_rate
        ],
        places=1)

    # 微信围餐
    WX_DINE_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_DINE_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_DINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)

    # 微信0费率
    WX_ZERO_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_ZERO_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_ZERO_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)

    # 支付宝线下
    ALI_OFFLINE_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'支付宝－线下-扫码支付的费率为0~1000'),
            validate_payment_rate
        ],
        places=1)
    ALI_OFFLINE_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'支付宝－线下-刷卡支付的费率为0~1000'),
            validate_payment_rate
        ],
        places=1)

    ALI_OFFLINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'支付宝－线下-公众号支付的费率为0~1000'),
            validate_payment_rate
        ],
        places=1)

    # 支付宝线下
    ALI_ZERO_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    ALI_ZERO_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)

    ALI_ZERO_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)

    # 京东线下
    JD_OFFLINE_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'京东－线下-扫码支付的费率为0~1000'),
            validate_payment_rate
        ],
        places=1)
    JD_OFFLINE_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'京东－线下-刷卡支付的费率为0~1000'),
            validate_payment_rate
        ],
        places=1)

    JD_OFFLINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'京东－线下-公众号支付的费率为0~1000'),
            validate_payment_rate
        ],
        places=1)

    JD_ONLINE_H5 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'京东－线上-h5支付的费率为4~1000'),
            validate_payment_rate
        ],
        places=1)

    JD_ONLINE_H5_DEBIT = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'京东－线上-h5支付(借记卡)的费率为2~1000'),
            validate_payment_rate
        ],
        places=1)

    # D0 临时方案
    # 微信线下
    WX_OFFLINE_NATIVE_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_OFFLINE_MICROPAY_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_OFFLINE_JSAPI_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)

    # 微信线上
    WX_ONLINE_NATIVE_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_ONLINE_JSAPI_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)

    WX_ONLINE_APP_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_ONLINE_MWEB_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)

    # 微信围餐
    WX_DINE_NATIVE_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_DINE_MICROPAY_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_DINE_JSAPI_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)

    # 微信0费率
    WX_ZERO_NATIVE_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_ZERO_MICROPAY_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    WX_ZERO_JSAPI_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)

    # 支付宝线下
    ALI_OFFLINE_NATIVE_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)
    ALI_OFFLINE_MICROPAY_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)

    ALI_OFFLINE_JSAPI_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_payment_rate
        ],
        places=1)

    # D0提现手续费(老版)
    # 银联js支付
    checkItem33 = fields.DecimalField(validators=[validators.Optional()])

    # D0提现手续费
    wx = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000000, message=u'D0-微信手续费设置错误')
        ]
    )

    alipay = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000000, message=u'D0-支付宝手续费设置错误')
        ]
    )

    # D0提现手续费
    wx_draw_fee = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000000, message=u'D0-微信手续费设置错误')
        ]
    )

    ali_draw_fee = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000000, message=u'D0-支付宝手续费设置错误')
        ]
    )

    # D0提现垫资费
    wx_draw_rate = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_draw_rate
        ]
    )

    ali_draw_rate = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_draw_rate
        ]
    )

    # 是否使用D0提现
    bankRatePayWechat = fields.IntegerField(validators=[validators.Optional()])
    bankRatePayAlipay = fields.IntegerField(validators=[validators.Optional()])

    licenseNum = fields.StringField(
        validators=[
            validators.required(),
            validators.Length(min=1, max=32, message=u'无效营业执照注册号')
        ]
    )
    licenseStartDate = fields.DateField(validators=[validators.Required()])
    licenseEndDate = fields.DateField(
        validators=[
            validators.Optional(),
            validate_license_end_date
        ]
    )
    licensePeriod = fields.StringField(
        # 'licensePeriod',
        validators=[
            # validators.Optional(),
            validate_license_period
        ]
    )
    licenseScope = fields.TextAreaField(
        validators=[
            validators.Length(max=500, message=u'营业范围内容太长')
        ]
    )
    licenseImgOld = fields.StringField(
        validators=[validators.Length(min=4, max=255, message=u'无效文件名')]
    )
    licenseImg = fields.FileField(
        'licenseImg',
        # validators=[File]
    )

    wxChannelId = fields.StringField(validators=[
        validators.Optional(),
        validators.Length(min=1, max=32, message=u'请重新输入微信渠道号')
    ])

    wxAppChannelId = fields.StringField(validators=[
        validators.Optional(),
        validators.Length(min=1, max=32, message=u'请重新输入微信APP渠道号')
    ])

    # 银联机构号
    unionpay_id = fields.StringField(validators=[
        validators.Optional(),
        validators.Length(min=1, max=32, message=u'银联机构号')
    ])

    jobType = fields.StringField(validators=[validators.optional(), validators.Length(
        min=15, max=15, message=u'无效行业类别'), is_has_space])
    area = fields.StringField()
    cmbProvince = fields.StringField()
    cmbCity = fields.StringField()
    cmbArea = fields.StringField()
    dtType = fields.IntegerField(
        validators=[validators.NumberRange(min=1, max=2, message=u'无效渠道商类型'), is_has_space])

    use_dine = fields.StringField(validators=[validators.optional()])
    wx_dinner_channel_id = fields.StringField(validators=[
        validators.Optional(),
        validators.Length(min=1, max=32, message=u'请重新输入微信围餐渠道号')
    ])
    bk_name = fields.StringField(validators=[validators.Optional()])
    bankType = fields.IntegerField(validators=[validators.Optional(), validators.AnyOf([1, 2])])

    alipay_pid = fields.StringField(validators=[
        validators.Optional(),
        validators.Length(min=1, max=32, message=u'请重新输入微信APP渠道号')
    ])

    # 平台
    WX = fields.StringField(default='')
    ALI = fields.StringField(default='')
    JD = fields.StringField(default='')

    # 微信通道
    WX_OFFLINE = fields.StringField(default='')
    WX_ONLINE = fields.StringField(default='')
    WX_DINE = fields.StringField(default='')
    WX_ZERO = fields.StringField(default='')

    # D0
    WX_D0 = fields.StringField(default='')
    ALI_D0 = fields.StringField(default='')

    # D1
    WX_D1 = fields.StringField(default='')
    ALI_D1 = fields.StringField(default='')

    # 支付宝通道
    ALI_ZERO = fields.StringField(default='')
    ALI_OFFLINE = fields.StringField(default='')


class ResendMchActiveEmail(BaseForm):
    # 获取商户信息ajax接口
    mch_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'商户ID不能为空'), validate_mch_id])


class ChainSearch(BaseForm):
    # 列出连锁商户
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    activated_status = fields.IntegerField(
        validators=[validators.AnyOf([0, 1, 2])])
    dt_name = fields.StringField()
    auth_status = fields.IntegerField(
        validators=[validators.Optional(), validators.AnyOf([0] + [int(key) for key in AUTH_STATUS])], default=0)
    total_num = fields.IntegerField()
    dt_id = fields.StringField()
    parent_id = fields.StringField()
    parent_name = fields.StringField()
    bk_name = fields.StringField()
    bk_id = fields.StringField()
    # 0 全部 1 主银行拓展 2 同业银行拓展
    expand_type = fields.IntegerField(validators=[validators.AnyOf([0, 1, 2])], default=0)


class CSSearch(BaseForm):
    # 列出渠道商的商户
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    activated_status = fields.IntegerField(
        validators=[validators.AnyOf([0, 1, 2])])
    auth_status = fields.IntegerField(
        validators=[validators.AnyOf([0, 1, 2, 3, 4])])
    total_num = fields.IntegerField()

    cs_id = fields.StringField()
    cs_name = fields.StringField()
    mch_id = fields.StringField()
    short_name = fields.StringField()
    bk_name = fields.StringField()
    bk_id = fields.StringField()
    # 0 全部 1 主银行拓展 2 同业银行拓展
    expand_type = fields.IntegerField(validators=[validators.AnyOf([0, 1, 2])], default=0)


class GetMerchanWxConfig(BaseForm):
    # 查询商户微信配置信息
    mch_id = fields.IntegerField(validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_mch_id])
    refresh = fields.IntegerField(validators=[validators.Optional()], default=1)


class GetChainWxConfig(BaseForm):
    # 查询连锁商户微信配置信息
    mch_id = fields.IntegerField(validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_dt_id])

    refresh = fields.IntegerField(validators=[validators.Optional()], default=1)


class ResendChainActiveEmail(BaseForm):
    # 获取商户信息ajax接口
    chain_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'商户ID不能为空'), validate_chain_id])
