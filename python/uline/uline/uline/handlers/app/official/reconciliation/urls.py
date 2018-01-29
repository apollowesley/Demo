#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url

from .reconTransactionErrorIndex import ReconTransactionErrorIndexHandler
from .reconTransactionErrorList import ReconTransactionErrorListHandler

from .reconRefundErrorIndex import ReconRefundErrorIndexHandler
from .reconRefundErrorList import ReconRefundErrorListHandler

from .exportRefundError import ExportRefundErrorHandler
from .exportTransactionError import ExportTransactionErrorHandler
# 前缀/official/recon/
urls = [
    url(r'/refund', ReconRefundErrorIndexHandler),
    url(r'/refund/list', ReconRefundErrorListHandler),
    url(r'/refund/export', ExportRefundErrorHandler),

    url(r'/transaction', ReconTransactionErrorIndexHandler),
    url(r'/transaction/list', ReconTransactionErrorListHandler),
    url(r'/transaction/export', ExportTransactionErrorHandler),
]
