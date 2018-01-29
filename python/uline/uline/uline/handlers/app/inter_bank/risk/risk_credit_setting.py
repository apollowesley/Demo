#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado import web, gen

from uline.handlers.baseHandlers import IntBkAdminHandler
from uline.public import common
from uline.handlers.app.inter_bank.risk.form import RiskControlCreditForm
from uline.utils.risk_api import risk_api_util


class RiskControlCreditHandler(IntBkAdminHandler):
    @web.authenticated
    def prepare(self):
        self.form = RiskControlCreditForm(self)
        if not self.form.validate():
            response = common.f_rsp(406, u'操作失败')
            self.write(response)
            self.finish()

    @gen.coroutine
    def post(self):
        keys = ["role_id", "role_type", "action", "platform"]
        post_data = {}
        for key in keys:
            form_data = getattr(getattr(self.form, key), 'data', None)
            if form_data:
                post_data[key] = form_data
        result = yield risk_api_util.query_risk_api("merchant_credit_setting", method="POST", body=post_data)
        print result, type(result)

        is_success, error_mesage = risk_api_util.check_response(result)
        if is_success:
            response = common.scc_rsp(200, '操作成功')
        else:
            response = common.f_rsp(406, error_mesage)
        self.write(response)
        self.finish()
