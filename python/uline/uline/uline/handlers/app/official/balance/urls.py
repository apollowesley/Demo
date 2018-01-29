#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url
from .distributorBalanceIndex import DistributorBalanceIndexHandler
from .merchantBalanceIndex import MerchantBalanceIndexIndexHandler
from .distributorBalanceList import DistributorBalanceListHandler
from .merchantBalanceList import MerchantBalanceIndexListHandler
from .exportMerchantBalance import ExportMerchantBalanceHandler
from .exportDistributorBalance import ExportDistributorBalanceHandler

# 前缀/official/balance
urls = [
    url(r'/mch', MerchantBalanceIndexIndexHandler),
    url(r'/mch/list', MerchantBalanceIndexListHandler),
    url(r'/mch/export', ExportMerchantBalanceHandler),
    url(r'/dt', DistributorBalanceIndexHandler),
    url(r'/dt/list', DistributorBalanceListHandler),
    url(r'/dt/export', ExportDistributorBalanceHandler),
]
