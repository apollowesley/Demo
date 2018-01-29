#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import URLSpec as url
from .mch_subsidize_index import MchSubsidizeIndexHandler
from .mch_subsidize_detail import MchSubsidizeDetail

# 前缀/bank/subsidize/
urls = [
    url(r'/mch', MchSubsidizeIndexHandler),
    url(r'/mch/detail', MchSubsidizeDetail),
]
