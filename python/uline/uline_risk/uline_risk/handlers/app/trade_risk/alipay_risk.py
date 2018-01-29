#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uline_risk.handlers.api.risk.alipay_risk import AlipayTransactionRiskNotify


class AddAlipayTradeRisk(AlipayTransactionRiskNotify):

    def write_response(self):
        if self.risk_id:
            response = self.generate_response_msg(**{"risk_id": self.risk_id})
        else:
            response = self.generate_response_msg('logic_error')
        self.write(response)
        self.finish()
