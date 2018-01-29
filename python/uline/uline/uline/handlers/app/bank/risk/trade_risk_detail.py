#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado import web, gen

from uline.handlers.app.bank.risk.form import TradeRiskDetailForm
from uline.handlers.baseHandlers import BkAdminHandler
from uline.public import common
from uline.utils.risk_api.risk_api_util import query_risk_api, check_response


class TradeRiskDetailHandler(BkAdminHandler):
    @web.authenticated
    def prepare(self):
        self.form = TradeRiskDetailForm(self)
        if not self.form.validate():
            response = common.f_rsp(406, u'请指定风险条目')
            self.write(response)
            self.finish()

    @gen.coroutine
    def get(self):
        risk_id = self.form.risk_id.data
        risk_info = None
        result = yield query_risk_api("trade_risk_list", params={"risk_id": risk_id})
        is_success, error_msg = check_response(result)
        if is_success:
            trade_risk_list = result.get("trade_risk_list", None)
            if trade_risk_list:
                risk_info = trade_risk_list[0]
            if not risk_info:
                response = common.f_rsp(406, u'没有对应的风险条目')
            else:
                response = common.scc_rsp(code=200, msg='success', **risk_info)
        else:
            response = common.f_rsp("406", "服务器繁忙")

        # risk_info['create_at'] = common.datetime_to_str(risk_info['create_at'])
        self.write(response)
        self.finish()
