#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url

from .merchant_daily_transactionStatisticsHandler import MchDailyTransactionHandler
from .chain_daily_transactionStatisticsHandler import ChainDailyTransactionHandler
from .exportmchTransactionStatisticHandler import ExportmchTransactionStatisticHandler
from .exportchainTransactionStatisticHandler import ExportchainTransactionStatisticHandler
from .transactionStatisticsHandler import TransactionStatisticsHandler
from .exportTransactionStatisticHandler import ExportTransactionStatisticHandler
from .mchStatisticsHandler import MchStatisticsHandler
from .chainStatisticsHandler import ChainStatisticsHandler
from .exportMchStatistics import ExportMchStatistics
from .exportChainStatistics import ExportChainStatistics

# 前缀bank
urls = [
    url(r'/transaction', TransactionStatisticsHandler),
    url(r'/mch', MchStatisticsHandler),
    url(r'/chain', ChainStatisticsHandler),
    url(r'/mch/export', ExportMchStatistics),
    url(r'/chain/export', ExportChainStatistics),
    url(r'/mch/detail', MchDailyTransactionHandler),
    url(r'/chain/detail', ChainDailyTransactionHandler),
    url(r'/transaction/export', ExportTransactionStatisticHandler),
    url(r'/mch/detail/export', ExportmchTransactionStatisticHandler),
    url(r'/transaction/export/chain', ExportchainTransactionStatisticHandler),
]
