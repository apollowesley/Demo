#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url
from .merchantBalanceIndex import MerchantBalanceIndexIndexHandler
from .merchantBalanceList import MerchantBalanceIndexListHandler
from .exportMerchantBalance import ExportMerchantBalanceHandler

# 前缀/distributor/balance
urls = [
    url(r'/mch', MerchantBalanceIndexIndexHandler),
    url(r'/mch/list', MerchantBalanceIndexListHandler),
    url(r'/mch/export', ExportMerchantBalanceHandler),
]
