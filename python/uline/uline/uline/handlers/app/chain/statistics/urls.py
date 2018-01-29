#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url

from .chain_transaction_statistics import ChainTransactionStatisticsHandler
from .chain_statistic_export import ExportchainTransactionStatisticHandler

# chain
urls = [
    url(r'/transaction', ChainTransactionStatisticsHandler),
    url(r'/transaction/export', ExportchainTransactionStatisticHandler),
]
