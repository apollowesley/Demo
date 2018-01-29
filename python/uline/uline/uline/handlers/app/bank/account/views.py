# -*- coding: utf-8 -*-
import datetime
import json
import random
from tornado.gen import coroutine, Return
from tornado.httpclient import AsyncHTTPClient
from tornado.web import authenticated, HTTPError, asynchronous

from uline.settings import MESSAGE_URL
from uline.settings import env, use_secure_cookie
from uline.handlers.baseHandlers import BkAdminHandler
from uline.public.baseDB import DbClient
from uline.public.common import bcrypt_pwd, bcrypt_pwd_new
from .form import LoginForm, ChangePasswordForm, AuthCodeForm, ModifyPasswordForm
from uline.public import log
from uline.public.permit import check_permission

import tcelery

tcelery.setup_nonblocking_producer()


class BkIndexHanddler(BkAdminHandler):

    @authenticated
    @check_permission
    def get(self):
        self.render('bank/account/index.html')


class BkLoginHanddler(BkAdminHandler):

    def prepare(self):
        self.form = LoginForm(self)
        if self.request.method == 'POST':
            if not self.form.validate():
                self.redirect('/bank/login')
            else:
                self.dbClient = DbClient()
                self.rdsClient = self.application.client

    def get(self):
        if self.get_current_user():
            self.redirect('/bank/')
            return
        self.render('bank/account/login.html', passwdMsg='', form=self.form)

    @coroutine
    def post(self):
        email = self.form.email.data
        password = self.form.password.data

        db_ret = yield self.auth_user(email, password)
        if db_ret:
            if not use_secure_cookie:
                self.session['bk_id'] = db_ret[0]
                self.session['bk_name'] = db_ret[2]
                self.session.save()
            else:
                # expires = datetime.datetime.now() + datetime.timedelta(minutes=60)
                # 一天有效期
                self.set_secure_cookie('bk_id', str(db_ret[0]), expires_days=1)
                self.set_secure_cookie('bk_name', db_ret[2], expires_days=1)
            self.redirect('/bank/')
        else:
            # 暂时注释银行子帐号登录
            # bk_user 中找不到记录
            # db_ret = yield self.auth_subuser(email, password)
            # if db_ret:
            #     self.session['bk_id'] = db_ret[3]
            #     print db_ret[3]
            #     self.session['bk_name'] = self.get_ub_user_name(str(db_ret[3]))[0]
            #     self.session['bk_sub_id'] = db_ret[0]
            #     self.session['bk_sub_name'] = db_ret[2]
            #     self.session.save()
            #     self.redirect('/bank/')
            # else:
            #     self.render('bank/account/login.html', passwdMsg=u'账号或密码错误', form=self.form)
            self.render('bank/account/login.html', passwdMsg=u'账号或密码错误', form=self.form)

    @coroutine
    def auth_user(self, email, password):
        valid = False
        selSql = "select bk_id,password,bk_name from bk_user where email=%s and bk_type=1"
        db_ret = self.dbClient.selectSQL(selSql, (email,))
        if db_ret:
            valid = yield bcrypt_pwd(password, db_ret[1])
        raise Return(valid and db_ret)

    @coroutine
    def auth_subuser(self, email, password):
        valid = False
        selSql = "select bk_sub_id,password,bk_sub_name,bk_user_bk_id from bk_subuser where email=%s"
        db_ret = self.dbClient.selectSQL(selSql, (email,))
        if db_ret:
            valid = yield bcrypt_pwd(password, db_ret[1])
        raise Return(valid and db_ret)


class BkLogoutHanddler(BkAdminHandler):

    @authenticated
    def get(self):
        self.session['bk_id'] = None
        self.session['bk_sub_id'] = None
        self.session.save()

        self.clear_cookie('bk_id')
        self.clear_cookie('bk_sub_id')

        self.redirect('/bank/login')


class BkResetPasswordHandler(BkAdminHandler):

    @authenticated
    def prepare(self):
        self.form = ChangePasswordForm(self)

    def get(self):
        self.render('bank/cgPassword.html')

    def post(self):
        email = self.form.email.data
        bk_id = self.current_user
        bk_sub_id = self.get_current_subuser()
        if bk_sub_id:
            if self.auth_subuser_email(email, bk_sub_id):
                self.redirect('/bank/resetpasswd/auth')
                return
        else:
            if self.auth_email(email, bk_id):
                self.redirect('/bank/resetpasswd/auth')
                return
            # else:
        self.render('bank/cgPassword.html')

    def auth_email(self, email, bk_id):
        return self.db.selectSQL("select 1 from bk_user where email=%s and bk_id=%s and bk_type=1", (email, bk_id))

    def auth_subuser_email(self, email, bk_sub_id):
        return self.db.selectSQL("select 1 from bk_subuser where email=%s and bk_sub_id=%s", (email, bk_sub_id))


class BkResetPasswordAuthHandler(BkAdminHandler):

    @authenticated
    def get(self):
        self.render('bank/cgPassword2.html')

    def post(self):
        form = AuthCodeForm(self)
        if not form.validate():
            self.render('bank/cgPassword2.html')
            return
        auth_code = form.auth_code.data
        if self.check_auth_code(auth_code):
            self.redirect('/bank/resetpasswd/modify')
            return
        self.render('bank/cgPassword2.html')

    def check_auth_code(self, auth_code):
        bk_id = self.current_user
        bk_sub_id = self.get_current_subuser()
        key = (str(bk_sub_id) if bk_sub_id else str(bk_id)) + ':AuthChangePass'
        # key = str(bk_id) + ':AuthChangePass'
        if self.rdb.get(key) == auth_code:
            return True
        return False


class BkResetPasswordAuthCodeHandler(BkAdminHandler):

    @asynchronous
    @coroutine
    @authenticated
    def get(self):
        msg = {'code': 406, 'msg': 'fail'}
        try:
            bk_id = self.current_user
            bk_sub_id = self.get_current_subuser()
            key = (str(bk_sub_id) if bk_sub_id else str(bk_id)) + ':AuthChangePass'
            # key = str(bk_id) + ':AuthChangePass'
            if self.rdb.get(key):
                auth_code = self.rdb.get(key)
            else:
                auth_code = str(random.randint(10000, 999999))
            # email = self.get_ub_user_email(bk_id)[0]
            email = self.get_ub_subuser_email(bk_sub_id)[0] if bk_sub_id else self.get_ub_user_email(bk_id)[0]
            # 给银行验证码是使用邮件  并非短信
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

    def get_ub_user_email(self, bk_id):
        return self.db.selectSQL("select email from bk_user where bk_id=%s and bk_type=1", (bk_id,))

    def get_ub_subuser_email(self, bk_sub_id):
        return self.db.selectSQL("select email from bk_subuser where bk_sub_id=%s", (bk_sub_id, ))


class BkResetPasswordModifyHandler(BkAdminHandler):

    @authenticated
    def get(self):
        self.render('bank/cgPassword3.html')

    def post(self):
        form = ModifyPasswordForm(self)
        new_pwd = form.newPwd.data
        check_pwd = form.checkPwd.data
        bk_id = self.current_user
        bk_sub_id = self.get_current_subuser()
        key = (str(bk_sub_id) if bk_sub_id else str(bk_id)) + ':AuthChangePass'
        # key = str(bk_id) + ':AuthChangePass'
        if not form.validate() and not (new_pwd == check_pwd):
            self.render('bank/cgPassword3.html', form=form)
            return

        self.update_user_passwd(new_pwd)
        self.rdb.delete(key)

        self.redirect('/bank/')

    def update_user_passwd(self, new_pwd):
        _password = bcrypt_pwd_new(str(new_pwd))
        bk_id = self.current_user
        bk_sub_id = self.get_current_subuser()
        update_at = datetime.datetime.now()
        if bk_sub_id:
            query = """update bk_subuser set password=%s,update_at=%s where bk_sub_id=%s"""
        else:
            query = """update bk_user set password=%s,update_at=%s where bk_id=%s"""
        self.db.executeSQL(query, (_password, update_at, bk_sub_id if bk_sub_id else bk_id))
