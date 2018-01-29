#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url

from .views import DtIndexHandler, DtLoginHandler, DtLogoutHandler, \
    DtResetPasswordHandler, DtResetPasswordAuthHandler, DtResetPasswordModifyHandler, \
    DtResetPasswordAuthCodeHandler, DtFirstLoginAuthCodeCodeHandler, \
    DtFirstLoginModifyHandler, DtFirstLoginGetAuthCodeHandler, DtForgetPasswordHandler, \
    DtForgetPasswordAuthHandler, DtForgetPasswordAuthCodeHandler, DtForgetPasswordModifyHandler

# 前缀dist
urls = [
    url(r'', DtIndexHandler),
    url(r'index', DtIndexHandler),
    url(r'login', DtLoginHandler),
    url(r'logout', DtLogoutHandler),
    url(r'resetpasswd', DtResetPasswordHandler),
    url(r'resetpasswd/auth', DtResetPasswordAuthHandler),
    url(r'resetpasswd/modify', DtResetPasswordModifyHandler),
    url(r'resetpasswd/auth/code', DtResetPasswordAuthCodeHandler),
    url(r'login/code', DtFirstLoginGetAuthCodeHandler),
    url(r'login/auth', DtFirstLoginAuthCodeCodeHandler),
    url(r'login/modify', DtFirstLoginModifyHandler),
    url(r'forgetpwd', DtForgetPasswordHandler),
    url(r'forgetpwd/auth', DtForgetPasswordAuthHandler),
    url(r'forgetpwd/modify', DtForgetPasswordModifyHandler),
    url(r'forgetpwd/auth/code', DtForgetPasswordAuthCodeHandler),
]
