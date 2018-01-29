#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url
from .transactionStatisticsHandler import TransactionStatisticsHandler
from .exportTransactionStatisticHandler import ExportTransactionStatisticHandler

# 前缀bank
urls = [
    url(r'/transaction', TransactionStatisticsHandler),
    url(r'/transaction/export', ExportTransactionStatisticHandler),
]
