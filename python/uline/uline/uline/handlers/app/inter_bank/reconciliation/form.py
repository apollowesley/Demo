#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/9/16'

from wtforms import validators, fields, ValidationError
from uline.utils.form import IdCard, File, BaseForm
from uline.public.baseDB import DbClient

db = DbClient()


class ReconErrorSearch(BaseForm):
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    except_type = fields.IntegerField(validators=[validators.optional(), validators.AnyOf([0, 1, 2])])
    handle_status = fields.IntegerField(validators=[validators.optional(), validators.AnyOf([0, 1, 2, 3])])
    out_trade_no = fields.StringField(validators=[validators.Optional()])
    total_num = fields.IntegerField()


class ReconErrorList(BaseForm):
    out_trade_no = fields.StringField(validators=[validators.Optional()])


class ReconErrorRefundSearch(BaseForm):
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    except_type = fields.IntegerField(validators=[validators.optional(), validators.AnyOf([0, 1, 2])])
    handle_status = fields.IntegerField(validators=[validators.optional(), validators.AnyOf([0, 1, 2, 3])])
    out_refund_no = fields.StringField(validators=[validators.Optional()])
    total_num = fields.IntegerField()


class ReconErrorRefundList(BaseForm):
    out_refund_no = fields.StringField(validators=[validators.Optional()])
