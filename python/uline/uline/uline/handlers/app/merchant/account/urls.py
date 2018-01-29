#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url

from .views import MchIndexHandler, MchLoginHandler, MchLogoutHandler, \
    MchResetPasswordHandler, MchResetPasswordAuthHandler, MchResetPasswordModifyHandler, \
    MchResetPasswordAuthCodeHandler, MchFirstLoginAuthCodeCodeHandler, \
    MchFirstLoginGetAuthCodeHandler, MchFirstLoginModifyHandler, \
    MchForgetPasswordAuthHandler, MchForgetPasswordHandler, \
    MchForgetPasswordModifyHandler, MchForgetPasswordAuthCodeHandler

# 前缀mch
urls = [
    url(r'', MchIndexHandler),
    url(r'index', MchIndexHandler),
    url(r'login', MchLoginHandler),
    url(r'logout', MchLogoutHandler),
    url(r'resetpasswd', MchResetPasswordHandler),
    url(r'resetpasswd/auth', MchResetPasswordAuthHandler),
    url(r'resetpasswd/modify', MchResetPasswordModifyHandler),
    url(r'resetpasswd/auth/code', MchResetPasswordAuthCodeHandler),
    url(r'login/code', MchFirstLoginGetAuthCodeHandler),
    url(r'login/auth', MchFirstLoginAuthCodeCodeHandler),
    url(r'login/modify', MchFirstLoginModifyHandler),
    url(r'forgetpwd', MchForgetPasswordHandler),
    url(r'forgetpwd/auth', MchForgetPasswordAuthHandler),
    url(r'forgetpwd/modify', MchForgetPasswordModifyHandler),
    url(r'forgetpwd/auth/code', MchForgetPasswordAuthCodeHandler),
]
