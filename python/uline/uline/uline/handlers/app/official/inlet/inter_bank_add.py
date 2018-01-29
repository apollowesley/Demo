# -*- coding: utf-8 -*-
'''
BEGIN
添加同业银行进件信息
    必选参数:

    可选参数:

    成功:
        {"code": 200, "msg": "成功"}
    失败:
        {"code": 406, "msg": "失败"}
END
'''
import os
import uuid
from tornado import gen
from uline.public import log
from uline.handlers.baseHandlers import OfclAdminHandler
from uline.public import common, generate_employee_profile
from tornado.web import authenticated, HTTPError
from .form import AddInterBankInlet
from decimal import Decimal
from uline.public.constants import DEFAULT_INTER_BANK_PASSWORD, BANK_TYPE
from uline.settings import FEATURE_SWITCH
from uline.utils.dayzero import form_verify
from uline.public.permit import check_permission


class AddInterBankInletHandler(OfclAdminHandler):
    @authenticated
    @check_permission
    def prepare(self):
        self.form = AddInterBankInlet(self)
        self.form.validate()

    @gen.coroutine
    @authenticated
    def post(self):
        if self.form.errors:
            self.write({"code": "1000", "message": self.form.errors})
            return
        self.bk_id = common.create_bk_id()
        self.bk_name = self.form.bk_name.data
        self.email = self.form.email.data
        self.bank_type = BANK_TYPE.get("inter")
        _password = self.email.split("@")[0] + DEFAULT_INTER_BANK_PASSWORD
        self.password = yield common.bcrypt_pwd(str(_password))
        self.create_at = self.update_at = common.timestamp_now()

        with self.db.get_db() as cur:
            yield self.create_inter_bank_user(cur)
            yield generate_employee_profile.employee_profile("bk", self.bk_id, self.email,
                                                             self.password, self.bk_name,
                                                             phone1=None, city=None, sex=None)
        self.write({"code": "200", "message": "添加成功"})

    @gen.coroutine
    def create_inter_bank_user(self, cursor):
        cursor.execute(
            """
            INSERT INTO bk_user(bk_id, bk_name, email, password, bk_type, create_at, update_at)
             VALUES(%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                self.bk_id, self.bk_name, self.email, self.password,
                self.bank_type, self.create_at, self.update_at
            )
        )
