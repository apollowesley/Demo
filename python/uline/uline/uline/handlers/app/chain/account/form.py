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


def validate_chain_id(form, field):
    ret = db.selectSQL("select 1 from dt_inlet_info where dt_id=%s and parent_id is not null",
                       (field.data,))
    if not ret:
        raise ValidationError(u'该连锁号不存在,请确认输入')


class LoginForm(BaseForm):
    chain_id = fields.StringField()
    password = fields.PasswordField(validators=[validators.required()])


class ForgetPasswordForm(BaseForm):
    chain_id = fields.IntegerField(
        validators=[validate_chain_id])


class ChangePasswordForm(BaseForm):
    chain_id = fields.StringField(
        validators=[validators.required(), validators.length(min=5, max=64)])


class AuthCodeForm(BaseForm):
    auth_code = fields.StringField(
        validators=[validators.length(min=5, max=6)])


class AuthTokenForm(BaseForm):
    token = fields.StringField(validators=[validators.required()])


class AuthCodeTokenForm(BaseForm):
    auth_code = fields.StringField(
        validators=[validators.length(min=5, max=6)])
    token = fields.StringField(validators=[validators.required()])


class ModifyPasswordForm(BaseForm):
    newPwd = fields.StringField(validators=[validators.length(min=5, max=20)])
    checkPwd = fields.StringField(
        validators=[validators.length(min=5, max=20)])


class ModifyPasswordTokenForm(BaseForm):
    newPwd = fields.StringField(validators=[validators.length(min=5, max=20)])
    checkPwd = fields.StringField(
        validators=[validators.length(min=5, max=20)])
    token = fields.StringField(validators=[validators.required()])
