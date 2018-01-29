#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from datetime import timedelta

from tornado import gen
from tornado.web import authenticated, asynchronous

from uline.handlers.baseHandlers import BkAdminHandler
from .form import MerchantWithdrawSearch
from uline.handlers.app.common import merchant_capital_util
from uline.public.db import uline_session_scope
from uline.public import common, constants
from uline.public.permit import check_permission


class MchWithdrawIndexHandler(BkAdminHandler):
    @authenticated
    @check_permission
    def prepare(self):
        self.form = MerchantWithdrawSearch(self)
        # 查询参数不合法
        if not self.form.validate():
            self.redirect('/bank/')
            return
        self.pageindex = int(self.get_argument("p", 1))
        self.render_url = 'bank/capital/capital.html'

    @gen.coroutine
    def get(self):
        query_keys = ['create_at_start', 'create_at_end', 'mch_clear_no', 'channel', 'pay_status', 'mch_clear_no',
                      'mch_name',
                      'mch_shortname', 'mch_id', 'dt_name', 'dt_id', 'settle_card']

        query_conditions = {key: getattr(getattr(self.form, key), 'data', None) for key in query_keys}
        total_number, data = self.db_execute(self.pageindex - 1, 10, query_conditions)
        query_conditions = {key: query_conditions[key] for key in query_conditions if query_conditions[key]}
        navigate_html = self.get_navigate_html(total_number, **query_conditions)
        self.render(
            self.render_url,
            navigate_html=navigate_html, data=data,
            total_number=total_number
        )

    def generate_unchanged_render_params(self):
        return {
            "form": self.form,
            "datetime_to_str": common.datetime_to_str,
            "print_pay_status": merchant_capital_util.get_capital_pay_status,
        }

    @gen.coroutine
    def post(self):
        self.get()

    def db_execute(self, page, page_size, query_conditions):

        data_list = []
        count = 0
        with uline_session_scope() as session:
            count, withdraw_list = merchant_capital_util.get_merchant_capital_list(session, query_conditions, page)
            for each_withdraw in withdraw_list:
                withdraw_info = {key: getattr(each_withdraw, key, '') for key in each_withdraw.keys()}
                business_type = withdraw_info.get('business_type', '')
                withdraw_info['business_type'] = constants.MCH_CLEAR_TYPES.get(int(business_type), '')
                withdraw_info['pay_status'] = merchant_capital_util.get_capital_pay_status(business_type,
                                                                                           withdraw_info.get(
                                                                                               'pay_status', ''))
                data_list.append(withdraw_info)
        return count, data_list
