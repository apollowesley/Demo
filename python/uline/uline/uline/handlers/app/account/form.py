# -*- coding: utf-8 -*-
import re

from uline.utils.form import BaseForm
from wtforms import validators, fields, ValidationError
from uline.public.baseDB import DbClient
from uline.model.uline.user import Employee
from uline.model.uline.base import uline_session
db = DbClient()


def query_employee(employee_login_name):
    employee_auth = uline_session.query(Employee.login_name).\
        filter(Employee.login_name == employee_login_name)
    employee_auth = employee_auth.first()
    return True if employee_auth else False


class LoginForm(BaseForm):
    login_name = fields.StringField(validators=[validators.DataRequired(message=u'登录名不能为空')])
    password = fields.PasswordField(validators=[validators.required(message=u'密码不能为空')])


class changelogin(BaseForm):
    cs_id = fields.PasswordField(validators=[validators.DataRequired()])


class ChangePasswordForm(BaseForm):

    platform_type = fields.PasswordField(
        validators=[validators.required(), validators.any_of(["official", "mch", "dist", "bank", "chain"])])
    login_name = fields.StringField(
        validators=[validators.required(), validators.length(min=5, max=64)])


class AuthCodeForm(BaseForm):
    auth_code = fields.StringField(
        validators=[validators.length(min=5, max=6)])


def auth_password(form, field):

    pwd = field.data
    other_pwd = "checkPwd" if field.id == "newPwd" else "newPwd"
    if field.data != form.__getattribute__(other_pwd).data:
        raise ValidationError(u'密码输入不一致,请重新输入.')
    if pwd.find(" ") != -1:
        raise ValidationError(u'密码中不可包含空格,请重新输入密码.')


class ModifyPasswordForm(BaseForm):

    newPwd = fields.StringField(
        validators=[validators.length(min=6, max=20), validators.required(), auth_password])
    checkPwd = fields.StringField(
        validators=[validators.required()])


class ForgetPasswordForm(BaseForm):
    login_name = fields.StringField(validators=[validators.required()])


class AuthTokenForm(BaseForm):
    token = fields.StringField(validators=[validators.required()])
    sys_type_code = fields.PasswordField(validators=[validators.Optional()])


class AuthCodeTokenForm(BaseForm):
    auth_code = fields.StringField(
        validators=[validators.length(min=5, max=6)])
    token = fields.StringField(validators=[validators.required()])
    sys_type_code = fields.PasswordField(
        validators=[validators.Optional()])


class ModifyPasswordTokenForm(BaseForm):
    newPwd = fields.StringField(validators=[validators.length(min=6, max=20), auth_password])
    checkPwd = fields.StringField()
    token = fields.StringField(validators=[validators.required()])
    sys_type_code = fields.PasswordField(validators=[validators.Optional()])
