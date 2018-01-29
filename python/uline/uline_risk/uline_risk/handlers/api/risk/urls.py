#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import URLSpec as url
from uline_risk.handlers.api.risk.alipay_risk import AlipayTransactionRiskNotify

# 前缀/api/fee/
urls = [
    url(r'/alipay', AlipayTransactionRiskNotify)
]
