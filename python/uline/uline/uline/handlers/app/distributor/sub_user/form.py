# -*- coding: utf-8 -*-

from wtforms import validators, fields, ValidationError

import uline.handlers.app.distributor.utils.form as dist_form_utils
from uline.model.uline.base import uline_session
from uline.model.uline.base import DtSubUser

import uline.utils.form as form_utils


def validate_login_name(form, field):
    login_name = field.data
    if len(login_name.split('@')) != 2:
        raise ValidationError(u'账号格式不对,请重新输入: 自定义名@渠道商号')

    name_part, dt_id_from_user = login_name.split('@')
    if not name_part.isalnum():
        raise ValidationError(u'登录账号只允许英文字母和数字')

    if str(dt_id_from_user) != str(form.dt_id):
        raise ValidationError(u'@后面必须为当前供应商号')

    sub_user = uline_session.query(DtSubUser).filter(DtSubUser.login_name == login_name).one_or_none()
    if sub_user:
        raise ValidationError(u'登录账号已存在,请重新输入')


class SubUserIndexForm(form_utils.BaseForm):
    """列出所有的渠道商子账户"""
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    status = fields.IntegerField(validators=[validators.AnyOf([0, 1, 2])])
    dt_sub_name = fields.StringField(validators=[validators.Optional()])
    total_num = fields.IntegerField(validators=[validators.Optional()])


class SubUserForm(form_utils.BaseForm):
    """列出所有的渠道商子账户"""
    login_name = fields.StringField(validators=[
        validators.DataRequired(message=u'登录账号不能为空'),
        validators.Length(min=2, max=64, message=u'登录账户长度必须为2到64个字符'),
        form_utils.is_has_space, validate_login_name])

    dt_sub_name = fields.StringField(validators=[
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
    pass


class SubUserEditForm(SubUserForm):
    login_name = fields.StringField()
    dt_sub_id = fields.IntegerField(validators=[
        validators.DataRequired(message=u'子账户id不能为空'),
        dist_form_utils.validate_dt_sub_id_exists
    ])


class SubUserInfoForm(form_utils.BaseForm):
    """列出所有的渠道商子账户"""
    dt_sub_id = fields.IntegerField(validators=[
        validators.DataRequired(message=u'子账户id不能为空'),
        dist_form_utils.validate_dt_sub_id_exists
    ])
