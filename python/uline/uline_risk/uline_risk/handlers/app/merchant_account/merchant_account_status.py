#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uline_risk.handlers.baseHandlers import RESTfulHandler
from uline_risk.model.uline.info import MchBalance
from uline_risk.handlers.app.merchant_account.form import MerchantBalanceStatusForm
from uline_risk.utils.db import uline_session_scope


class GetMerchantBalanceStatus(RESTfulHandler):
    def prepare(self):
        pass

    def get(self):
        self.form = MerchantBalanceStatusForm(self)
        self.valid_params()
        merchant_id = self.form.merchant_id.data
        balance_status = 1
        with uline_session_scope() as session:
            balance_info = session.query(MchBalance).filter(MchBalance.mch_id == merchant_id).first()
            balance_status = balance_info.status if balance_info and balance_info.status else balance_status

        response = self.generate_response_msg(**{"balance_status": balance_status})
        self.write(response)
        self.finish()
