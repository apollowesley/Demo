#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url
from .cs_balance_index import CsBalanceIndexHandler
from .cs_balance_list import CsBalanceListHandler
from .cs_balance_export import CsBalanceExportHandler

# 前缀/chain/balance
urls = [
    url(r'/cs', CsBalanceIndexHandler),
    url(r'/cs/list', CsBalanceListHandler),
    url(r'/cs/export', CsBalanceExportHandler)
]
