#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from datetime import timedelta

from tornado import gen
from tornado.web import authenticated, asynchronous

from uline.handlers.baseHandlers import OfclAdminHandler
from .form import MerchantWithdrawDetail
from uline.handlers.app.common import merchant_capital_util
from uline.public.db import uline_session_scope
from uline.public import constants, common
from uline.public.permit import check_permission


class MchWithdrawDetailHandler(OfclAdminHandler):
    @authenticated
    @check_permission
    def prepare(self):
        self.form = MerchantWithdrawDetail(self)
        # 查询参数不合法
        if not self.form.validate():
            self.redirect('/official/')
            return
        self.render_html = 'official/capital/capitalDetail.html'

    def generate_unchanged_render_params(self):
        return {
            "datetime_to_str": common.datetime_to_str
        }

    @gen.coroutine
    def get(self):
        withdraw_info = self.db_execute()
        self.render(self.render_html, data=withdraw_info)

    @gen.coroutine
    def post(self):
        self.get()

    def db_execute(self):
        mch_clear_no = self.form.mch_clear_no.data
        query_conditions = {'mch_clear_no': mch_clear_no}
        mch_clear_info = {}
        with uline_session_scope() as session:
            count, withdraw_info = merchant_capital_util.get_merchant_capital_list(session, query_conditions,
                                                                                   fetchone=True)
            if withdraw_info:
                mch_clear_info = {key: getattr(withdraw_info, key, '') for key in withdraw_info.keys()}
                business_type = mch_clear_info.get('business_type', '')
                mch_clear_info['business_type'] = constants.MCH_CLEAR_TYPES.get(int(business_type), '')
                mch_clear_info['pay_status'] = merchant_capital_util.get_capital_pay_status(business_type,
                                                                                            mch_clear_info.get(
                                                                                                'pay_status', ''))
        return mch_clear_info
