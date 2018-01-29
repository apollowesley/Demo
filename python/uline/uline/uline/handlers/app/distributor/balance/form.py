#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/9/16'

from wtforms import validators, fields, ValidationError

import uline.handlers.app.distributor.utils.form as dist_form_utils
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
    channel = fields.StringField(validators=[validators.Optional(),
                                             validators.AnyOf(['weixin', 'alipay', 'jdpay'])])
    total_num = fields.IntegerField()
    mch_id = fields.StringField()
    dt_sub_id = fields.IntegerField(validators=[
        validators.Optional(), dist_form_utils.validate_dt_sub_id_exists,
    ])
    cs_mch_short_name = fields.StringField()
    cs_mch_id = fields.StringField()


class MerchantBalanceList(BaseForm):
    mdb_no = fields.StringField(validators=[validate_mdbn])


class DistributorBalanceSearch(BaseForm):
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    pay_status = fields.IntegerField(
        validators=[validators.optional(), validators.AnyOf([0, 1, 2, 3])])
    channel = fields.StringField(validators=[validators.Optional(),
                                             validators.AnyOf(['weixin', 'alipay', 'jdpay'])])
    total_num = fields.IntegerField()


class DistributorBalanceList(BaseForm):
    ddb_no = fields.StringField(validators=[validate_ddbn])
