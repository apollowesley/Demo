# -*- coding: utf-8 -*-

import re
from wtforms import validators, fields, ValidationError

from uline.model.uline.base import uline_session
from uline.model.uline.base import MchSubUser

import uline.utils.form as form_utils
import uline.handlers.app.chain.utils.form as mch_form_utils


def is_has_space(form, field):
    if re.search(r' ', str(field.data)):
        raise ValidationError(str(field.data) + u' 包含空格, 请修改！')


def auth_sub_name(form, field):
    if re.match(r'[\]\[\*\(\)\{\}\^\|\$\&\#\@\!\<\>\,\.\?\~\`\+\-\/\'\"\:\;\=\%]', field.data):
        raise ValidationError(u'查询员工名称 %s 存在特殊字符,请重新输入' % str(field.data))


def auth_real_mch_sub_id(form, field):
    query = uline_session.query(MchSubUser.mch_sub_id).filter(
        MchSubUser.mch_sub_id == field.data).one()
    if len(field.data) != 8 and query[0]:
        raise ValidationError(u'生成二维码失败,原因:员工ID %s 无效,请联系客服' % str(field.data))


def validate_login_name(form, field):
    login_name = field.data
    if len(login_name.split('@')) != 2:
        raise ValidationError(u'账号格式不对,请重新输入: 自定义名@渠道商号')

    name_part, mch_id_from_user = login_name.split('@')
    if not re.match(r'^[a-zA-Z0-9]+$', name_part):
        raise ValidationError(u'登录账号只允许英文字母和数字')

    if str(mch_id_from_user) != str(form.dt_id):
        raise ValidationError(u'@后面必须为当前供应商号')

    sub_user = uline_session.query(MchSubUser).filter(
        MchSubUser.login_name == login_name).one_or_none()
    if sub_user:
        raise ValidationError(u'登录账号已存在,请重新输入')


class SubUserIndexForm(form_utils.BaseForm):
    """列出所有的商户子账户"""
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    status = fields.IntegerField(validators=[validators.AnyOf([0, 1, 2])])
    mch_sub_name = fields.StringField(
        validators=[validators.Optional()])
    total_num = fields.IntegerField(validators=[validators.Optional()])


class SubUserForm(form_utils.BaseForm):
    """列出所有的渠道商子账户"""
    login_name = fields.StringField(validators=[
        validators.DataRequired(message=u'登录账号不能为空'),
        validators.Length(min=2, max=64, message=u'登录账户长度必须为2到64个字符'),
        form_utils.is_has_space, validate_login_name])

    mch_sub_name = fields.StringField(validators=[
        validators.DataRequired(message=u'员工账号不能为空'),
        form_utils.is_has_space,
        validators.Length(min=2, max=64, message=u'员工姓名长度必须为2到64个字符')])

    phone = fields.StringField(validators=[
        form_utils.is_has_space, form_utils.validate_phone])

    email = fields.StringField(
        validators=[validators.Email(message=u'无效邮箱')])

    status = fields.IntegerField(
        validators=[validators.AnyOf([1, 2])])


class SubUserAddForm(SubUserForm):
    mch_id = fields.StringField(validators=[validators.required()])
    # pass


class SubUserEditForm(SubUserForm):
    mch_id = fields.StringField(validators=[validators.required()])
    login_name = fields.StringField()
    mch_sub_id = fields.IntegerField(validators=[
        validators.DataRequired(
            message=u'子账户id不能为空')
    ])


class SubUserInfoForm(form_utils.BaseForm):
    """列出所有的渠道商子账户"""
    mch_sub_id = fields.IntegerField(validators=[
        validators.DataRequired(
            message=u'子账户id不能为空')
    ])


class GenerateQrcode(form_utils.BaseForm):
    mch_sub_id = fields.StringField(
        validators=[validators.required(), auth_real_mch_sub_id])
