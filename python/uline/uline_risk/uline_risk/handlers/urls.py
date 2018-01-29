# -*- coding: utf-8 -*-

from uline_risk.utils.urls import include

urls = []


# 风险回调信息
urls += include(r"/risk/", "uline_risk.handlers.api.risk.urls")

# 交易风险
urls += include(r"/trade_risk/", "uline_risk.handlers.app.trade_risk.urls")

# 商户风险处理
urls += include(r"/merchant_risk/", "uline_risk.handlers.app.merchant_risk.urls")

# 商户账户
urls += include(r"/merchant/", "uline_risk.handlers.app.merchant_account.urls")
