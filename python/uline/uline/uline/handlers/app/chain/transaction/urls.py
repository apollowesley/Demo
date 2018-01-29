#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url
from .cs_transaction_trade import CsTransactionTradeHandler
from .cs_transaction_trade_list import CsTransactionTradeListHandler
from .cs_transaction_refund import CsTransactionRefundHandler
from .cs_transaction_refund_list import CsTransactionRefundListHandler
from .cs_export_refund import CsExportRefundHandler
from .cs_export_trade import CsExportTradeHandler
from .single_cs_refund import CsRefundDetailHandler, CsInitiateRefundHandler
from .cs_transaction_can_refund import CsTransactionCanRefundHandler

# 前缀/chain/transaction
urls = [
    url(r'/trade', CsTransactionTradeHandler),
    url(r'/trade/list', CsTransactionTradeListHandler),
    # 判断是否可以退款
    url(r'/can_refund', CsTransactionCanRefundHandler),
    url(r'/refund', CsTransactionRefundHandler),
    url(r'/refund/list', CsTransactionRefundListHandler),
    url(r'/refund/export', CsExportRefundHandler),
    url(r'/trade/export', CsExportTradeHandler),
    url(r'/refund/detail', CsRefundDetailHandler),
    url(r'/refund/initiate', CsInitiateRefundHandler),
]
