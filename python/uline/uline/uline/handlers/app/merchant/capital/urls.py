#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: LiuFei
# Create: '25/4/17'

from tornado.web import URLSpec as url
from .capital_index import MchCapitalIndexHandler
from .capital_info import MchCapitalInfoHandler
from .capital_status import MchCapitalStatusHandler

# 前缀/mch/capital
urls = [
    url(r'/', MchCapitalIndexHandler),
    url(r'/detail', MchCapitalInfoHandler),
    url(r'/status', MchCapitalStatusHandler)
]
