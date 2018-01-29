# -*- coding: utf-8 -*-
from __future__ import division
import json
import tornado.web
from tornado import gen
from tornado.web import asynchronous
from uline.settings import FEATURE_SWITCH


class MchCapitalStatusHandler(tornado.web.RequestHandler):
    @asynchronous
    @gen.coroutine
    def get(self):
        self.write(json.dumps({'OPEN_D0': FEATURE_SWITCH.get('OPEN_D0')}))
