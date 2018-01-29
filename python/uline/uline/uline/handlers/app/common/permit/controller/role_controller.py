#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import json
import time
import functools

import tornado.web
import tornado.gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from uline.handlers.app.common.system_settings.common import LOCAL_HTML
from uline.model.uline.base import uline_session
from uline.handlers.app.common.message import Message
from uline.handlers.baseHandlers import CommanHandler
from uline.public.permit import check_permission
from uline.public.permit import add_role, update_role, delete_role, get_role


class RoleController(CommanHandler):

    def prepare(self):
        # 确保能在多线程环境中使用同一个db session会话
        self.dbsession = uline_session()
        self.message = Message()

    def common(self):
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
    def get_role(self, dbsession, sys_type_id, sys_id, get_type, page_index=1, page_size=10):
        return get_role(dbsession, sys_type_id, sys_id, get_type, page_index, page_size)

    @run_on_executor
    def add_role(self, dbsession, name, sys_type_id, sys_id, sys_type_code, employee_id, update_permits, is_follower):
        return add_role(dbsession, name, sys_type_id, sys_id, sys_type_code, employee_id, update_permits, is_follower=is_follower)

    @run_on_executor
    def update_role(self, dbsession, name, role_id, update_permits, sys_id, sys_type_id,
                    sys_type_code, employee_id):
        return update_role(dbsession, name, role_id, update_permits, sys_id, sys_type_id,
                           sys_type_code, employee_id)

    @run_on_executor
    def delete_role(self, dbsession, role_id):
        return delete_role(dbsession, role_id, self.employee_id)

    @tornado.web.authenticated
    @check_permission("/common/role")
    @tornado.gen.coroutine
    def get(self):
        self.common()

        page_index = self.get_argument("p", "1")
        page_size = self.get_argument("page_size", "10")

        if not (str(page_index).isdigit() and str(page_size).isdigit()):
            self.common_response(700, "请输入有效的页码")
            return

        total_num, data = yield self.get_role(self.dbsession, self.sys_type_id, self.sys_id, "more", page_index, page_size)
        navigate_html = self.get_navigate_html(total_num)

        data_html = self.render_string('common/roleManagement.html', sys_type_code=self.sys_type_code,
                                       navigate_html=navigate_html, data=data)

        html = '{}/system_settings/roleManagementIndex.html'.format(LOCAL_HTML[self.sys_type_code])
        self.render(html, data_html=data_html, total_num=total_num)
        return

    @tornado.web.authenticated
    @check_permission("/common/role")
    @tornado.gen.coroutine
    def post(self):
        self.common()
        name = self.get_argument("name", "")
        is_follower = self.get_argument("is_follower", "0")
        if name and is_follower in ("0", "1"):
            update_permits = {int(i) for i in json.loads(self.get_argument("permits", []))}
            status, result = yield self.add_role(
                self.dbsession, name,
                self.sys_type_id, self.sys_id,
                self.sys_type_code, self.employee_id,
                update_permits, is_follower
            )
            if not status:
                self.common_response(700, result)
                return
            self.common_response(200, "Success")
            return
        self.common_response(700, "无效的数据")

    @tornado.web.authenticated
    @check_permission("/common/role")
    @tornado.gen.coroutine
    def put(self):
        self.common()

        name = self.get_argument("name", "")
        role_id = self.get_argument("role_id", "")

        if name and role_id:
            update_permits = {int(i) for i in json.loads(self.get_argument("permits", []))}
            status, message = yield self.update_role(
                self.dbsession, name,
                role_id, update_permits,
                self.sys_id, self.sys_type_id,
                self.sys_type_code, self.employee_id
            )

            if not status:
                self.common_response(700, message)
                return

            self.common_response(200, "Success")
            return

        self.common_response(700, "传输数据异常")

    @tornado.web.authenticated
    @check_permission("/common/role")
    @tornado.gen.coroutine
    def delete(self):
        self.common()
        role_id = self.get_argument("role_id", "")

        status, message = yield self.delete_role(
            self.dbsession,
            role_id
        )

        if not status:
            self.common_response(700, message)
            return

        self.common_response(200, "Success")
