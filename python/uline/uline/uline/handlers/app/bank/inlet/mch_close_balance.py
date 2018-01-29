#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: ficapy
# Create: '7/26/17'
import bcrypt
import tornado.web
import tornado.gen
from functools import wraps
from uline.public import common
from uline.handlers.baseHandlers import BkAdminHandler
from uline.model.uline.base import uline_session
from uline.model.uline.user import BkUser
from uline.model.uline.info import MchBalance
from uline.public.permit import check_permission


# 冻结或者解冻商户

# 先把装饰器写在这里吧 ，其实可以作为一个通用的函数的
def need_password(field='password'):
    def valid(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            input_password = self.get_arguments(field)
            input_password = input_password[0] if input_password else '1' * 99
            bk_id = self.session.get('bk_id')
            if not bk_id:
                raise tornado.web.HTTPError(403)
            password = uline_session.query(BkUser.password).filter_by(bk_id=bk_id).first().password
            result = bcrypt.checkpw(tornado.escape.utf8(input_password), tornado.escape.utf8(password))
            if result:
                return func(self, *args, **kwargs)
            else:
                raise tornado.web.HTTPError(403)

        return inner

    return valid


class CloseBalanceHandle(BkAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        pass

    @need_password(field='password')
    def post(self):
        # 默认为空，1为冻结  2为解冻
        rsp = common.scc_rsp(code=200, msg='success')
        mch_id = self.get_arguments('mch_id')[0]
        current = uline_session.query(MchBalance.status).filter_by(mch_id=mch_id)
        current_status = current.status
        if current_status == None:
            modify = 1
        elif current_status == 1:
            modify = 2
        elif current_status == 2:
            modify = 1
        else:
            raise Exception("我也不知道你到底想干什么")
        current.status = modify
        return self.write(rsp)
