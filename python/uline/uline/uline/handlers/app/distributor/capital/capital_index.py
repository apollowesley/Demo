# -*- coding: utf-8 -*-
from __future__ import division
import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import DtAdminHandler
from datetime import timedelta, datetime
from uline.public.constants import TO_PAY, PAY_CHANNEL


class DistCapitalIndexHandler(DtAdminHandler):

    def get(self):
        self.render('dist/capital/capital.html')

    def post(self):
        pass
