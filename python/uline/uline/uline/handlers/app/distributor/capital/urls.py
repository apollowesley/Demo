#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: LiuFei
# Create: '25/4/17'

from tornado.web import URLSpec as url
from .capital_index import DistCapitalIndexHandler

# 前缀/dist/capital/
urls = [
    url(r'', DistCapitalIndexHandler),
]
