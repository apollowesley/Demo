#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @author: LiuFei
# @createTime: 2017-08-17 18:58:25
# @description: 权限基础对象

from __future__ import division
import os
import json
from tornado.web import authenticated, asynchronous
from tornado import gen
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
from uline.handlers.baseHandlers import CommanHandler
from uline.public import common, log
from uline.handlers.app.common.message import Message
from uline.handlers.app.common.encoder import Encoder


class BaseController(CommanHandler):
    executor = ThreadPoolExecutor(8)

    # @authenticated
    def prepare(self):
        self.model = None
        self.Model = None
        self.encoder = Encoder()

    def page_verify(self, page_num):
        if page_num:
            page_num = str(page_num)
            if page_num.isdigit():
                page_num = int(page_num)
                if page_num <= 0:
                    return False
                return True
        return False

    # 不校验xsrf
    def check_xsrf_cookie(self):
        pass

    @asynchronous
    @gen.coroutine
    def options(self, message=Message(), *args, **kwargs):
        """
        请求复杂资源的验证方法
        :param args:
        :param kwargs:
        :return:
        """
        self.write(json.dumps(message.SUCCESS))
