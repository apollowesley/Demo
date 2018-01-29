#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: LiuFei
# Create: '25/4/17'

from tornado.web import URLSpec as url
from .capital_index import MchWithdrawIndexHandler
from .capital_export import CapitalExportHandler
from .capital_detail import MchWithdrawDetailHandler

# 前缀/bank/capital/
urls = [
    url(r'/mch', MchWithdrawIndexHandler),
    url(r'/mch/detail', MchWithdrawDetailHandler),
    url(r'/mch/export', CapitalExportHandler),
]
