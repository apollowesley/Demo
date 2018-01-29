#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from tornado.web import authenticated

from uline.handlers.baseHandlers import BkAdminHandler
from uline.handlers.app.bank.subsidize.form import MchSubsidizeDetailForm
from uline.public.db import uline_session_scope
from uline.public import common, discount_util
from uline.public.permit import check_permission


class MchSubsidizeDetail(BkAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        self.form = MchSubsidizeDetailForm(self)
        if not self.form.validate():
            f_rsp = common.f_rsp(code=406, msg='fail')
            f_rsp['error_msg'] = self.form.errors
            self.finish(f_rsp)

    def get(self):
        role_id = self.form.role_id.data

        subsidize_info = {}
        if role_id:
            with uline_session_scope() as session:
                _, db_info = discount_util.get_mch_subsidize_info(session, {'mch_id': role_id}, fetchone=True)
                subsidize_info = {key: getattr(db_info, key) for key in db_info.keys()}
                subsidize_info['rate'] = json.loads(subsidize_info['rate']) if subsidize_info['rate']  else {}
                weixin = subsidize_info['rate'].get('weixin', 0)
                subsidize_info['create_at'] = subsidize_info['create_at'].strftime("%Y-%m-%d %H:%M:%S")
                if weixin:
                    subsidize_info['rate']['weixin'] = weixin / 100.0
                alipay = subsidize_info['rate'].get('alipay', 0)
                if alipay:
                    subsidize_info['rate']['alipay'] = alipay / 100.0
        s_rsp = common.scc_rsp(code=200, msg='success', **subsidize_info)
        self.write(s_rsp)
