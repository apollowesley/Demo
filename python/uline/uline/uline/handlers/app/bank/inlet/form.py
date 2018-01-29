#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/9/16'

from wtforms import validators, fields, ValidationError, RadioField
from uline.utils.form import IdCard, File, BaseForm
from uline.public.baseDB import DbClient
from uline.public.constants import PAY_TYPES, AUTH_STATUS

db = DbClient()


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
    # 0 全部 1 主银行拓展  2 同业银行拓展
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


class BankInfo(BaseForm):
    # 列出渠道商的商户
    q = fields.StringField(
        validators=[validators.DataRequired(message=u'查询字符不能为空')])
    page = fields.IntegerField(
        validators=[validators.Optional(),
                    validators.NumberRange(min=1, max=1000)])


def validate_mch_id(form, field):
    ret = db.selectSQL("SELECT count(*) FROM mch_inlet_info WHERE mch_id=%s",
                       (field.data,))
    if not ret[0]:
        raise ValidationError(u'该商户号不存在,请确认输入')


def validate_dt_id(form, field):
    ret = db.selectSQL("SELECT count(*) FROM dt_inlet_info WHERE dt_id=%s",
                       (field.data,))
    if not ret[0]:
        raise ValidationError(u'该商户号不存在,请确认输入')


def validate_chain_id(form, field):
    ret = db.selectSQL("SELECT count(*) FROM dt_inlet_info WHERE dt_id=%s and parent_id NOTNULL",
                       (field.data,))
    if not ret[0]:
        raise ValidationError(u'该商户号不存在,请确认输入')


class GetMerchantInfo(BaseForm):
    # 获取商户信息ajax接口
    mch_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_mch_id])


class AuthMerchantInfo(BaseForm):
    # 获取商户信息ajax接口
    mch_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_mch_id])


class DenyMerchantInfo(BaseForm):
    # 获取商户信息ajax接口
    mch_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_mch_id])
    comment = fields.TextAreaField(
        validators=[validators.Length(min=0, max=1500, message=u'无效驳回原因')])


class ActivatedBatchMerchantInfo(BaseForm):
    # 获取商户信息ajax接口
    mch_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_mch_id])


class ActivatedMerchantInfo(BaseForm):
    # 获取商户信息ajax接口
    mch_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_mch_id])
    # pay_type = fields.IntegerField(validators=[validators.AnyOf(PAY_TYPES)])
    pay_type = fields.StringField()


class AuthDistributorInfo(BaseForm):
    # 获取商户信息ajax接口
    dt_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_dt_id])


class DenyDistributorInfo(BaseForm):
    # 获取商户信息ajax接口
    dt_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_dt_id])
    comment = fields.TextAreaField(
        validators=[validators.Length(min=0, max=1500, message=u'无效驳回原因')])


class CloseDistributorPayment(BaseForm):
    # 关闭渠道商某一个支付类型
    dt_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'渠道商id不能为空'), validate_dt_id])
    # payment_type = fields.IntegerField()
    payment_type = fields.StringField()


class CloseBatchDistributorPayment(BaseForm):
    # 批量关闭渠道商支付类型
    dt_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'渠道商id不能为空'), validate_dt_id])


class CloseMerchantPayment(BaseForm):
    # 关闭商户某一个支付类型
    mch_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'商户id不能为空'), validate_mch_id])
    payment_type = fields.StringField()


class CloseBatchMerchantPayment(BaseForm):
    # 批量关闭商户支付类型
    mch_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'商户id不能为空'), validate_mch_id])


class ActivatedBatchDistributorInfo(BaseForm):
    # 获取商户信息ajax接口
    dt_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_dt_id])


class ActivatedDistributorInfo(BaseForm):
    # 获取商户信息ajax接口
    dt_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_dt_id])
    # pay_type = fields.IntegerField(validators=[validators.AnyOf(PAY_TYPES)])
    pay_type = fields.StringField()


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
    # 0 全部 1 主银行拓展  2 同业银行拓展
    expand_type = fields.IntegerField(validators=[validators.AnyOf([0, 1, 2])], default=0)


class ChainSearch(BaseForm):
    # 列出渠道商的商户
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    activated_status = fields.IntegerField(
        validators=[validators.Optional(), validators.AnyOf([0, 1, 2])])
    dt_name = fields.StringField()
    auth_status = fields.IntegerField(
        validators=[validators.Optional(), validators.AnyOf([0] + [int(key) for key in AUTH_STATUS])], default=0)
    total_num = fields.IntegerField()
    dt_id = fields.StringField()
    parent_id = fields.StringField()
    parent_name = fields.StringField()

    bk_name = fields.StringField()
    bk_id = fields.StringField()
    # 0 全部 1 主银行拓展  2 同业银行拓展
    expand_type = fields.IntegerField(validators=[validators.AnyOf([0, 1, 2])], default=0)


class GetDistributorInfo(BaseForm):
    # 获取商户信息ajax接口
    dt_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_dt_id])


class CSSearch(BaseForm):
    # 列出渠道商的商户
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    activated_status = fields.IntegerField(
        validators=[validators.Optional(), validators.AnyOf([0, 1, 2])])
    auth_status = fields.IntegerField(
        validators=[validators.Optional(), validators.AnyOf([0] + [int(key) for key in AUTH_STATUS])], default=0)
    total_num = fields.IntegerField()

    cs_id = fields.StringField()
    cs_name = fields.StringField()
    mch_id = fields.StringField()
    short_name = fields.StringField()

    bk_name = fields.StringField()
    bk_id = fields.StringField()
    # 0 全部 1 主银行拓展  2 同业银行拓展
    expand_type = fields.IntegerField(validators=[validators.AnyOf([0, 1, 2])], default=0)


class ActivatedChainInfo(BaseForm):
    # 获取商户信息ajax接口
    dt_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_chain_id])
    pay_type = fields.IntegerField(validators=[validators.AnyOf(PAY_TYPES)])


class CloseChainInfo(BaseForm):
    # 获取商户信息ajax接口
    dt_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_chain_id])
    payment_type = fields.IntegerField(validators=[validators.AnyOf(PAY_TYPES)])


class ActivatedBatchChainInfo(BaseForm):
    # 获取商户信息ajax接口
    dt_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_chain_id])


class CloseBatchChainPayment(BaseForm):
    # 获取商户信息ajax接口
    dt_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_chain_id])


class GetMerchanWxConfig(BaseForm):
    # 获取商户微信配置ajax接口
    mch_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_mch_id])
    refresh = fields.IntegerField(validators=[validators.Optional()], default=1)


class GetChainWxConfig(BaseForm):
    # 获取商户信息ajax接口
    mch_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_dt_id])
    refresh = fields.IntegerField(validators=[validators.Optional()], default=1)


class InterBankSearch(BaseForm):
    # 列出银行的同业银行
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    bk_name = fields.StringField()
    bk_id = fields.StringField()
