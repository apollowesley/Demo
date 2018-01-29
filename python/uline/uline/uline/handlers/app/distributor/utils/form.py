# -*- coding: utf-8 -*-
from wtforms import validators, fields, ValidationError

from uline.model.uline.user import DtSubUser
from uline.utils.form import BaseForm
from uline.public.baseDB import DbClient

db = DbClient()


def validate_order_id(form, fields):
    ret = db.selectSQL(
        """select 1 from order_download_info where order_id=%s and status in (1,2,3,4);""", (fields.data,))
    if not ret:
        raise ValidationError(u'该下载编号不存在')


class OperateExportFile(BaseForm):
    order_id = fields.StringField(
        validators=[validators.Length(min=32, max=32, message=u'无效的下载编号'), validate_order_id])


def validate_dt_sub_id_exists(form, field):
    """验证子账户id必须存在， 而且必须属于该渠道商"""
    validate_dt_sub_id(form, field)


def validate_dt_sub_id_enable(form, field):
    """验证子账户id必须存在， 而且必须属于该渠道商, 而且必须没有禁用"""
    validate_dt_sub_id(form, field, status=1)


def validate_dt_sub_id(form, field, status=None):
    """验证子账户id必须存在是否合法"""
    dt_sub_id = field.data
    if status:
        dt_sub_user = DtSubUser.get_by(dt_sub_id=dt_sub_id, dt_user_dt_id=form.dt_id, status=1).first()#dt_user_dt_id=form.dt_id,
    else:
        dt_sub_user = DtSubUser.get_by(dt_sub_id=dt_sub_id,dt_user_dt_id=form.dt_id).first()#, dt_user_dt_id=form.dt_id
    if dt_sub_user is None:
        raise ValidationError(u'子账户id必须存在且属于该渠道商')
