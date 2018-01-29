#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url
from .withdraw import WithdrawHandler

# 前缀/api/fee/
urls = [
    url(r'/withdraw', WithdrawHandler)
]
