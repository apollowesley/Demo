#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import URLSpec as url
from .mch_subsidize_index import MchSubsidizeIndexHandler
from .mch_subsidize_detail import MchSubsidizeDetail
from .mch_subsidize_query import MchSubsidizeInfo
from .mch_subsidize_modify import MchSubsidizeModifyHandler
from .mch_subsidize_add import MchSubsidizeAddHandler

# 前缀/bank/subsidize/
urls = [
    url(r'/mch', MchSubsidizeIndexHandler),
    url(r'/mch/detail', MchSubsidizeDetail),
    url(r'/mch/mch_info', MchSubsidizeInfo),
    url(r'/mch/add', MchSubsidizeAddHandler),
    url(r'/mch/modify', MchSubsidizeModifyHandler),
]
