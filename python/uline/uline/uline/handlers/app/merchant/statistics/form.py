#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/9/16'

from wtforms import validators, fields
from uline.utils.form import BaseForm


class TotalStatisticsSearch(BaseForm):
    create_at_start = fields.StringField()
    create_at_end = fields.StringField()
    order_by = fields.StringField(validators=[validators.Optional(), validators.AnyOf(
        ['day_tx_count', 'day_tx_amount', 'day_refund_count', 'day_refund_amount', 'day_tx_net_amout', 'day_profit_amount', 'need_pay_time', 'pay_time'])])

    query_date = fields.StringField(
        validators=[validators.Optional(), validators.AnyOf(['1', '2'])])
