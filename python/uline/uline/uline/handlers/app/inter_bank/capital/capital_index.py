# -*- coding: utf-8 -*-
from __future__ import division
import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import BkAdminHandler
from datetime import timedelta, datetime
from uline.public.constants import TO_PAY, PAY_CHANNEL


class BankCapitalIndexHandler(BkAdminHandler):

    def get(self):
        self.render('bank/capital/capital.html')

    def post(self):
        pass
