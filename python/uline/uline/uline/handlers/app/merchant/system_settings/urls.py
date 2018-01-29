#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: guozhihua
# Create: '03/20/17'

from tornado.web import URLSpec as url

from .views import MchRefundPasswordHandler,\
    MchSetRefundPasswordAuthHandler, MchSetRefundPasswordModifyHandler,\
    MchSetRefundPasswordAuthCodeHandler, MchValidationRefundPasswordHandler
from .wechat_send import NewsOperateWeb, SwitchWechatNews, ChoosePaymentType
from WeChat_bind import GetOpenid
# from sub_user import (
#     SubUserEditHandler, SubUserIndexHandler, SubUserInfoHandler, SubUserAddHandler, SubUserSearchHandler,
#     Getbindingstatus, WebChat, GetOpenid)

# 前缀/merchant/settings/
urls = [
    # 验证退款密码
    url(r'refund/password/validation', MchValidationRefundPasswordHandler),
    # 退款密码设置相关接口
    url(r'refund/password', MchRefundPasswordHandler),
    url(r'refund/password/auth/code', MchSetRefundPasswordAuthCodeHandler),
    url(r'refund/password/auth', MchSetRefundPasswordAuthHandler),
    url(r'refund/password/modify', MchSetRefundPasswordModifyHandler),
    url(r'send', NewsOperateWeb),
    url(r'send/switch', SwitchWechatNews),
    url(r'send/open/choosepay', ChoosePaymentType),
    # url(r'sub_user/getqrcode', WebChat),
    url(r'sub_user/getopenid', GetOpenid),
    # url(r'sub_user/bindingstatus', Getbindingstatus),
    # url(r'sub_user', SubUserIndexHandler),
    # url(r'sub_user/add', SubUserAddHandler),
    # url(r'sub_user/info', SubUserInfoHandler),
    # url(r'sub_user/edit', SubUserEditHandler),
    # url(r'sub_user/search', SubUserSearchHandler),
]
