#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url
from .views import BkIndexHanddler, BkLoginHanddler, BkLogoutHanddler, \
    BkResetPasswordHandler, BkResetPasswordAuthHandler, BkResetPasswordModifyHandler, BkResetPasswordAuthCodeHandler

# 前缀bank
urls = [
    url(r'/', BkIndexHanddler),
    url(r'/index', BkIndexHanddler),
    url(r'/login', BkLoginHanddler),
    url(r'/logout', BkLogoutHanddler),
    url(r'resetpasswd', BkResetPasswordHandler),
    url(r'resetpasswd/auth', BkResetPasswordAuthHandler),
    url(r'resetpasswd/modify', BkResetPasswordModifyHandler),
    url(r'resetpasswd/auth/code', BkResetPasswordAuthCodeHandler),
]
