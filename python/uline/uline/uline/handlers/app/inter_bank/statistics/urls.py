#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url

from .exportmchTransactionStatisticHandler import ExportmchTransactionStatisticHandler
from .exportchainTransactionStatisticHandler import ExportChainTransactionStatisticHandler
from .merchant_daily_transactionStatisticsHandler import MchDailyTransactionHandler
from .chain_daily_transactionStatisticsHandler import ChainDailyTransactionHandler
from .transactionStatisticsHandler import TransactionStatisticsHandler
from .dist_daily_transactionStatisticsHandler import DistDailyTransactionHandler
from .exportTransactionStatisticHandler import ExportTransactionStatisticHandler
from .distStatisticsHandler import DistStatisticsHandler
from .exportDistStatistics import ExportDistStatistics
from .mchStatisticsHandler import MchStatisticsHandler
from .chainStatisticsHandler import ChainStatisticsHandler
from .exportMchStatistics import ExportMchStatistics
from .exportChainStatistics import ExportChainStatistics
from .exportdistTransactionStatisticHandler import ExportdistTransactionStatisticHandler


# 前缀bank/stats
urls = [
    url(r'/transaction', TransactionStatisticsHandler),
    url(r'/dist', DistStatisticsHandler),
    url(r'/mch', MchStatisticsHandler),
    url(r'/chain', ChainStatisticsHandler),
    url(r'/dist/export', ExportDistStatistics),
    url(r'/mch/export', ExportMchStatistics),
    url(r'/chain/export', ExportChainStatistics),
    url(r'/dist/detail', DistDailyTransactionHandler),
    url(r'/mch/detail', MchDailyTransactionHandler),
    url(r'/chain/detail', ChainDailyTransactionHandler),
    url(r'/transaction/export', ExportTransactionStatisticHandler),
    url(r'/dist/detail/export', ExportdistTransactionStatisticHandler),
    url(r'/mch/detail/export', ExportmchTransactionStatisticHandler),
    url(r'/transaction/export/chain', ExportChainTransactionStatisticHandler),
]
