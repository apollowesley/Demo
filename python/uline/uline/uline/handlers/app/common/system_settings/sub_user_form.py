# -*- coding: utf-8 -*-

import re
from .common import (get_login_suffix, get_employee_login, auth_junior_id,
                     auth_employee_role, get_headquarters, get_modify_id_sys_code, get_user_profile)
from wtforms import validators, fields, ValidationError
from uline.model.uline.base import uline_session
import uline.utils.form as form_utils
from uline.model.uline.user import Employee, UnionEmployee, BkUser
from uline.model.uline.info import UserProfile
from uline.model.uline.other import SysType


def auth_real_employee_id(form, field):
    query = uline_session.query(Employee.id).filter(
        Employee.id == field.data).first()
    if not query:
        raise ValidationError(u'员工账号%s不存在,请联系客服' % str(field.data))


def auth_email(form, field):
    sys_type_code = form.sys_type_code
    if sys_type_code in ["bk", "ibk"]:
        new_email = uline_session.query(BkUser.email).filter(BkUser.email == field.data).first()
        if new_email:
            raise ValidationError(u'邮箱存在请更换邮箱重试')

        if hasattr(form, 'modify_id'):
            sys_type = uline_session.query(SysType).filter(SysType.code == "bk").one()
            all_email = uline_session.query(UserProfile).\
                join(Employee, Employee.user_id == UserProfile.id).\
                filter(Employee.sys_type_id == sys_type.id, UserProfile.email == field.data).all()
            if all_email:
                old_email = get_user_profile(form.modify_id.data)
                if len(all_email) == 1 and all_email[0].email != old_email.email:
                    raise ValidationError(u'邮箱存在请更换邮箱重试')


def validate_login_name(form, field):

    if field.data.find("@") == -1 or field.data.count("@") > 1:
        raise ValidationError(u'登录名不符合规则,请重新输入')

    user_defined, suffix = field.data.split("@")

    if user_defined.isdigit():
        raise ValidationError(u'登录名自定义部分不可以是纯数字,请重新输入')

    if not re.match(r'^[a-zA-Z0-9@]+$', user_defined):
        raise ValidationError(u'登录账号只允许英文字母和数字')

    employee_id = form.employee_id
    sys_type_code = form.sys_type_code
    employee = get_employee_login(employee_id)
    suffix_before = get_login_suffix(employee, sys_type_code)
    if ("@" + suffix) != suffix_before:
        raise ValidationError(u'登录名不符合平台规则,请重新输入')

    employee_ = uline_session.query(Employee).filter(Employee.login_name == field.data).first()

    if not hasattr(form, 'modify_id') and employee_:
        raise ValidationError(u'员工账号已经存在,请重新输入')
    if hasattr(form, 'modify_id'):
        employee_modify = uline_session.query(Employee.id).filter(Employee.login_name == field.data).all()
        if len(employee_modify) == 1 and employee_modify[0][0] != form.modify_id.data:
            raise ValidationError(u'员工账号已经存在,请重新输入')

        sys_type_code = get_modify_id_sys_code(form.modify_id.data)
        if sys_type_code == "mr":
            if not form.headquarters.data:
                raise ValidationError(u'连锁商户需要携带总部,门店区分参数')
            old_headquarters = get_headquarters(form.modify_id.data)
            if old_headquarters != form.headquarters.data:
                raise ValidationError(u'员工账号不支持总部,门店切换')

    # 连锁商户验证门店信息
    if sys_type_code == "mr":
        if not form.headquarters.data:
            raise ValidationError(u'连锁商户需要携带总部,门店区分参数')
        if form.headquarters.data == 1:
            if not isinstance(form.junior_ids, list):
                raise ValidationError(u'门店参数错误,请重新尝试')
            if not form.junior_ids:
                raise ValidationError(u'连锁商户门店员工需要携带门店信息')
            if not auth_junior_id(form.junior_ids, employee_id):
                raise ValidationError(u'门店信息错误,请重新尝试')

    # 验证角色信息
    if form.employee_role:
        if not isinstance(form.employee_role, list):
            raise ValidationError(u'角色参数错误,请重新尝试')
        if not auth_employee_role(form.employee_role, sys_type_code, employee_id, form.headquarters.data):
            raise ValidationError(u'角色信息错误,请重新尝试')


class SubUserIndexForm(form_utils.BaseForm):
    """列出所有的渠道商子账户"""

    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    status = fields.IntegerField(validators=[validators.Optional(), validators.AnyOf([0, 1, 2])])
    employee_name = fields.StringField(validators=[validators.Optional()])
    mch_id = fields.IntegerField(validators=[validators.Optional()])
    employee_id = fields.StringField(validators=[validators.Optional()])
    role_id = fields.IntegerField(validators=[validators.Optional()])
    p = fields.IntegerField(validators=[validators.Optional()])


class SubUserForm(form_utils.BaseForm):

    # 1代表不属于总部,2代表属于总部
    headquarters = fields.IntegerField(validators=[validators.Optional(), validators.any_of([1, 2])])

    login_name = fields.StringField(validators=[
        validators.DataRequired(message=u'登录账号不能为空'),
        validators.Length(min=2, max=64, message=u'登录账户长度必须为2到64个字符'),
        form_utils.is_has_space, validate_login_name])

    name = fields.StringField(validators=[
        validators.DataRequired(message=u'员工姓名不能为空'),
        form_utils.is_has_space,
        validators.Length(min=2, max=64, message=u'员工姓名长度必须为2到64个字符')])

    phone1 = fields.StringField(validators=[
        form_utils.is_has_space, form_utils.validate_phone])
    status = fields.IntegerField(validators=[validators.AnyOf([1, 2])])

    email = fields.StringField(
        validators=[validators.Email(message=u'无效邮箱'), auth_email])


class SubUserEditForm(SubUserForm):
    modify_id = fields.IntegerField(validators=[validators.DataRequired(message=u'子账户id不能为空'), auth_real_employee_id])


class SubUserInfoForm(form_utils.BaseForm):
    employee_id = fields.IntegerField(validators=[validators.DataRequired(message=u'子账户id不能为空'), auth_real_employee_id])


class GenerateQrcode(form_utils.BaseForm):
    employee_id = fields.StringField(
        validators=[validators.required(message=u'子账户id不能为空'), auth_real_employee_id])


class BindingStatus(GenerateQrcode):
    binding_status = fields.IntegerField(
        validators=[validators.required(), validators.any_of([1, 2])])
    employee_id = fields.StringField(
        validators=[validators.required(), auth_real_employee_id])
