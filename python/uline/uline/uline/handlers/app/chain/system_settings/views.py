# -*- coding: utf-8 -*-
import hashlib
import json
import random
import datetime
from tornado import gen
from tornado.gen import coroutine, Return
from tornado.httpclient import AsyncHTTPClient
from tornado.web import authenticated, HTTPError, asynchronous
from uline.handlers.baseHandlers import ChainAdminHandler
from .form import AuthCodeForm, ModifyRefundPasswordForm, ValidationRefundPasswordForm
from uline.public.common import bcrypt_pwd, bcrypt_pwd_new, timestamp_now
from uline.public import log
from uline.settings import MESSAGE_URL, env
from uline.public import common
from uline.public.permit import check_permission


class ChainRefundPasswordHandler(ChainAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        self.chain_id = self.current_user

    @asynchronous
    @gen.coroutine
    def get(self):
        mch_refund_password = self.get_chain_refund_password()
        self.render('chain/system_settings/csSettingRefundPassword.html',
                    mch_refund_password=mch_refund_password)

    def get_chain_refund_password(self):
        query = """select refund_password from dt_user where dt_id=%s;"""
        mch_refund_password = self.db.selectSQL(query, (self.chain_id,))
        return mch_refund_password[0] if mch_refund_password else None


class ChainSetRefundPasswordAuthCodeHandler(ChainAdminHandler):

    @asynchronous
    @coroutine
    @authenticated
    @check_permission
    def get(self):
        msg = {'code': 406, 'msg': 'fail'}
        try:
            chain_id = self.current_user
            key = str(chain_id) + ':AuthChangeRefundPassword'

            if self.rdb.get(key):
                auth_code = self.rdb.get(key)
            else:
                auth_code = str(random.randint(10000, 999999))

            mobile = self.get_chain_user_mobile(chain_id)[0]

            http_client = AsyncHTTPClient()
            data = {
                'env': env,
                'reciver': mobile,
                'body': u'您的验证码是{},一个小时后失效。'.format(auth_code)
            }
            url = MESSAGE_URL + '/v1/message'

            # 测试，暂时返回成功

            # msg = {'code': 200, 'msg': 'success', 'data': mobile}

            response = yield http_client.fetch(url, method='POST', body=json.dumps(data))

            if str(response.body) == '2' and self.rdb.set(key, auth_code, 60 * 60):
                msg = {'code': 200, 'msg': 'success', 'data': mobile}
            else:
                msg = {'code': 406, 'msg': 'fail'}
        except Exception as err:
            log.exception.info(err)
        self.write(msg)

    def get_chain_user_mobile(self, chain_id):
        return self.db.selectSQL("select mobile from dt_inlet_info where dt_id=%s", (chain_id,))


class ChainSetRefundPasswordAuthHandler(ChainAdminHandler):

    @authenticated
    @check_permission
    def get(self):
        form = AuthCodeForm(self)
        if form.validate():
            auth_code = form.auth_code.data
            if self.check_auth_code(auth_code):
                f_rsp = common.f_rsp(code=200, msg='success')
                self.finish(f_rsp)
                return
        f_rsp = common.f_rsp(code=406, msg='Invalid verification code')
        self.finish(f_rsp)

    def check_auth_code(self, auth_code):
        chain_id = self.current_user
        key = str(chain_id) + ':AuthChangeRefundPassword'
        if self.rdb.get(key) == auth_code:
            return True
        return False


class ChainSetRefundPasswordModifyHandler(ChainAdminHandler):

    @authenticated
    @check_permission
    def get(self):
        new_pwd = self.get_argument('newPwd')
        check_pwd = self.get_argument('checkPwd')
        chain_id = self.current_user
        key = str(chain_id) + ':AuthChangeRefundPassword'
        if len(new_pwd) != 6 or not (new_pwd == check_pwd):
            f_rsp = common.f_rsp(code=406, msg='Invalid verification code')
            self.finish(f_rsp)
            return

        self.update_user_refund_passwd(new_pwd)
        self.rdb.delete(key)

        f_rsp = common.f_rsp(code=200, msg='success')
        self.finish(f_rsp)
        return

    def update_user_refund_passwd(self, new_pwd):
        _password = bcrypt_pwd_new(str(new_pwd))
        chain_id = self.current_user
        update_at = timestamp_now()
        query = """update dt_user set refund_password=%s,update_at=%s where dt_id=%s"""
        self.db.executeSQL(query, (_password, update_at, chain_id))
