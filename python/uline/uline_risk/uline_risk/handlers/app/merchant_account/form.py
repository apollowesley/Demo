#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wtforms import validators, fields
from uline_risk.utils.form import BaseForm, BaseOriginForm


class MerchantSettleControl(BaseOriginForm):
    role_id = fields.IntegerField(validators=[validators.DataRequired()])
    role_type = fields.StringField(validators=[validators.DataRequired()])
    # platform = fields.StringField(validators=[validators.DataRequired(),validators.AnyOf(['weixin', 'alipay'])])
    action = fields.StringField(validators=[validators.DataRequired(), validators.AnyOf(['close', 'open'])])


class MerchantCreditControl(BaseOriginForm):
    role_id = fields.IntegerField(validators=[validators.DataRequired()])
    role_type = fields.StringField(validators=[validators.DataRequired()])
    platform = fields.StringField(validators=[validators.DataRequired(), validators.AnyOf(['weixin', 'alipay'])])
    action = fields.StringField(validators=[validators.DataRequired(), validators.AnyOf(['close', 'open'])])


class MerchantRiskInfoControlForm(BaseForm):
    sys_id = fields.IntegerField(validators=[validators.DataRequired()])
    sys_type_id = fields.StringField(validators=[validators.DataRequired()])


class MerchantBalanceStatusForm(BaseForm):
    merchant_id = fields.IntegerField(validators=[validators.DataRequired()])
