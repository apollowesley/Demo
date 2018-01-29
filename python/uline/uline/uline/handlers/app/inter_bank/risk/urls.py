#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import URLSpec as url
from .merchant_risk_index import MerchantRiskIndexHandler
from .trade_risk_index import TradeRiskIndexHandler
from .deal_trade_risk import DealTradeRiskHandler
from .trade_risk_detail import TradeRiskDetailHandler
from .merchant_risk_detail import MerchantRiskDetailHandler
from .risk_settle_setting import RiskControlSettleHandler
from .merchant_payments import GetMerchantPayments
from .risk_credit_setting import RiskControlCreditHandler

# 前缀/inter_bank/risk/
urls = [
    url(r'/merchant', MerchantRiskIndexHandler),
    url(r'/merchant/detail', MerchantRiskDetailHandler),
    url(r'/trade', TradeRiskIndexHandler),
    url(r'/trade/deal', DealTradeRiskHandler),
    url(r'/trade/detail', TradeRiskDetailHandler),
    url(r'/settle/operate', RiskControlSettleHandler),
    url(r'/merchant/payments', GetMerchantPayments),
    url(r'/credit/operate', RiskControlCreditHandler),
]
