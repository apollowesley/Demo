#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import URLSpec as url
from .deal_trade_risk import TradeRiskDeal
from .trade_risk_query import QueryTradeRiskList
from .alipay_risk import AddAlipayTradeRisk

# 前缀/bank/trade_risk/

urls = [
    # 处理风险交易
    url(r'/deal', TradeRiskDeal),
    # 支付宝通知
    url(r'/alipay', AddAlipayTradeRisk),
    # 查询风险交易，列表
    url(r'/', QueryTradeRiskList),
]
