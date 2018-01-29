#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: guozhihua
# Create: '03/20/17'

from tornado.web import URLSpec as url

from .wechat_send import NewsOperateWeb, SwitchWechatNews, ChoosePaymentType
from wechat_binding import Getbindingstatus, WebChat
from sub_user_add import SubUserAddHandler
from sub_user_index import GetCsprofile
from sub_user_edit import SubUserEditHandler
from sub_user_index import SubUserIndexHandler
from sub_user_info import SubUserInfoHandler

# 前缀/common/settings/
urls = [

    url(r'send', NewsOperateWeb),
    url(r'send/switch', SwitchWechatNews),
    url(r'send/choosepay', ChoosePaymentType),

    url(r'sub_user/getqrcode', WebChat),
    # url(r'sub_user/getopenid', GetOpenid),
    url(r'sub_user/bindingstatus', Getbindingstatus),


    url(r'sub_user/index', SubUserIndexHandler),
    url(r'sub_user/index/cs', GetCsprofile),
    url(r'sub_user/add', SubUserAddHandler),
    url(r'sub_user/info', SubUserInfoHandler),
    url(r'sub_user/edit', SubUserEditHandler),


]
