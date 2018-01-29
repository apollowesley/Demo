# -*- coding: utf-8 -*-
from __future__ import division
from uline.utils.form import File, BaseForm
from wtforms import validators, fields, ValidationError


class WithdrawForm(BaseForm):
    role = fields.IntegerField(
        validators=[validators.DataRequired(message=u'role is required')])
    role_type = fields.StringField(
        validators=[validators.DataRequired(message=u'role_type is required')])
