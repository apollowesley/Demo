#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url
from .views import AddMerchant
from .update_merchant import UpdateMerchant
from .view_auth_test import AuthTest
from .wx_pay_config import SetMchWxPayConfigHandler, GetMchWxPayConfigHandler, UpdateMchWxPayConfigHandler


# 前缀/v1/mchinlet
urls = [
    url(r'$', AddMerchant),
    url(r'\/update$', UpdateMerchant),
    url(r'\/authtest', AuthTest),
    url(r'\/setwxconfig', SetMchWxPayConfigHandler),
    url(r'\/getwxconfig', GetMchWxPayConfigHandler),
    url(r'\/refreshwxconfig', UpdateMchWxPayConfigHandler),
]
