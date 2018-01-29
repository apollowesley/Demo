# -*- coding: utf-8 -*-
from wtforms import validators, fields
from uline.utils.form import BaseForm


class LoginForm(BaseForm):
    email = fields.StringField(
        validators=[validators.Email(), validators.required(), validators.length(min=5, max=64)])
    password = fields.PasswordField(validators=[validators.required()])


class ChangePasswordForm(BaseForm):
    email = fields.StringField(
        validators=[validators.Email(), validators.required(), validators.length(min=5, max=64)])


class AuthCodeForm(BaseForm):
    auth_code = fields.StringField(validators=[validators.length(min=5, max=6)])


class ModifyPasswordForm(BaseForm):
    newPwd = fields.StringField(validators=[validators.length(min=5, max=20)])
    checkPwd = fields.StringField(validators=[validators.length(min=5, max=20)])
