#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/9/16'

from wtforms import validators, fields, ValidationError
import uline.handlers.app.distributor.utils.form as dist_form_utils
from uline.utils.form import BaseForm
from uline.public.baseTradeDB import TradeDbClient
from uline.public.baseDB import DbClient
import uline.utils.form as form_utils

tdb = TradeDbClient()
db = DbClient()


def validate_wx_id(form, fields):
    ret = tdb.selectSQL(
        """select 1 from orders where out_trade_no=%s;""", (fields.data,))
    if not ret:
        raise ValidationError(u'该uline订单号不存在')


def validate_mch_id(form, fields):
    ret = db.selectSQL("""
        select 1 from mch_inlet_info where cs_id=%s and mch_id=%s;
    """, (form.cs_id, fields.data,))

    if not ret:
        raise ValidationError(u'不存在此门店')


def validate_wx_rid(form, fields):
    ret = tdb.selectSQL(
        """select 1 from order_refunds where out_refund_no=%s;""", (fields.data,))
    if not ret:
        raise ValidationError(u'该退款订单号不存在')


def validate_refund_password_long(form, field):
    if len(str(field.data)) != 6:
        raise ValidationError(u'请输入6位数字密码')


def validate_refund_fee(form, field):
    refund_fee = int(float(field.data) * 100)
    if refund_fee <= 0:
        raise ValidationError(u'可退金额不能小等于0')


class MerchantTradeSearch(BaseForm):
    mch_name = fields.StringField()
    complete_at_start = fields.DateTimeField(
        validators=[validators.Optional()])
    complete_at_end = fields.DateTimeField(validators=[validators.Optional()])
    # create_at_start = fields.DateField(validators=[validators.Optional()])
    # create_at_end = fields.DateField(validators=[validators.Optional()])
    trade_state = fields.StringField(validators=[validators.Optional(),
                                                 validators.AnyOf(['SUCCESS', 'REFUND', 'NOTPAY', 'CLOSED',
                                                                   'REVOKED', 'USERPAYING', 'PAYERROR'])])
    trade_type = fields.StringField(validators=[validators.Optional(),
                                                validators.AnyOf(['JSAPI', 'NATIVE', 'APP', 'MICROPAY', 'MWEB',
                                                                  'ALIPAY.JSAPI', 'ALIPAY.NATIVE',
                                                                  'ALIPAY.MICROPAY',
                                                                  'JDPAY.JSAPI', 'JDPAY.NATIVE',
                                                                  'JDPAY.MICROPAY', 'JDPAY.H5',
                                                                  'JDPAY.H5_DEBIT'])])
    out_trade_no = fields.StringField()
    mch_trade_no = fields.StringField()
    wx_transaction_id = fields.StringField()
    channel = fields.StringField(validators=[validators.Optional(),
                                             validators.AnyOf(['weixin', 'alipay', 'jdpay'])])
    total_num = fields.IntegerField()
    mch_id = fields.StringField()
    chain_sub_id = fields.IntegerField(validators=[
        validators.Optional(), dist_form_utils.validate_dt_sub_id_exists,
    ])


class MerchantTradeList(BaseForm):
    out_trade_no = fields.StringField(validators=[validators.Length(
        min=20, max=32, message=u'无效的微信订单号'), validate_wx_id])


class MerchantRefundSearch(BaseForm):
    mch_name = fields.StringField()
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])

    refund_status = fields.StringField(validators=[validators.Optional(),
                                                   validators.AnyOf(['SUCCESS', 'FAIL', 'PROCESSING', 'CHANGE'])])
    mch_refund_no = fields.StringField()
    out_refund_no = fields.StringField()
    refund_id = fields.StringField()

    mch_trade_no = fields.StringField()
    out_trade_no = fields.StringField()
    transaction_id = fields.StringField()
    channel = fields.StringField(validators=[validators.Optional(),
                                             validators.AnyOf(['weixin', 'alipay', 'jdpay'])])
    total_num = fields.IntegerField()
    mch_id = fields.StringField()
    chain_sub_id = fields.IntegerField(validators=[
        validators.Optional(), dist_form_utils.validate_dt_sub_id_exists,
    ])


class MerchantRefundList(BaseForm):
    out_refund_no = fields.StringField(
        validators=[validators.Length(min=12, max=32, message=u'无效的退款给订单号'), validate_wx_rid])


class MerchanCanRefund(BaseForm):
    mch_id = fields.StringField()
    out_trade_no = fields.StringField(validators=[validators.Length(
        min=20, max=32, message=u'无效的订单号'), validate_wx_id])


class MerchanInitiateRefund(BaseForm):
    mch_id = fields.StringField(validators=[validate_mch_id])
    Pwd = fields.StringField(validators=[validate_refund_password_long])
    out_trade_no = fields.StringField(validators=[validators.Length(
        min=20, max=32, message=u'无效的订单号'), validate_wx_id])
    refund_fee = fields.StringField(validators=[validate_refund_fee])