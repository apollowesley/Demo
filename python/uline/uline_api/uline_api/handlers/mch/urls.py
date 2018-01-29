#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url
from .views import GetMchPayKey, MerchantHandler, GetMchWithdrawBalance


# 前缀/v1/mch
urls = [
    url(r'\/mchpaykey', GetMchPayKey),
    url(r'\/mch_withdraw_balance', GetMchWithdrawBalance),
    url(r'', MerchantHandler),
]
