# -*- coding: utf-8 -*-
'''
BEGIN
添加商户进件信息
    必选参数:

    可选参数:

    成功:
        {"code": 200, "msg": "成功"}
    失败:
        {"code": 406, "msg": "失败"}
END
'''
import json
import uuid
from datetime import date

import os
from tornado import gen
from tornado.web import authenticated, asynchronous

from uline.handlers.baseHandlers import OfclAdminHandler
from uline.public import common
from uline.public.constants import BANK_TYPE
from uline.utils.record import record_utils
from uline.public.constants import PAY_TYPES
from .form import ModifyInterBankInlet
from datetime import datetime, date
from decimal import Decimal
from uline.settings import FEATURE_SWITCH
from uline.utils.dayzero import form_verify
from uline.public.permit import check_permission
from uline.model.uline.user import Employee
from uline.model.uline.info import UserProfile
from uline.model.uline.base import uline_session


class ModifyInterBnakInletHandler(OfclAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        self.form = ModifyInterBankInlet(self)
        self.form.validate()

    def has_inter(self):
        query = """select 1 from bk_user where bk_id=%s and bk_type=%s;"""
        result = self.db.selectSQL(query, (self.bk_id, BANK_TYPE.get("inter")))
        return bool(result)

    @asynchronous
    @gen.coroutine
    def post(self):
        if self.form.errors:
            self.write({"code": "1000", "message": self.form.errors})
            return

        self.bk_id = self.form.bk_id.data
        self.email = self.form.email.data
        self.update_at = common.timestamp_now()
        with self.db.get_db() as cur:
            yield self.update_inlet_info(cur)
        self.write({"code": "200", "message": "修改成功"})

    @gen.coroutine
    def update_inlet_info(self, cursor):
        sql = "update bk_user set email=%s,update_at=%s where bk_id=%s"
        args = (self.email, self.update_at, self.bk_id)
        cursor.execute(sql, args)
        employee = uline_session.query(Employee).filter(Employee.login_name == str(self.bk_id) + ".bk").one()
        uline_session.query(UserProfile).filter(UserProfile.id == employee.user_id).update({'email': self.email})
        uline_session.commit()


class ComplexEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)
