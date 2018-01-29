#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url

from .sub_user import (
    SubUserIndexHandler, SubUserAddHandler, SubUserSearchHandler, SubUserInfoHandler,
    SubUserEditHandler,

)

# 前缀sub_user
urls = [
    url(r'/', SubUserIndexHandler),
    url(r'/add', SubUserAddHandler),
    url(r'/info', SubUserInfoHandler),
    url(r'/edit', SubUserEditHandler),
    url(r'/search', SubUserSearchHandler),
]
