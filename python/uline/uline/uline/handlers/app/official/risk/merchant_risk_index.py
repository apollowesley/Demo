#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado import gen, web

from uline.handlers.baseHandlers import OfclAdminHandler
from uline.public import merchant_risk_util, common
from uline.handlers.app.bank.risk.form import MerchantRiskSearchForm
from uline.utils.risk_api import risk_api_util
from uline.public.permit import check_permission


class MerchantRiskIndexHandler(OfclAdminHandler):
    @web.authenticated
    @check_permission
    def prepare(self):
        self.form = MerchantRiskSearchForm(self)
        if not self.form.validate():
            self.redirect('/official/')
            return
        self.pageindex = int(self.get_argument("p", 1))
        self.render_url = 'official/risk/merchant_risk.html'

    def generate_unchanged_render_params(self):
        return {
            "form": self.form,
            "datetime_to_str": common.datetime_to_str,
            "print_merchant_risk_type": merchant_risk_util.print_merchant_risk_type
        }

    @gen.coroutine
    def get(self):
        query_keys = ['has_risk', 'risk_type', 'risk_content']
        query_conditions = {key: getattr(getattr(self.form, key), 'data', None) for key in query_keys}
        query_conditions = {key: value for key, value in query_conditions.items() if value}
        query_conditions["page"] = self.pageindex - 1

        result = yield risk_api_util.query_risk_api("merchant_risk_list", method="GET", params=query_conditions)
        is_success, error_msg = risk_api_util.check_response(result)
        if not is_success:
            raise Exception(error_msg)

        merchant_risk_list = result.get('merchant_risk_list', [])
        total_num = result.get("total_num", 0)

        navigate_html = self.get_navigate_html(total_num, **query_conditions)
        self.render(self.render_url, navigate_html=navigate_html, merchant_risk_list=merchant_risk_list,
                    total_number=total_num)
