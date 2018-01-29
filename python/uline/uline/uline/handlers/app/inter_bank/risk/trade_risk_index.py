#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado import web, gen

from uline.public import common
from uline.handlers.baseHandlers import IntBkAdminHandler
from uline.handlers.app.bank.risk.form import TradeRiskSearchForm
from uline.settings import DEFAULT_BANK_ID
from uline.utils.risk_api.risk_api_util import query_risk_api, check_response
from uline.public.permit import check_permission


class TradeRiskIndexHandler(IntBkAdminHandler):
    @web.authenticated
    @check_permission
    def prepare(self):
        self.form = TradeRiskSearchForm(self)
        if not self.form.validate():
            self.redirect('/inter_bank/')
            return
        self.pageindex = int(self.get_argument("p", 1))
        self.render_url = 'inter_bank/risk/trade_risk.html'
        self.main_bk_id = DEFAULT_BANK_ID

    def generate_unchanged_render_params(self):
        return {
            "form": self.form,
            "datetime_to_str": common.datetime_to_str,
        }

    @gen.coroutine
    def get(self):
        query_keys = ['merchant_id', 'merchant_name', 'merchant_shortname', 'dt_id', 'dt_name', 'create_at_start',
                      'create_at_end', 'handle_status']
        query_conditions = {key: getattr(getattr(self.form, key), 'data', None) for key in query_keys}
        query_conditions['bk_id'] = self.current_user
        query_conditions['page'] = self.pageindex
        query_conditions = {key: value for key, value in query_conditions.items() if value}

        result = yield query_risk_api("trade_risk_list", params=query_conditions)
        is_success, error_msg = check_response(result)
        if not is_success:
            raise Exception(error_msg)
        trade_risk_list = result.get("trade_risk_list", [])
        total_num = result.get("total_num", 0)

        navigate_html = self.get_navigate_html(total_num, **query_conditions)
        self.render(self.render_url, navigate_html=navigate_html, trade_risk_list=trade_risk_list,
                    total_number=total_num)
