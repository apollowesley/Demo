#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url
from .views import OfclIndexHanddler, OfclLoginHanddler, OfclLogoutHanddler, \
    OfclResetPasswordHandler, OfclResetPasswordAuthHandler, OfclResetPasswordAuthCodeHandler,\
    OfclResetPasswordModifyHandler, TestSMSAsyncHandler, TestMchEmailAsyncHandler, TestDtEmailAsyncHandler

# 前缀official
urls = [
    url(r'/', OfclIndexHanddler),
    url(r'/index', OfclIndexHanddler),
    url(r'/login', OfclLoginHanddler),
    url(r'/logout', OfclLogoutHanddler),
    url(r'resetpasswd', OfclResetPasswordHandler),
    url(r'resetpasswd/auth', OfclResetPasswordAuthHandler),
    url(r'resetpasswd/modify', OfclResetPasswordModifyHandler),
    url(r'resetpasswd/auth/code', OfclResetPasswordAuthCodeHandler),
    url(r'emailMch', TestMchEmailAsyncHandler),
    url(r'emailDt', TestDtEmailAsyncHandler),
    url(r'sms', TestSMSAsyncHandler),
]
