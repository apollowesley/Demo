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
from uline.public.permit import check_permission
from uline.public.permit import (get_platform_permits, get_mr_sub_mch_permits,
                                 get_platform_role_permits, set_role_permits)
from uline.public.permit import permit_compatibility_platform


class PermitController(CommanHandler):

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

        # # # 测试代码
        # self.sys_type_id = 16
        # self.sys_type_code = "mr"
        # self.employee_id = 4
        # self.is_admin = self.session.get("is_admin", False)
        # self.sys_id = 10000074485

    def common_response(self, code, msg, data=None):
        self.write(json.dumps(
                    {'code': code, 'msg': msg, 'data': data if data else {}},
                    ensure_ascii=False))

    @run_on_executor
    def set_role_permits_thread(self, role_id, update_permits, sys_id,
                                sys_type_id, sys_type_code, employee_id, dbsession):
        return set_role_permits(role_id, update_permits, sys_id, sys_type_id,
                                sys_type_code, employee_id, dbsession)

    @run_on_executor
    def get_platform_permits_thread(self, sys_id, sys_type_id, sys_type_code, dbsession):
        platform_permits = get_platform_permits(sys_id, sys_type_id, dbsession)
        if not platform_permits:
            return [], []
        # 连锁商户要把连锁门店相关的权限查询出来
        sub_platform_permits = []
        if platform_permits and sys_type_code == "mr":
            sub_platform_permits = get_mr_sub_mch_permits(dbsession)

        return platform_permits, sub_platform_permits

    @run_on_executor
    def get_platfrom_and_role(self, role_id, sys_id, sys_type_id,
                              sys_type_code, dbsession):
        '''
        获取平台用户权限  以及 请求的角色id权限
        '''
        has_permits = []
        platform_permits = []
        sub_platform_permits = []
        flag, has_permits, role_info = get_platform_role_permits(
                            role_id, sys_id, sys_type_id, dbsession)
        if not flag:
            return False, [], [], []

        # 连锁商户创建的门店角色需要特殊处理
        if sys_type_code == "mr" and role_info["is_follower"]:
            sub_platform_permits = get_mr_sub_mch_permits(dbsession)
        else:
            platform_permits = get_platform_permits(
                                sys_id, sys_type_id, dbsession)

        return True, has_permits, platform_permits, sub_platform_permits


    def transform_model_name(self, spp):
        for row in spp:
            if row["model_name"].startswith("商户"):
                row["model_name"] = "门店" + row["model_name"][2:]
        return spp



    @tornado.web.authenticated
    @check_permission("/common/role")
    @tornado.gen.coroutine
    def get(self):
        self.common()
        role_id = self.get_argument("role_id", "").strip()
        if role_id and not role_id.isdigit():
            error = self.message.PARAMETER_DATA_ERROR
            error['msg'] = error['msg'].format("role_id")
            self.common_response(**error)
            return

        # 获取角色以及平台用户相关权限
        has_permits = []
        platform_permits = []
        spp = []
        if role_id:
            flag, has_permits, platform_permits, spp = yield self.get_platfrom_and_role(
                        role_id, self.sys_id, self.sys_type_id,
                        self.sys_type_code, self.dbsession)
            if not flag:
                self.common_response(**self.message.NO_PERMIT)
                return
        else:
            platform_permits, spp = yield self.get_platform_permits_thread(
                                    self.sys_id, self.sys_type_id,
                                    self.sys_type_code, self.dbsession)

        platform_permits = permit_compatibility_platform(self.sys_type_code, platform_permits)
        if spp:
            spp = self.transform_model_name(spp)

        result = {
            "has_permits": has_permits,
            "platform_permits": platform_permits,
            "sub_platform_permits": spp,
        }
        self.common_response(200, "Success", result)

    # @tornado.web.authenticated
    # @check_permission("/common/role")
    # @tornado.gen.coroutine
    # def post(self):
    #     self.common()
    #     try:
    #         form_data = json.loads(self.request.body)
    #         role_id = int(form_data["role_id"])
    #         update_permits = {int(i) for i in form_data["permits"]}
    #     except Exception as e:
    #         self.common_response(**self.message.JSON_ERROR)
    #         return
    #
    #     status = yield self.set_role_permits_thread(
    #                     role_id, update_permits, self.sys_id, self.sys_type_id,
    #                     self.sys_type_code, self.employee_id, self.dbsession)
    #     if not status:
    #         self.common_response(**self.message.NO_PERMIT)
    #         return
    #
    #     self.common_response(200, "Success")


