#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from tornado.web import authenticated

from uline.handlers.baseHandlers import BkAdminHandler
from uline.handlers.app.bank.subsidize.form import MchSubsidizeSearch
from uline.public.db import uline_session_scope
from uline.public import discount_util
from uline.public.permit import check_permission


class MchSubsidizeIndexHandler(BkAdminHandler):
    @authenticated
    @check_permission
    def prepare(self):
        self.form = MchSubsidizeSearch(self)

    def generate_unchanged_render_params(self):
        return {
            'form': self.form,
        }

    def get(self):
        page = int(self.get_argument('p', 1))
        total_num = 0
        subsidize_data_list = []
        query_keys = ['status', 'mch_id', 'mch_name', 'dt_id', 'dt_name']
        query_params = {key: getattr(getattr(self.form, key), 'data', None) for key in query_keys}
        with uline_session_scope() as session:
            total_num, subsidize_data = discount_util.get_mch_subsidize_info(session, query_params, page=page - 1)
            for each_subsidize in subsidize_data:
                subsidize_info = {key: getattr(each_subsidize, key) for key in each_subsidize.keys()}
                subsidize_info['rate'] = json.loads(subsidize_info['rate']) if subsidize_info['rate'] else {}
                subsidize_data_list.append(subsidize_info)
        render_params = {
            'navigate_html': self.get_navigate_html(total_num),
            'total_num': total_num,
            'subsidize_list': subsidize_data_list
        }

        self.render('bank/subsidize/mchActivity.html', **render_params)

    def post(self):
        pass
