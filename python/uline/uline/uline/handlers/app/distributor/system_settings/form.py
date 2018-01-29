# -*- coding: utf-8 -*-

from wtforms import validators, fields, ValidationError
import uline.utils.form as form_utils


class ResendEmailForm(form_utils.BaseForm):
    resend_date = fields.StringField(validators=[validators.DataRequired()])
