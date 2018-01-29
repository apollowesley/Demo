#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import URLSpec as url
from .merchant_settle_setting import SettingMerchantSettleHandler
from .merchant_credit_setting import SettingMerchantCreditControlHandler
from .merchant_risk_info import GetMerchantRiskControlInfoHandler
from .merchant_account_status import GetMerchantBalanceStatus
from .get_all_freeze_merchant import GetAllFreezeMerchant
# 前缀/merchant/

urls = [
    # 账户冻结关闭
    url(r'/settle/deal', SettingMerchantSettleHandler),
    # 信用卡冻结关闭
    url(r'/credit/deal', SettingMerchantCreditControlHandler),
    # 用户风控信息
    url(r'/risk_info', GetMerchantRiskControlInfoHandler),
    # 商户账户状态
    url(r'/balance_status', GetMerchantBalanceStatus),
    # 获取所有冻结商户
    url(r'/freeze_mchs', GetAllFreezeMerchant),
]
