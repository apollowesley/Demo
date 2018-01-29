#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url
from .merchantsTransactionTrade import MerchantsTransactionTradeHandler
from .merchantsTransactionTradeList import MerchantsTransactionTradeListHandler
from .merchantsTransactionRefund import MerchantsTransactionRefundHandler
from .merchantsTransactionRefundList import MerchantsTransactionRefundListHandler
from .exportMerchantRefund import ExportMerchantRefundHandler
from .exportMerchantTrade import ExportMerchantTradeHandler

# 前缀/inter_banks/transaction
urls = [
    url(r'/trade', MerchantsTransactionTradeHandler),
    url(r'/trade/list', MerchantsTransactionTradeListHandler),
    url(r'/refund', MerchantsTransactionRefundHandler),
    url(r'/refund/list', MerchantsTransactionRefundListHandler),
    url(r'/refund/export', ExportMerchantRefundHandler),
    url(r'/trade/export', ExportMerchantTradeHandler),
]
