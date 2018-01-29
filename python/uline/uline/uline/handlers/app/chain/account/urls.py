#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url

from .views import ChainIndexHandler, ChainLoginHandler, ChainLogoutHandler, \
    ChainResetPasswordHandler, ChainResetPasswordAuthHandler, ChainResetPasswordModifyHandler, \
    ChainResetPasswordAuthCodeHandler, ChainFirstLoginAuthCodeCodeHandler, \
    ChainFirstLoginModifyHandler, ChainFirstLoginGetAuthCodeHandler, ChainForgetPasswordHandler, \
    ChainForgetPasswordAuthHandler, ChainForgetPasswordAuthCodeHandler, ChainForgetPasswordModifyHandler

# chain
urls = [
    url(r'', ChainIndexHandler),
    url(r'index', ChainIndexHandler),
    url(r'login', ChainLoginHandler),
    url(r'logout', ChainLogoutHandler),
    url(r'resetpasswd', ChainResetPasswordHandler),
    url(r'resetpasswd/auth', ChainResetPasswordAuthHandler),
    url(r'resetpasswd/modify', ChainResetPasswordModifyHandler),
    url(r'resetpasswd/auth/code', ChainResetPasswordAuthCodeHandler),
    url(r'login/code', ChainFirstLoginGetAuthCodeHandler),
    url(r'login/auth', ChainFirstLoginAuthCodeCodeHandler),
    url(r'login/modify', ChainFirstLoginModifyHandler),
    url(r'forgetpwd', ChainForgetPasswordHandler),
    url(r'forgetpwd/auth', ChainForgetPasswordAuthHandler),
    url(r'forgetpwd/modify', ChainForgetPasswordModifyHandler),
    url(r'forgetpwd/auth/code', ChainForgetPasswordAuthCodeHandler),
]
