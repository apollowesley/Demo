# -*- coding: utf-8 -*-
from uline.utils.form import BaseForm
from wtforms import validators, fields, ValidationError
from uline.public.baseDB import DbClient

db = DbClient()


def validate_mch_id(form, field):
    ret = db.selectSQL("SELECT 1 FROM mch_inlet_info WHERE mch_id=%s",
                       (field.data,))
    if not ret:
        raise ValidationError(u'该商户号不存在,请确认输入')


class LoginForm(BaseForm):
    mch_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_mch_id])
    password = fields.PasswordField(validators=[validators.required()])


class ChangePasswordForm(BaseForm):
    mch_id = fields.StringField(
        validators=[validators.required(), validators.length(min=5, max=64)])


class AuthCodeForm(BaseForm):
    auth_code = fields.StringField(
        validators=[validators.length(min=5, max=6)])


class ModifyPasswordForm(BaseForm):
    newPwd = fields.StringField(
        validators=[validators.length(min=5, max=20), validators.required()])
    checkPwd = fields.StringField(
        validators=[validators.length(min=5, max=20), validators.required()])


class ForgetPasswordForm(BaseForm):
    mch_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'请输入合法的商户号'), validate_mch_id])


class AuthTokenForm(BaseForm):
    token = fields.StringField(validators=[validators.required()])


class AuthCodeTokenForm(BaseForm):
    auth_code = fields.StringField(
        validators=[validators.length(min=5, max=6)])
    token = fields.StringField(validators=[validators.required()])


class ModifyPasswordTokenForm(BaseForm):
    newPwd = fields.StringField(validators=[validators.length(min=5, max=20)])
    checkPwd = fields.StringField(
        validators=[validators.length(min=5, max=20)])
    token = fields.StringField(validators=[validators.required()])
