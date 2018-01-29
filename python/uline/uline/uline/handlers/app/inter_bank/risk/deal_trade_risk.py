#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from datetime import datetime

from tornado import web, gen

from uline.handlers.baseHandlers import IntBkAdminHandler
from uline.public import constants, db, common
from uline.model.uline.other import TradeRiskInfo, RiskControl
from uline.model.uline.info import MchInletInfo, MchPayment, MchBalance
from uline.model.uline.user import MchUser
from uline.utils.alipay import new_merchantInletToAlipay, query_alipay_mapi
from uline.handlers.app.bank.risk.form import TradeRiskDealForm
from uline.utils.risk_api.risk_api_util import query_risk_api, check_response


class DealTradeRiskHandler(IntBkAdminHandler):
    @web.authenticated
    def prepare(self):
        self.form = TradeRiskDealForm(self)
        if not self.form.validate():
            response_message = common.f_rsp(406, '参数错误')
            self.write(response_message)
            self.finish()
        self.current_time = datetime.now()
        self.sys_type = 'mch'

    @gen.coroutine
    def get(self):
        yield self.post()

    @gen.coroutine
    def post(self):
        risk_id = self.form.risk_id.data
        handle_type = self.form.handle_type.data
        close_payments = self.form.close_payments.data
        freeze_account = self.form.freeze_account.data
        if freeze_account:
            freeze_account = 1

        params = {
            "risk_id": risk_id,
            "handle_type": handle_type,
            "close_payments": close_payments,
            "freeze_account": freeze_account
        }
        result = yield query_risk_api("alipay_trade_risk_deal", method="POST", body=params)

        is_success, msg = check_response(result)
        if is_success:
            response = common.scc_rsp()
        else:
            response = common.f_rsp(406, msg)
        self.write(response)
        self.finish()
