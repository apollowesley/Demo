#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/9/16'

from wtforms import validators, fields, ValidationError
from uline.utils.form import IdCard, File, BaseForm
from uline.public.baseDB import DbClient

db = DbClient()


def validate_mdbn(form, fields):
    ret = db.selectSQL(
        """select 1 from mch_daily_balance_info where mch_daily_balance_no=%s;""", (fields.data,))
    if not ret:
        raise ValidationError(u'该商户结算编号不存在')


def validate_ddbn(form, fields):
    ret = db.selectSQL(
        """select 1 from dt_daily_balance_info where dt_daily_balance_no=%s;""", (fields.data,))
    if not ret:
        raise ValidationError(u'该渠道商结算编号不存在')


class MerchantBalanceSearch(BaseForm):
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    pay_status = fields.IntegerField(
        validators=[validators.optional(), validators.AnyOf([0, 1, 2, 3])])
    mch_name = fields.StringField()
    dt_name = fields.StringField()
    channel = fields.StringField(validators=[validators.Optional(),
                                             validators.AnyOf(['weixin', 'alipay', 'jdpay'])])
    total_num = fields.IntegerField()
    dt_id = fields.StringField()
    mch_id = fields.StringField()
    balance_account = fields.StringField()
    cs_mch_id = fields.StringField()
    cs_mch_shortname = fields.StringField()
    bk_name = fields.StringField()
    bk_id = fields.StringField()
    # 0 全部 1 主银行拓展  2 同业银行拓展
    expand_type = fields.IntegerField(validators=[validators.AnyOf([0, 1, 2])], default=0)


class MerchantBalanceList(BaseForm):
    mdb_no = fields.IntegerField(validators=[validate_mdbn])


class InterbankBalanceSearch(BaseForm):
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    channel = fields.StringField(validators=[validators.Optional(),
                                             validators.AnyOf(['weixin', 'alipay'])])
    pay_status = fields.IntegerField(validators=[validators.optional(), validators.AnyOf([0, 1, 2, 3])])
    bk_name = fields.StringField()
    bk_id = fields.StringField()
    balance_account = fields.StringField()


class DistributorBalanceSearch(BaseForm):
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    pay_status = fields.IntegerField(
        validators=[validators.optional(), validators.AnyOf([0, 1, 2, 3])])
    dt_name = fields.StringField()
    channel = fields.StringField(validators=[validators.Optional(),
                                             validators.AnyOf(['weixin', 'alipay', 'jdpay'])])
    total_num = fields.IntegerField()
    balance_account = fields.StringField()
    dt_id = fields.StringField()
    bk_name = fields.StringField()
    bk_id = fields.StringField()
    # 0 全部 1 主银行拓展  2 同业银行拓展
    expand_type = fields.IntegerField(validators=[validators.AnyOf([0, 1, 2])], default=0)


class DistributorBalanceList(BaseForm):
    ddb_no = fields.IntegerField(validators=[validate_ddbn])