#!/usr/bin/env python
# -*- coding: utf-8 -*-
from uline_risk.handlers.baseHandlers import RESTfulHandler
from uline_risk.handlers.app.trade_risk.form import QueyTradeRiskForm
from uline_risk.utils.db import uline_session_scope
from uline_risk.public.trade_risk_util import get_trade_risk_info


class QueryTradeRiskList(RESTfulHandler):
    def prepare(self):
        self.form = QueyTradeRiskForm(self)
        bk_id = self.get_argument('bk_id', '')
        if bk_id:
            bk_id = bk_id.split(',')
        self.bk_id = bk_id

    def get(self):
        query_keys = ['merchant_id', 'merchant_name', 'merchant_shortname', 'dt_id', 'dt_name', 'create_at_start',
                      'create_at_end', 'handle_status', 'risk_id']
        query_conditions = {key: getattr(getattr(self.form, key), 'data', None) for key in query_keys}
        query_conditions['bk_id'] = self.bk_id
        page = self.form.page.data or 0
        page_size = self.form.page_size.data or 10
        with uline_session_scope() as session:
            total_num, trade_risk_list = get_trade_risk_info(session, query_conditions, page, page_size)
            trade_risk_list = [{key: getattr(each_risk, key, '') for key in each_risk.keys()} for each_risk in
                               trade_risk_list]
        response = self.generate_response_msg(**{'trade_risk_list': trade_risk_list, 'total_num': total_num})
        self.write(response)
        self.finish()
