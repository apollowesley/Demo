#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
from wtforms import validators, fields, ValidationError, RadioField
from wtforms.validators import NumberRange, URL
from wtforms.i18n import DefaultTranslations

import uline.handlers.app.distributor.utils.form as dist_form_utils
from uline.utils.form import File, BaseForm, BaseInletForm
from uline.public.baseDB import DbClient
# from uline.settings import cur_dir
from os import path
from datetime import date
import re
from uline.utils.dayzero import form_verify


db = DbClient()

cur_dir = path.dirname(path.dirname(path.abspath(__file__)))


def validate_check_item1(form, field):
    if not field.data:
        raise ValidationError(u'微信－扫码支付的费率必须大于0')


def validate_check_item2(form, field):
    if not field.data:
        raise ValidationError(u'微信－刷卡支付的费率必须大于0')


def validate_check_item3(form, field):
    if not field.data:
        raise ValidationError(u'微信－公众账号支付的费率必须大于0')


def validate_check_item4(form, field):
    if not field.data:
        raise ValidationError(u'微信－APP支付的费率必须大于6')


def validate_check_item7(form, field):
    if not field.data:
        raise ValidationError(u'支付宝－扫码支付的费率必须大于0')


def validate_check_item8(form, field):
    if not field.data:
        raise ValidationError(u'支付宝－刷卡支付的费率必须大于0')


def validate_check_item9(form, field):
    if not field.data:
        raise ValidationError(u'支付宝－JS支付的费率必须大于0')


def validate_balance_way(form, field):
    if field.data not in ['T+1', 'D+0']:
        raise ValidationError(u'结算方式是T+1或者D+0')


def validate_balance_type(form, field):
    if field.data not in [u'企业', u'个人']:
        raise ValidationError(u'结算账号类型是企业或者个人')


def validate_bank_no(form, field):
    ret = db.selectSQL(
        "select 1 from balance_bank_info where bank_no=%s", (field.data,))
    if not ret:
        raise ValidationError(u'结算支行联行号错误')


def validate_industry_code(form, field):
    ret = db.selectSQL(
        "select 1 from industry_uline_info where industry_code=%s;",
        (field.data,)
    )
    if not ret:
        raise ValidationError(u'行业类别错误')


def validate_payment_type(form, field):
    if field.data not in ['微信－扫码支付', '微信－刷卡支付', '微信－公众账号支付']:
        raise ValidationError(u'支付类型错误')


def validate_id_card_f_path(form, field):
    base_img_dir = path.normpath(
        path.join(cur_dir, '../../../static/uploads/tmp/mch/idcard/'))
    # base_img_dir = path.join(cur_dir, 'static/uploads/tmp/mch/idcard/')
    file_dir = path.join(base_img_dir, '{}'.format(
        form.cs_id), '{}'.format(form.uuid), '{}'.format(field.data))
    if not path.exists(file_dir):
        raise ValidationError(u'不存在身份证正面照片')


def validate_id_card_b_path(form, field):
    base_img_dir = path.normpath(
        path.join(cur_dir, '../../../static/uploads/tmp/mch/idcard/'))
    # base_img_dir = path.join(cur_dir, 'static/uploads/tmp/mch/idcard/')
    file_dir = path.join(base_img_dir, '{}'.format(
        form.cs_id), '{}'.format(form.uuid), '{}'.format(field.data))
    if not path.exists(file_dir):
        raise ValidationError(u'不存在身份证反面照片')


def validate_wx_use_parent(form, field):
    """
    现在已经不支持大商户模式
    """
    if field.data != '1':
        raise ValidationError(u'不支持使用渠道appid')


def validate_license_period(form, field):
    if not (form.licenseEndDate.data or field.data):
        raise ValidationError(u'营业执照无效的结束时间')


def validate_license_end_date(form, field):
    if not (form.licensePeriod.data or field.data):
        raise ValidationError(u'营业执照无效的结束时间')
    today = date.today()
    if field.data and (field.data - today).days < 90:
        raise ValidationError(u'营业执照有效期不足3个月')

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


def validate_license_period_upload(form, field):
    if not (form.license_end_date.data or field.data):
        raise ValidationError(u'营业执照无效的结束时间')
    if str(field.data) not in (['1', '2']):
        raise ValidationError(u'仅可填写是或否')


def validate_license_end_date_upload(form, field):
    if not (form.license_period.data or field.data):
        raise ValidationError(u'营业执照无效的结束时间')
    else:
        today = date.today()
        if field.data and (field.data - today).days < 90:
            raise ValidationError(u'营业执照有效期不足3个月')


class AddMerchantlnlet(BaseForm):
    mch_name = fields.StringField(
        validators=[validators.Length(min=2, max=64, message=u'无效商户名'), is_has_space])
    mch_shortname = fields.StringField(
        validators=[validators.Length(min=2, max=64, message=u'无效商户简称'), is_has_space])
    industry_no = fields.StringField(
        validators=[validate_industry_code, is_has_space])
    # jobType = fields.StringField(
    # validators=[validators.Length(min=15, max=15, message=u'无效行业类别'),
    # is_has_space])
    area = fields.StringField()
    cmbProvince = fields.StringField()
    cmbCity = fields.StringField()
    cmbArea = fields.StringField()
    province = fields.StringField(
        validators=[validators.Length(min=2, max=32, message=u'无效省份'), is_has_space])
    city = fields.StringField(
        validators=[validators.Length(min=2, max=32, message=u'无效城市'), is_has_space])
    district = fields.StringField(
        validators=[validators.Length(min=2, max=32, message=u'无效区域'), is_has_space])
    address = fields.StringField(
        validators=[validators.Length(min=2, max=255, message=u'无效地址'), is_has_space])
    contact = fields.StringField(
        validators=[validators.Length(min=2, max=20, message=u'无效联系人姓名'), is_has_space])
    mobile = fields.StringField(
        validators=[validators.Length(min=11, max=11, message=u'手机号必须为11位'), is_has_space])
    service_phone = fields.StringField(
        validators=[validators.Length(min=5, max=15, message=u'无效客服电话'), validate_service_phone, is_has_space])
    email = fields.StringField(
        validators=[validators.Email(message=u'无效邮箱'), is_has_space])
    balance_type = fields.IntegerField(
        validators=[validators.NumberRange(min=1, max=2, message=u'无效结算账号类型'), is_has_space])
    balance_name = fields.StringField(
        validators=[validators.Length(min=1, max=255, message=u'无效结算户名'), is_has_space])
    balance_account = fields.StringField(
        validators=[validators.Length(min=12, max=13, message=u'无效银行名称'), is_has_space])
    bank_no = fields.StringField(
        validators=[validators.Length(min=9, max=22, message=u'无效结算账户'), is_has_space])
    bankName = fields.StringField()
    id_card_no = fields.StringField(
        validators=[validators.Length(min=1, max=20, message=u'无效身份证号码'), is_has_space])

    id_card_img_f = fields.FileField('imgCardFront', validators=[File])
    id_card_img_b = fields.FileField('imgCardBack', validators=[File])
    activate_email_tag = fields.IntegerField(validators=[validators.AnyOf([1, 2])])

    wx_use_parent = RadioField(
        'wx_use_parent',
        [validators.Required()],
        choices=[('1', '不使用'), ('2', '使用')], default='1'
    )
    payment_type1 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type2 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type3 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type4 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type7 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type8 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type9 = fields.DecimalField(
        validators=[validators.Optional()])

    # d0费率，统一在API进行验证
    payment_type101 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type102 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type103 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type104 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type107 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type108 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type109 = fields.DecimalField(
        validators=[validators.Optional()])

    # D0提现手续费
    wx = fields.DecimalField()

    alipay = fields.DecimalField()

    license_num = fields.StringField(
        validators=[
            validators.required(),
            validators.Length(min=1, max=32, message=u'无效营业执照注册号')
        ]
    )
    license_start_date = fields.DateField(validators=[validators.Required()])
    license_end_date = fields.DateField(
        validators=[
            validators.Optional(),
            validate_license_end_date
        ]
    )
    license_period = fields.StringField(
        # 'licensePeriod',
        validators=[
            # validators.Optional(),
            validate_license_period
        ]
    )
    license_scope = fields.TextAreaField(
        validators=[
            validators.Length(max=500, message=u'营业范围内容太长')
        ]
    )
    license_img = fields.FileField(
        'licenseImg',
        validators=[File]
    )
    dt_sub_id = fields.IntegerField(validators=[
        validators.Optional(), dist_form_utils.validate_dt_sub_id_exists,
    ])

    cs_id = fields.IntegerField(validators=[
        validators.Optional()
    ])


class MerchantSearch(BaseForm):
    # 列出渠道商的商户
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    activated_status = fields.IntegerField(
        validators=[validators.AnyOf([0, 1, 2])])
    mch_name = fields.StringField()
    auth_status = fields.IntegerField(
        validators=[validators.AnyOf([0, 1, 2, 3])])
    total_num = fields.IntegerField()
    mch_id = fields.StringField()
    dt_sub_id = fields.IntegerField(validators=[
        validators.Optional(), dist_form_utils.validate_dt_sub_id_exists,
    ])
    cs_id = fields.StringField()
    cs_name = fields.StringField()


class BankInfo(BaseForm):
    # 列出渠道商的商户
    q = fields.StringField(
        validators=[validators.DataRequired(message=u'查询字符不能为空')])
    page = fields.IntegerField(
        validators=[validators.Optional(),
                    validators.NumberRange(min=1, max=1000)])


def validate_mch_id(form, field):
    ret = db.selectSQL(
        "SELECT count(*) FROM mch_inlet_info WHERE cs_id=%s AND mch_id=%s",
        (form.cs_id, field.data)
    )

    if not ret[0]:
        raise ValidationError(u'该商户号不存在,请确认输入')


class GetMerchanInfo(BaseForm):
    # 获取商户信息ajax接口
    mch_id = fields.IntegerField(
        validators=[
            validators.DataRequired(message=u'查询字符不能为空'),
            validate_mch_id
        ]
    )


class GetMerchanPayCallbackUrl(BaseForm):
    # 获取商户支付回调信息ajax接口
    mch_id = fields.IntegerField(
        validators=[
            validators.DataRequired(message=u'查询字符不能为空'),
            validate_mch_id
        ]
    )
    pay_notify_url = fields.StringField(
        validators=[
            URL(message=u"URL格式不正确"),
        ]
    )


class ModifyMerchantlnlet(BaseForm):
    cs_id = fields.StringField()
    mch_id = fields.IntegerField(
        validators=[
            validators.DataRequired(message=u'查询字符不能为空'),
            validate_mch_id,
            is_has_space
        ]
    )
    mch_name = fields.StringField(
        validators=[validators.Length(min=2, max=64, message=u'无效商户名'), is_has_space])
    mch_shortname = fields.StringField(
        validators=[validators.Length(min=2, max=64, message=u'无效商户简称'), is_has_space])
    industry_no = fields.StringField(
        validators=[validators.Length(min=15, max=15, message=u'无效行业类别'), is_has_space])
    province = fields.StringField(
        validators=[validators.Length(min=2, max=32, message=u'无效省份'), is_has_space])
    city = fields.StringField(
        validators=[validators.Length(min=2, max=32, message=u'无效城市'), is_has_space])
    district = fields.StringField(
        validators=[validators.Length(min=2, max=32, message=u'无效城市'), is_has_space])
    address = fields.StringField(
        validators=[validators.Length(min=2, max=255, message=u'无效地址'), is_has_space])
    contact = fields.StringField(
        validators=[validators.Length(min=2, max=20, message=u'无效联系人姓名'), is_has_space])
    mobile = fields.StringField(
        validators=[validators.Length(min=11, max=11, message=u'手机号必须为11位'), is_has_space])
    service_phone = fields.StringField(
        validators=[validators.Length(min=5, max=15, message=u'无效客服电话'), is_has_space])
    email = fields.StringField(
        validators=[validators.Email(message=u'无效邮箱'), is_has_space])
    balance_type = fields.IntegerField(
        validators=[validators.NumberRange(min=1, max=2, message=u'无效结算账号类型'), is_has_space])
    balance_name = fields.StringField(
        validators=[validators.Length(min=1, max=255, message=u'无效结算户名'), is_has_space])
    bank_no = fields.StringField(
        validators=[validators.Length(min=12, max=13, message=u'无效支联代码'), is_has_space])
    bankName = fields.StringField()
    balance_account = fields.StringField(
        validators=[validators.Length(min=9, max=22, message=u'无效结算账户'), is_has_space])
    id_card_no = fields.StringField(validators=[validators.Length(
        min=1, max=20, message=u'无效身份证号码'), is_has_space])

    imgCardFrontOld = fields.StringField(
        validators=[validators.Length(min=4, max=255, message=u'无效文件名')])
    imgCardBackOld = fields.StringField(
        validators=[validators.Length(min=4, max=255, message=u'无效文件名')])

    id_card_img_f = fields.FileField('imgCardFront')
    id_card_img_b = fields.FileField('imgCardBack')

    payment_type1 = fields.DecimalField()
    payment_type2 = fields.DecimalField()
    payment_type3 = fields.DecimalField()
    payment_type4 = fields.DecimalField()
    payment_type7 = fields.DecimalField()
    payment_type8 = fields.DecimalField()
    payment_type9 = fields.DecimalField()

    # d0费率，统一在API进行验证
    payment_type101 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type102 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type103 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type104 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type107 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type108 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type109 = fields.DecimalField(
        validators=[validators.Optional()])

    # D0提现手续费
    wx = fields.DecimalField()

    alipay = fields.DecimalField()

    license_num = fields.StringField(
        validators=[
            validators.required(),
            validators.Length(min=1, max=32, message=u'无效营业执照注册号'),
            is_has_space
        ]
    )
    license_start_date = fields.DateField(validators=[validators.Required()])
    license_end_date = fields.DateField(
        validators=[
            validators.Optional(),
            validate_license_end_date
        ]
    )
    license_period = fields.StringField(
        'licensePeriod',
        validators=[
            # validators.Optional(),
            validate_license_period
        ]
    )
    license_scope = fields.TextAreaField(
        validators=[
            validators.Length(max=500, message=u'营业范围内容太长')
        ]
    )
    licenseImgOld = fields.StringField(
        validators=[validators.Length(min=4, max=255, message=u'无效文件名')]
    )
    license_img = fields.FileField(
        'licenseImg',
        # validators=[File]
    )
    dt_sub_id = fields.IntegerField(validators=[
        validators.Optional(), dist_form_utils.validate_dt_sub_id_exists,
    ])

    area = fields.StringField()
    cmbProvince = fields.StringField()
    cmbCity = fields.StringField()
    cmbArea = fields.StringField()


class UploadCSInletExcel(BaseForm):
    xls_file = fields.FileField('xls_file', validators=[File])


class UploadCsInletImage(BaseForm):
    img_file = fields.FileField('img_file', validators=[File])
    uuid = fields.StringField(
        validators=[validators.Length(min=20, message=u'无效的提交参数')])


class UploadCsInletInfo(BaseForm):
    uuid = fields.StringField(
        validators=[validators.Length(min=20, message=u'无效的提交参数')])


class CSBatchInletInfo(BaseInletForm):
    cs_id = fields.StringField()
    mch_name = fields.StringField(
        validators=[validators.DataRequired(message=u'商户名称不能为空'), is_has_space])
    mch_shortname = fields.StringField(
        validators=[validators.Length(min=2, max=64, message=u'无效商户简称'), is_has_space])
    industry_code = fields.StringField(
        validators=[
            validators.Length(min=15, max=15, message=u'无效行业类别'),
            validate_industry_code,
            is_has_space
        ]
    )
    province = fields.StringField(
        validators=[validators.Length(min=2, max=32, message=u'无效省份')])
    city = fields.StringField(
        validators=[validators.Length(min=2, max=32, message=u'无效城市')])
    district = fields.StringField(
        validators=[validators.Length(min=2, max=32, message=u'无效城市')])
    address = fields.StringField(
        validators=[validators.Length(min=2, max=255, message=u'无效地址')])
    service_phone = fields.StringField(
        validators=[validators.Length(min=5, max=15, message=u'无效客服电话'), validate_service_phone, is_has_space])
    contact = fields.StringField(
        validators=[validators.Length(min=2, max=20, message=u'无效联系人'), is_has_space])
    mobile = fields.StringField(
        validators=[validators.Length(min=11, max=11, message=u'手机号必须为11位'), is_has_space])
    email = fields.StringField(validators=[validators.Email(message=u'无效邮箱')])
    balance_type = fields.StringField(
        validators=[
            validators.Length(min=2, max=30, message=u'无效结算账号类型'),
            validate_balance_type
        ]
    )
    balance_name = fields.StringField(
        validators=[validators.Length(min=2, max=255, message=u'无效结算户名'), is_has_space])
    bank_name_com = fields.StringField(
        validators=[validators.Length(min=2, max=255, message=u'无效结算银行'), is_has_space])
    bank_name = fields.StringField(
        validators=[validators.Length(min=2, max=255, message=u'无效结算支行'), is_has_space])
    bank_no = fields.StringField(validators=[validators.Length(
        min=2, max=30, message=u'无效结算支行联行号'), validate_bank_no, is_has_space])
    balance_account = fields.StringField(
        validators=[validators.Length(min=2, max=30, message=u'无效结算账号'), is_has_space])
    id_card_no = fields.StringField(
        validators=[validators.Length(min=1, max=20, message=u'无效身份证号码'), is_has_space])
    id_card_img_f = fields.StringField(validators=[validators.Length(
        min=2, max=64, message=u'无效身份证正面照片'), validate_id_card_f_path])
    id_card_img_b = fields.StringField(validators=[validators.Length(
        min=2, max=64, message=u'无效身份证反面照片'), validate_id_card_b_path])
    # D1
    checkItem1 = fields.DecimalField()
    checkItem2 = fields.DecimalField()
    checkItem3 = fields.DecimalField()
    checkItem4 = fields.DecimalField()
    checkItem7 = fields.DecimalField()
    checkItem8 = fields.DecimalField()
    checkItem9 = fields.DecimalField()

    # D0
    checkItem101 = fields.DecimalField()
    checkItem102 = fields.DecimalField()
    checkItem103 = fields.DecimalField()
    checkItem104 = fields.DecimalField()
    checkItem107 = fields.DecimalField()
    checkItem108 = fields.DecimalField()
    checkItem109 = fields.DecimalField()

    wx = fields.FloatField()
    alipay = fields.FloatField()

    wx_use_parent = fields.StringField(
        'wx_use_parent',
        default='1'
    )

    license_num = fields.StringField(
        validators=[
            validators.required(),
            validators.Length(min=1, max=32, message=u'无效营业执照注册号'),
            is_has_space
        ]
    )
    license_start_date = fields.DateField(validators=[validators.Required()])
    license_end_date = fields.DateField(
        validators=[
            validators.Optional(),
            validate_license_end_date_upload
        ]
    )
    license_period = fields.StringField(
        'licensePeriod',
        validators=[
            # validators.Optional(),
            validate_license_period_upload
        ]
    )
    license_scope = fields.TextAreaField(
        validators=[
            validators.Length(max=500, message=u'营业范围内容太长')
        ]
    )
    license_img = fields.StringField(
        validators=[validators.Length(min=4, max=255, message=u'无效文件名')]
    )
    dt_sub_id = fields.IntegerField(validators=[validators.Optional(),
                                                dist_form_utils.validate_dt_sub_id_enable])


class AddChainGeneralForm(BaseForm):
    contact = fields.StringField(validators=[validators.Length(
        min=2, max=20, message=u'无效联系人姓名'), is_has_space])
    mobile = fields.StringField(validators=[validators.Length(
        min=11, max=11, message=u'手机号必须为11位'), is_has_space])
    email = fields.StringField(
        validators=[validators.Email(message=u'无效邮箱'), is_has_space])

    chain_shortname = fields.StringField(
        validators=[validators.Length(min=2, max=64, message=u'无效商户简称'), is_has_space])
    industry_no = fields.StringField(
        validators=[validate_industry_code, is_has_space])
    area = fields.StringField()
    cmbProvince = fields.StringField()
    cmbCity = fields.StringField()
    cmbArea = fields.StringField()
    service_phone = fields.StringField(
        validators=[validators.Length(min=5, max=15, message=u'无效客服电话'), validate_service_phone, is_has_space])

    chain_name = fields.StringField(
        validators=[validators.Length(min=2, max=64, message=u'无效商户名'), is_has_space])
    province = fields.StringField(validators=[validators.Length(
        min=2, max=32, message=u'无效省份'), is_has_space])
    city = fields.StringField(validators=[validators.Length(
        min=2, max=32, message=u'无效城市'), is_has_space])
    address = fields.StringField(validators=[validators.Length(
        min=2, max=255, message=u'无效地址'), is_has_space])

    id_card_no = fields.StringField(
        validators=[validators.Length(min=1, max=20, message=u'无效身份证号码'), is_has_space])
    id_card_img_f = fields.FileField('imgCardFront', validators=[File])
    id_card_img_b = fields.FileField('imgCardBack', validators=[File])

    license_num = fields.StringField(
        validators=[
            validators.required(),
            validators.Length(min=1, max=32, message=u'无效营业执照注册号')
        ]
    )
    license_start_date = fields.DateField(validators=[validators.Required()])
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
    license_scope = fields.TextAreaField(
        validators=[
            validators.Length(max=500, message=u'营业范围内容太长')
        ]
    )
    license_img = fields.FileField(
        'licenseImg',
        validators=[File]
    )

    balance_type = fields.IntegerField(
        validators=[validators.NumberRange(min=1, max=2, message=u'无效结算账号类型'), is_has_space])
    balance_name = fields.StringField(
        validators=[validators.Length(min=1, max=255, message=u'无效结算户名'), is_has_space])
    bank_no = fields.StringField(
        validators=[validators.Length(min=12, max=13, message=u'无效支联代码'), is_has_space])
    bankName = fields.StringField()
    balance_account = fields.StringField(
        validators=[validators.Length(min=9, max=22, message=u'无效结算账户'), is_has_space])

    payment_type1 = fields.DecimalField()
    payment_type2 = fields.DecimalField()
    payment_type3 = fields.DecimalField()
    payment_type4 = fields.DecimalField()
    payment_type7 = fields.DecimalField()
    payment_type8 = fields.DecimalField()
    payment_type9 = fields.DecimalField()

    payment_type101 = fields.DecimalField()
    payment_type102 = fields.DecimalField()
    payment_type103 = fields.DecimalField()
    payment_type104 = fields.DecimalField()
    payment_type107 = fields.DecimalField()
    payment_type108 = fields.DecimalField()
    payment_type109 = fields.DecimalField()

    # D0提现手续费
    wx = fields.DecimalField()

    alipay = fields.DecimalField()

    dt_sub_id = fields.IntegerField(validators=[
        validators.Optional(), dist_form_utils.validate_dt_sub_id_exists,
    ])


class ChainSearch(BaseForm):
    # 列出渠道商的商户
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    activated_status = fields.IntegerField(
        validators=[validators.optional(), validators.AnyOf([0, 1, 2])], default=0)
    dt_name = fields.StringField()
    auth_status = fields.IntegerField(
        validators=[validators.optional(), validators.AnyOf([0, 1, 2, 3, 4])], default=0)
    total_num = fields.IntegerField()
    dt_id = fields.StringField()


class ModifyChainlnlet(BaseForm):
    # 连锁商户名称和行业类别不可变
    contact = fields.StringField(validators=[validators.Length(
        min=2, max=20, message=u'无效联系人姓名'), is_has_space])
    mobile = fields.StringField(validators=[validators.Length(
        min=11, max=11, message=u'手机号必须为11位'), is_has_space])
    email = fields.StringField(
        validators=[validators.Email(message=u'无效邮箱'), is_has_space])

    chain_shortname = fields.StringField(
        validators=[validators.Length(min=2, max=64, message=u'无效商户简称'), is_has_space])
    industry_no = fields.StringField(
        validators=[validators.optional(), validate_industry_code, is_has_space])
    area = fields.StringField()
    cmbProvince = fields.StringField()
    cmbCity = fields.StringField()
    cmbArea = fields.StringField()
    service_phone = fields.StringField(
        validators=[validators.Length(min=5, max=15, message=u'无效客服电话'), validate_service_phone, is_has_space])

    chain_name = fields.StringField(
        validators=[validators.optional(), validators.Length(min=2, max=64, message=u'无效商户名'), is_has_space])
    province = fields.StringField(validators=[validators.Length(
        min=2, max=32, message=u'无效省份'), is_has_space])
    city = fields.StringField(validators=[validators.Length(
        min=2, max=32, message=u'无效城市'), is_has_space])
    address = fields.StringField(validators=[validators.Length(
        min=2, max=255, message=u'无效地址'), is_has_space])

    id_card_no = fields.StringField(
        validators=[validators.Length(min=1, max=20, message=u'无效身份证号码'), is_has_space])
    id_card_img_f = fields.FileField('imgCardFront', validators=[File])
    id_card_img_b = fields.FileField('imgCardBack', validators=[File])

    license_num = fields.StringField(
        validators=[
            validators.required(),
            validators.Length(min=1, max=32, message=u'无效营业执照注册号')
        ]
    )
    license_start_date = fields.DateField(validators=[validators.Required()])
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
    license_scope = fields.TextAreaField(
        validators=[
            validators.Length(max=500, message=u'营业范围内容太长')
        ]
    )
    license_img = fields.FileField(
        'licenseImg',
        validators=[File]
    )

    balance_type = fields.IntegerField(
        validators=[validators.NumberRange(min=1, max=2, message=u'无效结算账号类型'), is_has_space])
    balance_name = fields.StringField(
        validators=[validators.Length(min=1, max=255, message=u'无效结算户名'), is_has_space])
    bank_no = fields.StringField(
        validators=[validators.Length(min=12, max=13, message=u'无效支联代码'), is_has_space])
    bankName = fields.StringField()
    balance_account = fields.StringField(
        validators=[validators.Length(min=9, max=22, message=u'无效结算账户'), is_has_space])

    payment_type1 = fields.DecimalField()
    payment_type2 = fields.DecimalField()
    payment_type3 = fields.DecimalField()
    payment_type4 = fields.DecimalField()
    payment_type7 = fields.DecimalField()
    payment_type8 = fields.DecimalField()
    payment_type9 = fields.DecimalField()

    payment_type101 = fields.DecimalField()
    payment_type102 = fields.DecimalField()
    payment_type103 = fields.DecimalField()
    payment_type104 = fields.DecimalField()
    payment_type107 = fields.DecimalField()
    payment_type108 = fields.DecimalField()
    payment_type109 = fields.DecimalField()

    # D0提现手续费
    wx = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000000, message=u'D0-微信手续费设置错误'),
            form_verify.range_fee
        ]
    )

    alipay = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000000, message=u'D0-支付宝手续费设置错误'),
            form_verify.range_fee
        ]
    )

    dt_sub_id = fields.IntegerField(validators=[
        validators.Optional(), dist_form_utils.validate_dt_sub_id_exists,
    ])


class ResendMchActiveEmail(BaseForm):
    # 获取商户信息ajax接口
    mch_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'商户ID不能为空'), validate_mch_id])
