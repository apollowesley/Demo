#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url

from .merchantIndex import MerchantInletIndexHandler
# 前缀/merchant/inlet
urls = [
    # 商户
    url(r'/mch', MerchantInletIndexHandler),
]
