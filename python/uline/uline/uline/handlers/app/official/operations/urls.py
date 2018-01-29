#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: wangjingCN
# Create: '7/11/17'

from tornado.web import URLSpec as url

from .messageSendAdd import MessageSendAddHandler
from .messageSearch import MessageSearchHandler
from .messageSearchBySendId import MessageSendSerchByIdHandler

# 前缀 /official/operations
urls = [
    url(r'/message/send', MessageSendAddHandler),
    url(r'/message/searchBySendId', MessageSendSerchByIdHandler),
    url(r'/message/searchList', MessageSearchHandler),
]
