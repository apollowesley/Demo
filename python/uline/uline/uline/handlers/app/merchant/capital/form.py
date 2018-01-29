#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: LiuFei
# Create: '25/4/17'

from wtforms import validators, fields
from uline.utils.form import BaseForm
from uline.public.baseTradeDB import TradeDbClient

tdb = TradeDbClient()


# 资金流水表单
class MerchantTCapitalSearch(BaseForm):
    # 业务名称
    business_type = fields.IntegerField(validators=[validators.Optional()])
    # 业务单号
    mch_clear_no = fields.IntegerField(validators=[validators.Optional()])
    # 交易/退款单号
    out_trade_no = fields.IntegerField(validators=[validators.Optional()])
    # 账户类型 支付宝 或 微信
    channel = fields.StringField(validators=[validators.Optional(),
                                             validators.AnyOf(['wx', 'alipay'])], default='wx')
    # 开始时间
    create_at_start = fields.DateField(validators=[validators.Optional()])
    # 结束时间
    create_at_end = fields.DateField(validators=[validators.Optional()])
    total_num = fields.IntegerField()

    # 结算
    cleared = fields.IntegerField(validators=[validators.Optional(),
                                              validators.AnyOf([0, 1])])


# 资金流水详情表单
class MerchantTCapitalInfo(BaseForm):
    # jump_no=7667446302864773120&channel=wx&business_type=3&cleared=1
    business_no = fields.StringField(validators=[validators.DataRequired(message=u'业务单号不能为空')])
    channel = fields.StringField(validators=[validators.Optional(),
                                             validators.AnyOf(['weixin', 'alipay'])])
    business_type = fields.IntegerField(validators=[validators.Optional(), validators.AnyOf([1, 2, 3])])
    cleared = fields.IntegerField(validators.Optional())
