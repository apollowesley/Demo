# -*- coding: utf-8 -*-
from wtforms import validators, fields, ValidationError

from uline.model.uline.user import DtSubUser, MchUserMchSubUser, MchSubUser
from uline.model.uline.info import MchInletInfo
from uline.utils.form import BaseForm
from uline.public.baseDB import DbClient
from uline.model.uline.base import uline_session
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
    """验证子账户id必须存在， 而且必须属于该连锁商户"""
    validate_dt_sub_id(form, field)


def validate_dt_sub_id_enable(form, field):
    """验证子账户id必须存在， 而且必须属于该连锁商户, 而且必须没有禁用"""
    validate_dt_sub_id(form, field, status=1)


def validate_dt_sub_id(form, field, status=None):
    """验证子账户id必须存在是否合法"""
    dt_sub_id = field.data
    if status:
        dt_sub_user = DtSubUser.get_by(
            dt_sub_id=dt_sub_id, dt_user_dt_id=form.dt_id, status=1).first()  # dt_user_dt_id=form.dt_id,
    else:
        dt_sub_user = DtSubUser.get_by(
            dt_sub_id=dt_sub_id, dt_user_dt_id=form.dt_id).first()  # , dt_user_dt_id=form.dt_id
    if dt_sub_user is None:
        raise ValidationError(u'子账户id必须存在且属于该连锁商户')


def validate_mch_sub_id(form, field):
    """验证子账户id必须存在， 而且必须属于该商户"""
    mch_sub_id = field.data
    dt_id = form.dt_id
    mch_sub_user = uline_session.query(MchInletInfo.cs_id).join(MchUserMchSubUser, MchUserMchSubUser.mch_id == MchInletInfo.mch_id).filter(
        MchUserMchSubUser.mch_sub_id == mch_sub_id).first()
    if mch_sub_user[0] != dt_id:
        raise ValidationError(u'子账户id必须存在且属于该商户')
