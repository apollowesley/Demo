#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: liufei
# Create: '06/12/17'

from tornado.web import URLSpec as url

from .views import ChainRefundPasswordHandler, ChainSetRefundPasswordAuthCodeHandler,\
    ChainSetRefundPasswordAuthHandler, ChainSetRefundPasswordModifyHandler
from .chain_wechat_send import NewsOperateWeb, SwitchWechatNews, ChoosePaymentType
from .sub_user import SubUserIndexHandler, SubUserAddHandler, SubUserEditHandler, SubUserInfoHandler


# 前缀/chain/settings/
urls = [
    # 退款密码设置相关接口
    url(r'refund/password', ChainRefundPasswordHandler),
    url(r'refund/password/auth/code', ChainSetRefundPasswordAuthCodeHandler),
    url(r'refund/password/auth', ChainSetRefundPasswordAuthHandler),
    url(r'refund/password/modify', ChainSetRefundPasswordModifyHandler),
    url(r'send', NewsOperateWeb),
    url(r'send/switch', SwitchWechatNews),
    url(r'send/open/choosepay', ChoosePaymentType),
    url(r'sub_user', SubUserIndexHandler),
    url(r'sub_user/add', SubUserAddHandler),
    url(r'sub_user/info', SubUserInfoHandler),
    url(r'sub_user/edit', SubUserEditHandler)

]
