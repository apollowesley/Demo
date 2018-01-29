#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import json

import tornado.web
import tornado.gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

from uline.model.uline.base import uline_session
from uline.handlers.app.common.message import Message
from uline.handlers.baseHandlers import CommanHandler
from uline.public.permit import get_user_permits


class HavePermitController(CommanHandler):

    @tornado.web.authenticated
    def prepare(self):
        # 确保能在多线程环境中使用同一个db session会话
        self.dbsession = uline_session()
        self.message = Message()
        self.sys_type_id = self.session.get("sys_type_id")
        self.sys_type_code = self.session.get("sys_type_code")
        self.employee_id = self.session.get("employee_id")
        self.is_admin = self.session.get("is_admin", False)
        self.sys_id = self.get_user_id(self.sys_type_code)

    def common_response(self, code, msg, data=None):
        self.write(json.dumps(
                    {'code': code, 'msg': msg, 'data': data if data else {}},
                    ensure_ascii=False))

    @run_on_executor
    def get_user_permits_thread(self, employee_id, sys_type_id, dbsession):
        return get_user_permits(employee_id, sys_type_id, dbsession)

    def transform_model_name(self, spp):
        for row in spp:
            if row["model_name"].startswith("商户"):
                row["model_name"] = "门店" + row["model_name"][2:]
        return spp

    @tornado.gen.coroutine
    def get(self):
        permission = yield self.get_user_permits_thread(
                            self.employee_id, self.sys_type_id, self.dbsession)

        result = {"cs_name": False}
        if self.session.get('cs_name'):
            permission = self.transform_model_name(permission)
            result["cs_name"] = True

        result["permission"] = permission
        self.common_response(200, "Success", result)


