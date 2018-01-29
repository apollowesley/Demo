#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wtforms import validators, fields
from uline_risk.utils.form import BaseForm


class MerchantRiskSearchForm(BaseForm):
    has_risk = fields.IntegerField(validators=[validators.Optional(), validators.AnyOf([0, 1, 2])], default=0)
    risk_type = fields.StringField(validators=[validators.Optional(),
                                               validators.AnyOf(['cert_no', 'bank_card_no', 'business_license_no'])])
    risk_content = fields.StringField(validators=[validators.Optional()])
    risk_id = fields.IntegerField(validators=[validators.Optional()], default=0)
    page = fields.IntegerField(validators=[validators.Optional()])
    page_size = fields.IntegerField(validators=[validators.Optional()])
