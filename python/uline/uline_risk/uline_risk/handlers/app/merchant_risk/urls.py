#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import URLSpec as url
from .get_merchant_risk_list import MerchantListHandler
from .add_merchant_risk import AddMerchantALIRiskHandler
# 前缀/bank/trade_risk/

urls = [
    url(r'/$', MerchantListHandler),
    url(r'/add/alipay', AddMerchantALIRiskHandler),
]
