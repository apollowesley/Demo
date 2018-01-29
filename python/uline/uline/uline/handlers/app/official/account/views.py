# -*- coding: utf-8 -*-
import json
import random
from tornado.gen import coroutine, Return
from tornado.httpclient import AsyncHTTPClient
from tornado.web import authenticated, HTTPError, asynchronous

from uline.handlers.baseHandlers import OfclAdminHandler
from uline.public import log
from uline.public.baseDB import DbClient
from uline.public.common import bcrypt_pwd, bcrypt_pwd_new, timestamp_now
from .form import LoginForm, ChangePasswordForm, AuthCodeForm, ModifyPasswordForm
from uline.settings import env, MESSAGE_URL
from uline.public.permit import check_permission

import tcelery

tcelery.setup_nonblocking_producer()


class OfclIndexHanddler(OfclAdminHandler):

    @authenticated
    @check_permission
    def get(self):
        self.render('official/account/index.html')


class OfclLoginHanddler(OfclAdminHandler):

    def prepare(self):
        self.form = LoginForm(self)
        if self.request.method == 'POST':
            if not self.form.validate():
                self.redirect('/official/login')
            else:
                self.dbClient = DbClient()
                self.rdsClient = self.application.client

    def get(self):
        if self.get_current_user():
            self.redirect('/official/')
            return
        self.render('official/account/login.html', passwdMsg='', form=self.form)

    @coroutine
    def post(self):
        email = self.form.email.data
        password = self.form.password.data

        db_ret = yield self.auth_user(email, password)
        if db_ret:
            self.session['ub_id'] = db_ret[0]
            self.session['ub_name'] = db_ret[2]
            self.session.save()
            self.redirect('/official/')
        else:
            self.render('official/account/login.html', passwdMsg=u'账号或密码错误', form=self.form)

    @coroutine
    def auth_user(self, email, password):
        valid = False
        selSql = "select ub_id,password,ub_name from ub_user where email=%s"
        db_ret = self.dbClient.selectSQL(selSql, (email,))
        if db_ret:
            valid = yield bcrypt_pwd(password, db_ret[1])
        raise Return(valid and db_ret)


class OfclLogoutHanddler(OfclAdminHandler):

    @authenticated
    def get(self):
        self.session['ub_id'] = None
        self.session.save()
        self.redirect('/official/login')


class OfclResetPasswordHandler(OfclAdminHandler):

    @authenticated
    def prepare(self):
        self.form = ChangePasswordForm(self)

    def get(self):
        self.render('official/cgPassword.html')

    def post(self):
        email = self.form.email.data
        ub_id = self.current_user
        if self.auth_email(email, ub_id):
            self.redirect('/official/resetpasswd/auth')
        else:
            self.render('official/cgPassword.html')

    def auth_email(self, email, ub_id):
        return self.db.selectSQL("select 1 from ub_user where email=%s and ub_id=%s", (email, ub_id))


class OfclResetPasswordAuthHandler(OfclAdminHandler):

    @authenticated
    def get(self):
        self.render('official/cgPassword2.html')

    def post(self):
        form = AuthCodeForm(self)
        if not form.validate():
            self.render('official/cgPassword2.html')
            return
        auth_code = form.auth_code.data
        if self.check_auth_code(auth_code):
            self.redirect('/official/resetpasswd/modify')
            return
        self.render('official/cgPassword2.html')

    def check_auth_code(self, auth_code):
        ub_id = self.session['ub_id']
        key = str(ub_id) + ':AuthChangePass'
        if self.rdb.get(key) == auth_code:
            return True
        return False


class OfclResetPasswordAuthCodeHandler(OfclAdminHandler):

    @asynchronous
    @coroutine
    @authenticated
    def get(self):
        msg = {'code': 406, 'msg': 'fail'}
        try:
            ub_id = self.current_user
            key = str(ub_id) + ':AuthChangePass'
            if self.rdb.get(key):
                auth_code = self.rdb.get(key)
            else:
                auth_code = str(random.randint(10000, 999999))
            email = self.get_ub_user_email(ub_id)[0]

            http_client = AsyncHTTPClient()
            data = {
                'env': env,
                'reciver': email,
                'title': u'uline验证码',
                'body': u'您的验证码是{},一个小时后失效。'.format(auth_code)
            }
            url = MESSAGE_URL + '/v1/email'
            response = yield http_client.fetch(url, method='POST', body=json.dumps(data))

            if str(response.body) == '2' and self.rdb.set(key, auth_code, 60 * 60):
                msg = {'code': 200, 'msg': 'success', 'data': email}
            else:
                msg = {'code': 406, 'msg': 'fail'}
        except Exception as err:
            log.exception.info(err)
        self.write(msg)

    def get_ub_user_email(self, ub_id):
        return self.db.selectSQL("select email from ub_user where ub_id=%s", (ub_id,))


class OfclResetPasswordModifyHandler(OfclAdminHandler):

    @authenticated
    def get(self):
        self.render('official/cgPassword3.html')

    def post(self):
        form = ModifyPasswordForm(self)
        new_pwd = form.newPwd.data
        check_pwd = form.checkPwd.data
        ub_id = self.current_user
        key = str(ub_id) + ':AuthChangePass'
        if not form.validate() and not (new_pwd == check_pwd):
            self.render('official/cgPassword3.html', form=form)
            return

        self.update_user_passwd(new_pwd)
        self.rdb.delete(key)

        self.redirect('/official/')

    def update_user_passwd(self, new_pwd):
        _password = bcrypt_pwd_new(str(new_pwd))
        ub_id = self.current_user
        update_at = timestamp_now()
        query = """update ub_user set password=%s,update_at=%s where ub_id=%s"""
        self.db.executeSQL(query, (_password, update_at, ub_id))


class TestMchEmailAsyncHandler(OfclAdminHandler):

    @asynchronous
    @coroutine
    @authenticated
    def get(self):
        http_client = AsyncHTTPClient()
        data = {
            'env': env,
            'reciver': 'zoulei@ulaiber.com',
            'title': u'uline商户激活信息',
            'body': u"""
XXXXXX有限公司，您好：
以下帐号重要信息请注意保密：
商户编号：100560015245
登录帐号：100560015245
初始登录密码：开户时填写的联系手机号 (登录后要求修改初始密码)
初始密钥：5f050213696dc7f6077fb5c9b1778549
登陆地址：https://cmb.uline.cc/merchant/login
温馨提示：
请妥善保管您的账号及密码，为安全起见，新申请的账号，首次登录后请立即修改管理员密码.

广州优畅信息技术有限公司
客服电话：4008047555"""
        }
        url = MESSAGE_URL + '/v1/email'
        response = yield http_client.fetch(url, method='POST', body=json.dumps(data))

        if str(response.body) == '1':
            self.write({'msg': 'wrong', 'code': 406})
            self.finish()
            return
        log.detail.info('test email have been sent!')
        self.write({'msg': 'ok', 'code': 200})


class TestDtEmailAsyncHandler(OfclAdminHandler):

    @asynchronous
    @coroutine
    @authenticated
    def get(self):
        http_client = AsyncHTTPClient()
        data = {
            'env': env,
            'reciver': 'zoulei@ulaiber.com',
            'title': u'uline商户激活信息',
            'body': u"""
XXXXXX有限公司，您好：
以下帐号重要信息请注意保密：
初始登录密码：开户时填写的联系手机号 (登录后要求修改初始密码)
初始密钥：5f050213696dc7f6077fb5c9b1778549
登陆地址：https://cmb.uline.cc/dist/login
温馨提示：
请妥善保管您的账号及密码，为安全起见，新申请的账号，首次登录后请立即修改管理员密码.

广州优畅信息技术有限公司
客服电话：4008047555"""
        }
        url = MESSAGE_URL + '/v1/email'
        response = yield http_client.fetch(url, method='POST', body=json.dumps(data))

        if str(response.body) == '1':
            self.write({'msg': 'wrong', 'code': 406})
            self.finish()
            return
        log.detail.info('test email have been sent!')
        self.write({'msg': 'ok', 'code': 200})


class TestSMSAsyncHandler(OfclAdminHandler):

    @asynchronous
    @coroutine
    @authenticated
    def get(self):
        http_client = AsyncHTTPClient()
        data = {
            'env': env,
            'reciver': '18772318985',
            'body': u'您的验证码是123456'
        }
        url = MESSAGE_URL + '/v1/message'
        response = yield http_client.fetch(url, method='POST', body=json.dumps(data))

        if str(response.body) == '1':
            self.write({'msg': 'wrong', 'code': 406})
            self.finish()
            return
        self.write({'msg': 'ok', 'code': 200})
