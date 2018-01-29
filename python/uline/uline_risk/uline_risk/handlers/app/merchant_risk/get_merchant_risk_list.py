#!/usr/bin/env python
# -*- coding: utf-8 -*-
from uline_risk.handlers.baseHandlers import RESTfulHandler, RESTfulException
from uline_risk.handlers.app.merchant_risk.form import MerchantRiskSearchForm
from uline_risk.utils.db import uline_session_scope
from uline_risk.public import merchant_risk_util


class MerchantListHandler(RESTfulHandler):
    def prepare(self):
        self.form = MerchantRiskSearchForm(self)
        if not self.form.validate():
            raise RESTfulException('params_error', error_detail=self.form.errors)

    def get(self):
        query_keys = ['has_risk', 'risk_type', 'risk_content', 'risk_id']
        query_conditions = {key: getattr(getattr(self.form, key), 'data', None) for key in query_keys}
        for key in query_conditions:
            if isinstance(query_conditions[key], bytes):
                query_conditions[key] = query_conditions[key].decode()
        page = self.form.page.data or 0
        page_size = self.form.page_size.data or 10
        with uline_session_scope() as session:
            total_num, merchant_risk_list = merchant_risk_util.get_all_merchant_risk_item(session, query_conditions,
                                                                                          page, page_size)
            merchant_risk_list = [{key: getattr(each_risk, key, '') for key in each_risk.keys()} for each_risk in
                                  merchant_risk_list]
        result_info = {
            'merchant_risk_list': merchant_risk_list,
            'total_num': total_num
        }
        response = self.generate_response_msg(**result_info)
        self.write(response)
        self.finish()
