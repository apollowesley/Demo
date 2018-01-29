#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url
from .merchantsTransactionTrade import MerchantsTransactionTradeHandler
from .merchantsTransactionTradeList import MerchantsTransactionTradeListHandler
from .merchantsTransactionRefund import MerchantsTransactionRefundHandler
from .merchantsTransactionRefundList import MerchantsTransactionRefundListHandler
from .merchantsTransactionCanRefund import MerchantsTransactionCanRefundHandler
from .exportMerchantRefund import ExportMerchantRefundHandler
from .exportMerchantTrade import ExportMerchantTradeHandler
from .exportMerchantTradeOld import ExportMerchantTradeHandlerOld
from .singleMerchantRefund import MerchantsRefundDetailHandler, MerchantsInitiateRefundHandler

# 前缀/merchant/transaction
urls = [
    url(r'/trade', MerchantsTransactionTradeHandler),
    url(r'/trade/list', MerchantsTransactionTradeListHandler),
    # 判断是否可以退款
    url(r'/can_refund', MerchantsTransactionCanRefundHandler),
    url(r'/refund', MerchantsTransactionRefundHandler),
    url(r'/refund/list', MerchantsTransactionRefundListHandler),
    url(r'/refund/export', ExportMerchantRefundHandler),
    url(r'/trade/export', ExportMerchantTradeHandler),
    url(r'/trade/old_export', ExportMerchantTradeHandlerOld),

    url(r'/refund/detail', MerchantsRefundDetailHandler),
    url(r'/refund/initiate', MerchantsInitiateRefundHandler),
]
