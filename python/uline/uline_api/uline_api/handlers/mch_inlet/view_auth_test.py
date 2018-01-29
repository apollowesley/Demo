#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '12/2/16'

from tornado.gen import coroutine
from uline_api.handlers.baseHandlers import RESTfulHandler


class AuthTest(RESTfulHandler):

    @coroutine
    def get(self):
        self.finish({})

    @coroutine
    def post(self):
        self.finish({})
