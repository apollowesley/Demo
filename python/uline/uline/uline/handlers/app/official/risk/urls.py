#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import URLSpec as url
from .merchant_risk_index import MerchantRiskIndexHandler
from .trade_risk_index import TradeRiskIndexHandler
from .trade_risk_detail import TradeRiskDetailHandler
from .merchant_risk_detail import MerchantRiskDetailHandler

# 前缀/official/risk/
urls = [
    url(r'/merchant', MerchantRiskIndexHandler),
    url(r'/merchant/detail', MerchantRiskDetailHandler),
    url(r'/trade', TradeRiskIndexHandler),
    url(r'/trade/detail', TradeRiskDetailHandler),
]
