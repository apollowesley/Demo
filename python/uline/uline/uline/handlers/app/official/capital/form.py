#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wtforms import validators, fields
from uline.utils.form import BaseForm


# 资金流水表单
class MerchantWithdrawSearch(BaseForm):
    # 开始时间
    create_at_start = fields.DateField(validators=[validators.Optional()])
    # 结束时间
    create_at_end = fields.DateField(validators=[validators.Optional()])

    # 账户类型 支付宝 或 微信
    channel = fields.StringField(validators=[validators.Optional(), validators.AnyOf(['weixin', 'alipay'])])

    pay_status = fields.IntegerField(validators=[validators.Optional(), validators.AnyOf([1, 2, 3])])

    mch_clear_no = fields.StringField(validators=[validators.Optional()])
    # 商户名称
    mch_name = fields.StringField(validators=[validators.Optional()])
    mch_shortname = fields.StringField(validators=[validators.Optional()])
    # 商户ID
    mch_id = fields.StringField(validators=[validators.Optional()])

    # 渠道商名称
    dt_name = fields.StringField(validators=[validators.Optional()])
    # 渠道商id
    dt_id = fields.StringField(validators=[validators.Optional()])

    # 结算卡号
    settle_card = fields.StringField(validators=[validators.Optional()])

    # 总数
    total_num = fields.IntegerField(validators=[validators.Optional()])


class MerchantWithdrawDetail(BaseForm):
    mch_clear_no = fields.StringField(validators=[validators.DataRequired()])
