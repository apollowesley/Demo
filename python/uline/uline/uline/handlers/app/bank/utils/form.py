# -*- coding: utf-8 -*-
from wtforms import validators, fields, ValidationError
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
