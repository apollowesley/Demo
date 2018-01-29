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

def validate_refund_password_long(form, field):
    if len(str(field.data)) != 6:
        raise ValidationError(u'请输入6位数字密码')

class ValidationRefundPasswordForm(BaseForm):
    Pwd = fields.IntegerField(validators=[validate_refund_password_long])

class EmployeeFollowWeChat(BaseForm):
    employee_name = fields.IntegerField(validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_mch_id])

class AuthCodeForm(BaseForm):
    auth_code = fields.StringField(validators=[validators.length(min=5, max=6)])


class ModifyRefundPasswordForm(BaseForm):
    newPwd = fields.IntegerField(validators=[validate_refund_password_long])
    checkPwd = fields.IntegerField(validators=[validate_refund_password_long])


class ModifyRefundPasswordTokenForm(BaseForm):
    newPwd = fields.IntegerField(validators=[validators.length(min=6, max=6)])
    checkPwd = fields.IntegerField(validators=[validators.length(min=6, max=6)])
    token = fields.StringField(validators=[validators.required()])