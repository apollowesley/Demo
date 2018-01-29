# -*- coding: utf-8 -*-
from wtforms import validators, fields, ValidationError
from uline.utils.form import BaseForm


def check_is_numbers(form, field):
    if not str(field.data).isdigit():
        raise ValidationError(u'请输入纯数字字符')


class query_mch_id(BaseForm):
    charac_id = fields.StringField(
        validators=[validators.Optional(), validators.AnyOf(['1', '2', '3', "5"]), check_is_numbers])
    # charac_account = fields.StringField(validators=[validators.Optional()])
    query_charac = fields.StringField(
        validators=[validators.Optional(), validators.AnyOf(['1', '2', '3']), check_is_numbers])
    id_name = fields.StringField(validators=[validators.Optional()])

# 查询角色 1渠道商,2商户,3门店


class DownloadsBill(BaseForm):
    query_charac = fields.StringField(
        validators=[validators.Optional(), validators.AnyOf(['1', '2', '3'], check_is_numbers)])
    id = fields.StringField(validators=[validators.Optional()])
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    charac_id = fields.StringField(
        validators=[validators.AnyOf(['1', '2', '3', '4', '5'])])
