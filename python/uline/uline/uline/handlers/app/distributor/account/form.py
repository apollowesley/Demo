# -*- coding: utf-8 -*-
from wtforms import validators, fields, ValidationError
from uline.utils.form import BaseForm
from uline.public.baseDB import DbClient

db = DbClient()


def validate_dt_email(form, field):
    ret = db.selectSQL("select dt_id from dt_user where email=%s and status=2",
                       (field.data,))
    if not ret:
        raise ValidationError(u'该渠道邮箱不存在,请确认输入')


class LoginForm(BaseForm):
    email = fields.StringField(
        validators=[validators.Email(), validators.required(), validators.length(min=5, max=64)])
    password = fields.PasswordField(validators=[validators.required()])


class ChangePasswordForm(BaseForm):
    email = fields.StringField(
        validators=[validators.required(message=u'请输入合法的渠道商邮箱'), validate_dt_email])


class AuthCodeForm(BaseForm):
    auth_code = fields.StringField(validators=[validators.length(min=5, max=6)])


class AuthTokenForm(BaseForm):
    token = fields.StringField(validators=[validators.required()])


class AuthCodeTokenForm(BaseForm):
    auth_code = fields.StringField(validators=[validators.length(min=5, max=6)])
    token = fields.StringField(validators=[validators.required()])


class ModifyPasswordForm(BaseForm):
    newPwd = fields.StringField(validators=[validators.length(min=5, max=20)])
    checkPwd = fields.StringField(validators=[validators.length(min=5, max=20)])


class ModifyPasswordTokenForm(BaseForm):
    newPwd = fields.StringField(validators=[validators.length(min=5, max=20)])
    checkPwd = fields.StringField(validators=[validators.length(min=5, max=20)])
    token = fields.StringField(validators=[validators.required()])
