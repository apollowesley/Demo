#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wtforms import validators, fields, ValidationError
from uline.utils.form import BaseForm
from uline.public.baseTradeDB import TradeDbClient


class MchSubsidizeSearch(BaseForm):
    status = fields.IntegerField(validators=[validators.Optional(), validators.AnyOf([0, 1, 2])])
    mch_id = fields.StringField()
    mch_name = fields.StringField()
    dt_id = fields.StringField()
    dt_name = fields.StringField()


class MchSubsidizeDetailForm(BaseForm):
    role_id = fields.IntegerField()


class MchSubsidizeAddForm(BaseForm):
    role_id = fields.IntegerField()
    status = fields.IntegerField(validators=[validators.Optional()], default=1)
    weixin = fields.IntegerField(
        validators=[validators.Optional(), validators.NumberRange(0, 100, message=u'微信支付优惠比例为0~100')])
    alipay = fields.IntegerField(
        validators=[validators.Optional(), validators.NumberRange(0, 100, message=u'支付宝支付优惠比例为0~100')])


class MchSubsidizeQueryForm(BaseForm):
    role_id = fields.IntegerField()


class MchSubsidizeModifyForm(BaseForm):
    role_id = fields.IntegerField()
    status = fields.IntegerField(validators=[validators.Optional()], default=1)
    weixin = fields.IntegerField(
        validators=[validators.Optional(), validators.NumberRange(0, 100, message=u'微信优惠比例为0~100')])
    alipay = fields.IntegerField(
        validators=[validators.Optional(), validators.NumberRange(0, 100, message=u'支付宝支付优惠比例为0~100')])
