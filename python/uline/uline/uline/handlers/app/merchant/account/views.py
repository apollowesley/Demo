# -*- coding: utf-8 -*-
import hashlib
import json
import random
import datetime
from tornado import gen
from tornado.gen import coroutine, Return
from tornado.httpclient import AsyncHTTPClient
from tornado.web import authenticated, HTTPError, asynchronous
from uline.handlers.baseHandlers import MchAdminHandler
from .form import LoginForm, ChangePasswordForm, AuthCodeForm, ModifyPasswordForm, \
    ForgetPasswordForm, AuthTokenForm, AuthCodeTokenForm, ModifyPasswordTokenForm
from uline.public.common import bcrypt_pwd, bcrypt_pwd_new, timestamp_now
from uline.public import log
from uline.settings import MESSAGE_URL, env
from uline.public.permit import check_permission

import tcelery

tcelery.setup_nonblocking_producer()


class MchIndexHandler(MchAdminHandler):

    @authenticated
    @check_permission
    def get(self):
        self.render('merchant/account/index.html')


class MchLoginHandler(MchAdminHandler):
    '''
    status:
        1 未审核
        2 审核通过但未修改密码
        3 驳回
    '''

    def prepare(self):
        self.form = LoginForm(self)
        if self.request.method == 'POST':
            if not self.form.validate():
                self.render('merchant/account/login.html',
                            passwdMsg='账号或密码错误', form=self.form, status=1)

    def get(self):
        if self.get_current_user():
            self.redirect('/merchant/')
            return
        self.render('merchant/account/login.html',
                    passwdMsg='', form=self.form, status=1)

    @coroutine
    def post(self):
        mch_id = self.form.mch_id.data
        password = self.form.password.data

        login_auth_query = "select cs_id, dt_id from mch_inlet_info where mch_id=%s"
        login_auth = self.db.selectSQL(login_auth_query, (mch_id,))
        if login_auth and login_auth[0]:
            self.render('merchant/account/login.html',
                        passwdMsg=u'账号或密码错误', form=self.form, status=1)
            return

        if login_auth and login_auth[1]:
            # 这个渠道商希望除了100001544897以外，其他的商户都不能登录
            if str(login_auth[1]) == '10000072751' and str(mch_id) != '100001544897':
                self.render('merchant/account/login.html',
                            passwdMsg=u'未开通登录权限', form=self.form, status=1)
                return

        db_ret = yield self.auth_user(mch_id, password)
        if db_ret:
            self.session['codeid'] = db_ret[0]
            self.session['mch_name'] = db_ret[2]
            self.session.save()
            mobile = yield self.get_mch_user_mobile(mch_id)
            if mobile == password:
                self.render('merchant/account/login.html',
                            passwdMsg=u'', form=self.form, status=2)
            else:
                self.session['mch_id'] = db_ret[0]
                self.session['mch_name'] = db_ret[2]
                self.session.save()
                self.redirect('/merchant/')
        else:
            self.render('merchant/account/login.html',
                        passwdMsg=u'账号或密码错误', form=self.form, status=1)

    @coroutine
    def auth_user(self, mch_id, password):
        valid = False
        selSql = "select mch_id,password,mch_name from mch_user where mch_id=%s and status=2"
        db_ret = self.db.selectSQL(selSql, (mch_id,))
        if db_ret:
            valid = yield bcrypt_pwd(password, db_ret[1])
        raise Return(valid and db_ret)

    @coroutine
    def get_mch_user_mobile(self, mch_id):
        ret = self.db.selectSQL(
            "select mobile from mch_inlet_info where mch_id=%s", (mch_id,))
        raise gen.Return(ret[0])


class MchLogoutHandler(MchAdminHandler):

    @authenticated
    def get(self):
        self.session['mch_id'] = None
        self.session.save()
        self.redirect('/merchant/login')


class MchResetPasswordHandler(MchAdminHandler):

    @authenticated
    def prepare(self):
        self.form = ChangePasswordForm(self)
        self.mch_id = self.current_user

    def get(self):
        self.render('merchant/cgPassword.html')

    def post(self):
        p_mch_id = self.form.mch_id.data
        if p_mch_id == str(self.mch_id):
            self.redirect('/merchant/resetpasswd/auth')
        else:
            self.render('merchant/cgPassword.html')


class MchResetPasswordAuthHandler(MchAdminHandler):

    @authenticated
    def get(self):
        self.render('merchant/cgPassword2.html')

    def post(self):
        form = AuthCodeForm(self)
        if not form.validate():
            self.render('merchant/cgPassword2.html')
            return
        auth_code = form.auth_code.data
        if self.check_auth_code(auth_code):
            self.redirect('/merchant/resetpasswd/modify')
            return
        self.render('merchant/cgPassword2.html')

    def check_auth_code(self, auth_code):
        mch_id = self.get_current_user()
        key = str(mch_id) + ':AuthChangePass'
        if self.rdb.get(key) == auth_code:
            return True
        return False


class MchResetPasswordAuthCodeHandler(MchAdminHandler):

    @asynchronous
    @coroutine
    @authenticated
    def get(self):
        msg = {'code': 406, 'msg': 'fail'}
        try:
            mch_id = self.get_current_user()
            key = str(mch_id) + ':AuthChangePass'

            if self.rdb.get(key):
                auth_code = self.rdb.get(key)
            else:
                auth_code = str(random.randint(10000, 999999))

            mobile = self.get_mch_user_mobile(mch_id)[0]

            http_client = AsyncHTTPClient()
            data = {
                'env': env,
                'reciver': mobile,
                'body': u'您的验证码是{},一个小时后失效。'.format(auth_code)
            }
            url = MESSAGE_URL + '/v1/message'
            response = yield http_client.fetch(url, method='POST', body=json.dumps(data))

            if str(response.body) == '2' and self.rdb.set(key, auth_code, 60 * 60):
                msg = {'code': 200, 'msg': 'success', 'data': mobile}
            else:
                msg = {'code': 406, 'msg': 'fail'}
        except Exception as err:
            log.exception.info(err)
        self.write(msg)

    def get_mch_user_mobile(self, mch_id):
        return self.db.selectSQL("select mobile from mch_inlet_info where mch_id=%s", (mch_id,))


class MchResetPasswordModifyHandler(MchAdminHandler):

    @authenticated
    def get(self):
        self.render('merchant/cgPassword3.html')

    def post(self):
        form = ModifyPasswordForm(self)
        new_pwd = form.newPwd.data
        check_pwd = form.checkPwd.data
        mch_id = self.current_user
        key = str(mch_id) + ':AuthChangePass'
        if not form.validate() and not (new_pwd == check_pwd):
            self.render('merchant/cgPassword3.html', form=form)
            return

        self.update_user_passwd(new_pwd)
        self.rdb.delete(key)

        self.redirect('/merchant/')

    def update_user_passwd(self, new_pwd):
        _password = bcrypt_pwd_new(str(new_pwd))
        mch_id = self.current_user
        update_at = timestamp_now()
        query = """update mch_user set password=%s,update_at=%s where mch_id=%s"""
        self.db.executeSQL(query, (_password, update_at, mch_id))


class MchFirstLoginGetAuthCodeHandler(MchAdminHandler):

    @asynchronous
    @coroutine
    def get(self):
        msg = {'code': 406, 'msg': 'fail'}
        try:
            codeid = self.session.get('codeid')
            key = str(codeid) + ':AuthChangePass'
            if self.rdb.get(key):
                auth_code = self.rdb.get(key)
            else:
                auth_code = str(random.randint(10000, 999999))
            mobile = self.get_mch_user_email()[0]

            http_client = AsyncHTTPClient()
            data = {
                'env': env,
                'reciver': mobile,
                'body': u'您的验证码是{},一个小时后失效。'.format(auth_code)
            }
            url = MESSAGE_URL + '/v1/message'
            response = yield http_client.fetch(url, method='POST', body=json.dumps(data))

            if str(response.body) == '2' and self.rdb.set(key, auth_code, 60 * 60):
                msg = {'code': 200, 'msg': 'success', 'data': mobile}
            else:
                msg = {'code': 406, 'msg': 'fail'}
        except Exception as err:
            log.exception.info(err)
        self.write(msg)

    def get_mch_user_email(self):
        return self.db.selectSQL("select mobile from mch_inlet_info where mch_id=%s", (self.session.get('codeid'),))


class MchFirstLoginAuthCodeCodeHandler(MchAdminHandler):

    def get(self):
        form = AuthCodeForm(self)
        if not form.validate():
            self.write({'code': 406, 'msg': '参数错误'})
        auth_code = form.auth_code.data
        if self.check_auth_code(auth_code):
            self.write({'code': 200, 'msg': 'success'})
        else:
            self.write({'code': 406, 'msg': '参数错误'})
        self.finish()

    def check_auth_code(self, auth_code):
        codeid = self.session.get('codeid')
        key = str(codeid) + ':AuthChangePass'
        if self.rdb.get(key) == auth_code:
            return True
        return False


class MchFirstLoginModifyHandler(MchAdminHandler):

    def get(self):
        form = ModifyPasswordForm(self)
        new_pwd = form.newPwd.data
        check_pwd = form.checkPwd.data
        codeid = self.session.get('codeid')
        key = str(codeid) + ':AuthChangePass'
        if not form.validate() or (not (new_pwd == check_pwd)):
            self.write({'code': 406, 'msg': '参数错误'})
            self.finish()
            return

        self.update_user_passwd(new_pwd)
        self.rdb.delete(key)

        self.write({'code': 200, 'msg': 'ok'})
        self.finish()

    def update_user_passwd(self, new_pwd):
        _password = bcrypt_pwd_new(str(new_pwd))
        update_at = datetime.datetime.now()
        query = """update mch_user set password=%s,update_at=%s where mch_id=%s"""
        self.db.executeSQL(query, (_password, update_at,
                                   self.session.get('codeid')))


class MchForgetPasswordHandler(MchAdminHandler):

    def prepare(self):
        self.form = ForgetPasswordForm(self)

    def get(self):
        self.render('merchant/fgPassword.html')

    @gen.coroutine
    def post(self):
        if not self.form.validate():
            error_form_html = self.render_string(
                'common/error_form.html', data=self.form)
            self.render('merchant/fgPassword.html',
                        error_form_html=error_form_html)
            return
        mch_id = self.form.mch_id.data
        token = hashlib.sha1(str(mch_id)).hexdigest()
        self.rdb.set(token, mch_id, 60 * 5)
        self.redirect('/merchant/forgetpwd/auth?token={}'.format(token))


class MchForgetPasswordAuthHandler(MchAdminHandler):

    def get(self):
        self.form = AuthTokenForm(self)
        token = self.form.token.data
        if not self.form.validate() and not self.rdb.get(token):
            self.redirect('/merchant/forgetpwd')
            return
        self.render('merchant/fgPassword2.html', token=token)

    def post(self):
        form = AuthCodeTokenForm(self)
        token = form.token.data
        mch_id = self.rdb.get(token)
        auth_code = form.auth_code.data

        if not form.validate() and not mch_id:
            self.render('merchant/fgPassword.html')
            return
        if self.check_auth_code(mch_id, auth_code):
            self.redirect('/merchant/forgetpwd/modify?token={}'.format(token))
            return
        self.render('merchant/fgPassword.html')

    def check_auth_code(self, mch_id, auth_code):
        key = str(mch_id) + ':AuthForgetPass'
        if self.rdb.get(key) == auth_code:
            return True
        return False


class MchForgetPasswordAuthCodeHandler(MchAdminHandler):

    @asynchronous
    @coroutine
    def get(self):
        msg = {'code': 406, 'msg': 'fail'}
        form = AuthTokenForm(self)
        token = form.token.data
        mch_id = self.rdb.get(token)
        if not form.validate() and not mch_id:
            self.write(msg)
        else:
            try:
                key = str(mch_id) + ':AuthForgetPass'
                if self.rdb.get(key):
                    auth_code = self.rdb.get(key)
                else:
                    auth_code = str(random.randint(10000, 999999))
                mobile = self.get_mch_user_mobile(mch_id)[0]

                http_client = AsyncHTTPClient()
                data = {
                    'env': env,
                    'reciver': mobile,
                    'body': u'您的验证码是{},一个小时后失效。'.format(auth_code)
                }
                url = MESSAGE_URL + '/v1/message'
                response = yield http_client.fetch(url, method='POST', body=json.dumps(data))

                if str(response.body) == '2' and self.rdb.set(key, auth_code, 60 * 60):
                    msg = {'code': 200, 'msg': 'success', 'data': mobile}
                else:
                    msg = {'code': 406, 'msg': 'fail'}
            except Exception as err:
                log.exception.info(err)
            self.write(msg)

    def get_mch_user_mobile(self, mch_id):
        return self.db.selectSQL("select mobile from mch_inlet_info where mch_id=%s", (mch_id,))


class MchForgetPasswordModifyHandler(MchAdminHandler):

    def get(self):
        self.form = AuthTokenForm(self)
        token = self.form.token.data
        if not self.form.validate() and not self.rdb.get(token):
            self.redirect('/merchant/forgetpwd')
            return
        self.render('merchant/fgPassword3.html', token=token)
        return

    def post(self):
        form = ModifyPasswordTokenForm(self)
        new_pwd = form.newPwd.data
        check_pwd = form.checkPwd.data
        token = form.token.data
        mch_id = self.rdb.get(token)
        if not mch_id:
            self.redirect('/merchant/forgetpwd')
            return
        if not form.validate() and not (new_pwd == check_pwd):
            self.render('merchant/fgPassword3.html', form=form)
            return

        key = str(mch_id) + ':AuthForgetPass'
        self.update_user_passwd(new_pwd, mch_id)
        self.rdb.delete(key)

        self.redirect('/merchant/')

    def update_user_passwd(self, new_pwd, mch_id):
        _password = bcrypt_pwd_new(str(new_pwd))
        update_at = datetime.datetime.now()
        query = """update mch_user set password=%s,update_at=%s where mch_id=%s"""
        self.db.executeSQL(query, (_password, update_at, mch_id))
