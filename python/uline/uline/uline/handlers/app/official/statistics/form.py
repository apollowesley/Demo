#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/9/16'

from wtforms import validators, fields
from uline.utils.form import BaseForm


class TotalStatisticsSearch(BaseForm):
    create_at_start = fields.StringField()
    create_at_end = fields.StringField()
    order_by = fields.StringField(validators=[validators.Optional(),
                                              validators.AnyOf(['day_tx_count', 'day_tx_amount',
                                                                'day_refund_count', 'day_refund_amount',
                                                                'day_tx_net_amout', 'day_profit_amount', 'pay_time', 'p_tranamt'])])
    mch_id = fields.StringField(validators=[validators.Optional()])
    query_date = fields.StringField(
        validators=[validators.Optional(), validators.AnyOf(['1', '2'])])


class DistStatisticsSearch(BaseForm):
    create_at_start = fields.StringField(validators=[validators.Optional()])
    dt_id = fields.StringField(validators=[validators.Optional()])
    dt_name = fields.StringField(validators=[validators.Optional()])

    order_by = fields.StringField(validators=[validators.Optional(),
                                              validators.AnyOf(['day_tx_count', 'day_tx_amount',
                                                                'day_refund_count', 'day_refund_amount',
                                                                'day_tx_net_amout', 'day_profit_amount'])])

    total_num = fields.IntegerField()
    query_date = fields.StringField(
        validators=[validators.Optional(), validators.AnyOf(['1', '2'])])
    bk_name = fields.StringField()
    bk_id = fields.StringField()
    # 0 全部 1 主银行拓展  2 同业银行拓展
    expand_type = fields.IntegerField(validators=[validators.AnyOf([0, 1, 2])], default=0)


class MchStatisticsSearch(BaseForm):
    create_at_start = fields.StringField(validators=[validators.Optional()])
    dt_id = fields.StringField(validators=[validators.Optional()])
    dt_name = fields.StringField(validators=[validators.Optional()])

    mch_id = fields.StringField(validators=[validators.Optional()])
    mch_name = fields.StringField(validators=[validators.Optional()])

    order_by = fields.StringField(validators=[validators.Optional(),
                                              validators.AnyOf(['day_tx_count', 'day_tx_amount',
                                                                'day_refund_count', 'day_refund_amount',
                                                                'day_tx_net_amout', 'day_profit_amount'])])

    total_num = fields.IntegerField()
    query_date = fields.StringField(validators=[validators.Optional(),
                                                validators.AnyOf(['1', '2'])])
    bk_name = fields.StringField()
    bk_id = fields.StringField()
    # 0 全部 1 主银行拓展  2 同业银行拓展
    expand_type = fields.IntegerField(validators=[validators.AnyOf([0, 1, 2])], default=0)


class ChainStatisticsSearch(BaseForm):
    create_at_start = fields.DateField(validators=[validators.Optional()])
    dt_id = fields.StringField(validators=[validators.Optional()])
    dt_name = fields.StringField(validators=[validators.Optional()])

    chain_id = fields.StringField(validators=[validators.Optional()])
    chain_name = fields.StringField(validators=[validators.Optional()])

    order_by = fields.StringField(validators=[validators.Optional(),
                                              validators.AnyOf(['day_tx_count', 'day_tx_amount',
                                                                'day_refund_count', 'day_refund_amount',
                                                                'day_tx_net_amout', 'day_profit_amount'])])

    total_num = fields.IntegerField()
