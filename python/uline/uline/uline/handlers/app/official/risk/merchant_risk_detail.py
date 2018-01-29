#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado import web, gen

from uline.handlers.app.bank.risk.form import TradeRiskDetailForm
from uline.handlers.baseHandlers import OfclAdminHandler
from uline.public import common, merchant_risk_util
from uline.utils.risk_api import risk_api_util


class MerchantRiskDetailHandler(OfclAdminHandler):
    @web.authenticated
    def prepare(self):
        self.form = TradeRiskDetailForm(self)
        if not self.form.validate():
            response = common.f_rsp(406, u'请指定风险条目')
            self.write(response)
            self.finish()

    @gen.coroutine
    def get(self):
        result = yield risk_api_util.query_risk_api("merchant_risk_list", params={"risk_id": self.form.risk_id.data})
        is_success, error_msg = risk_api_util.check_response(result)
        if not is_success:
            response = common.f_rsp(406, error_msg)
            self.write(response)
            self.finish()
            return

        risk_info = result.get("merchant_risk_list", [])
        if risk_info:
            risk_info = risk_info[0]
        if not risk_info:
            response = common.f_rsp(406, u'没有对应的风险条目')
            self.write(response)
            self.finish()
            return

        risk_info['risk_type'] = merchant_risk_util.print_merchant_risk_type(risk_info.get('risk_type', ''))
        response = common.scc_rsp(code=200, msg='success', **risk_info)
        self.write(response)
