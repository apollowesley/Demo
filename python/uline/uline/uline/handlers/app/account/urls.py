#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url

from .views import LoginHandler, LogoutHandler, \
    ResetPasswordAuthHandler, ResetPasswordModifyHandler, \
    ResetPasswordAuthCodeHandler, FirstLoginAuthCodeCodeHandler, \
    FirstLoginGetAuthCodeHandler, FirstLoginModifyHandler, \
    ForgetPasswordAuthHandler, ForgetPasswordHandler, \
    ForgetPasswordModifyHandler, ForgetPasswordAuthCodeHandler, IndexHandler, ChangeCs, NoRoleWebpage, Employee_cs

# 前缀
urls = [
    url(r'', IndexHandler),
    # url(r'index', IndexHandler),
    url(r'login', LoginHandler),
    url(r'logout', LogoutHandler),
    # url(r'resetpasswd', ResetPasswordHandler),
    url(r'resetpasswd/auth', ResetPasswordAuthHandler),
    url(r'resetpasswd/modify', ResetPasswordModifyHandler),
    url(r'resetpasswd/auth/code', ResetPasswordAuthCodeHandler),
    url(r'login/code', FirstLoginGetAuthCodeHandler),
    url(r'login/auth', FirstLoginAuthCodeCodeHandler),
    url(r'login/modify', FirstLoginModifyHandler),
    url(r'forgetpwd', ForgetPasswordHandler),
    url(r'forgetpwd/auth', ForgetPasswordAuthHandler),
    url(r'forgetpwd/modify', ForgetPasswordModifyHandler),
    url(r'forgetpwd/auth/code', ForgetPasswordAuthCodeHandler),
    url(r'change_cs', ChangeCs),

    url(r'no_role', NoRoleWebpage),
    url(r'employee_cs', Employee_cs),

]
