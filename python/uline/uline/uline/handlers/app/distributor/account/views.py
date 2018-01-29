# -*- coding: utf-8 -*-
import hashlib
import datetime
import json
import random
from tornado import gen
from tornado.gen import coroutine, Return
from tornado.httpclient import AsyncHTTPClient
from tornado.web import authenticated, HTTPError, asynchronous

from uline.settings import MESSAGE_URL, env
from uline.handlers.baseHandlers import DtAdminHandler
from uline.public.baseDB import DbClient
from .form import (
    LoginForm, ChangePasswordForm,
    AuthCodeForm, ModifyPasswordForm, AuthTokenForm,
    AuthCodeTokenForm, ModifyPasswordTokenForm
)
from uline.public.common import bcrypt_pwd, bcrypt_pwd_new
from uline.public import log
from uline.public.permit import check_permission

import tcelery

tcelery.setup_nonblocking_producer()


class DtIndexHandler(DtAdminHandler):

    @authenticated
    @check_permission
    def get(self):
        self.render('distributor/account/index.html')


class DtLoginHandler(DtAdminHandler):
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
                self.redirect('/dist/login')
            else:
                self.dbClient = DbClient()
                self.rdsClient = self.application.client

    def get(self):
        if self.get_current_user():
            self.redirect('/dist/')
            return
        self.render(
            'distributor/account/login.html',
            passwdMsg='', form=self.form, status=1
        )

    @coroutine
    def post(self):
        email = self.form.email.data
        password = self.form.password.data

        db_ret = yield self.auth_user(email, password)
        if db_ret:
            dt_id = db_ret[0]
            self.session['dt_codeid'] = dt_id
            self.session['dt_name'] = db_ret[2]
            self.session.save()
            # self.session['dt_id'] = dt_id
            # self.session['dt_name'] = db_ret[2]
            # self.session.save()
            mobile = yield self.get_dt_user_mobile(dt_id)
            if mobile == password:
                self.render(
                    'distributor/account/login.html',
                    passwdMsg='', form=self.form, status=2
                )
            else:
                self.session['dt_id'] = dt_id
                self.session['dt_name'] = db_ret[2]
                self.session.save()
                self.redirect('/dist/')
        # else:
        #     # dt_user 中找不到记录
        #     db_ret = yield self.auth_subuser(email, password)
        #     if db_ret:
        #         self.session['dt_subcodeid'] = db_ret[0]
        #         # self.session['dt_id'] = db_ret[3]
        #         # self.session['dt_name'] = self.get_dt_user_name(str(db_ret[3]))[0]
        #         # self.session['dt_sub_id'] = db_ret[0]
        #         # self.session['dt_sub_name'] = db_ret[2]
        #         # self.session.save()
        #         mobile = yield self.get_dt_user_mobile(db_ret[3])
        #         if mobile == password:
        #             self.render(
        #                 'distributor/account/login.html',
        #                 passwdMsg='', form=self.form, status=2
        #             )
        #         else:
        #             self.session['dt_id'] = db_ret[3]
        #             self.session['dt_name'] = self.get_dt_user_name(str(db_ret[3]))[0]
        #             self.session['dt_sub_id'] = db_ret[0]
        #             self.session['dt_sub_name'] = db_ret[2]
        #             self.session.save()
        #             self.redirect('/dist/')
        else:
            self.render(
                'distributor/account/login.html',
                passwdMsg=u'账号或密码错误',
                form=self.form, status=1
            )

    @coroutine
    def auth_user(self, email, password):
        valid = False
        selSql = """select dt_user.dt_id,dt_user.password,dt_user.dt_name
                    from dt_user
                    inner join dt_inlet_info on  dt_inlet_info.dt_id = dt_user.dt_id
                    where dt_user.email=%s and dt_user.status=2
                    and dt_inlet_info.parent_id is null;"""
        db_ret = self.dbClient.selectSQL(selSql, (email,))
        if db_ret:
            valid = yield bcrypt_pwd(password, db_ret[1])
        raise Return(valid and db_ret)

    @coroutine
    def auth_subuser(self, email, password):
        valid = False
        selSql = "select dt_sub_id,password,dt_sub_name,dt_user_dt_id from dt_subuser where email=%s"
        db_ret = self.dbClient.selectSQL(selSql, (email,))
        if db_ret:
            valid = yield bcrypt_pwd(password, db_ret[1])
        raise Return(valid and db_ret)

    @coroutine
    def get_dt_user_mobile(self, dt_id):
        ret = self.db.selectSQL(
            "select mobile from dt_inlet_info where dt_id=%s", (dt_id,))
        raise gen.Return(ret[0])


class DtLogoutHandler(DtAdminHandler):

    @authenticated
    def get(self):
        self.session['dt_id'] = None
        self.session['dt_sub_id'] = None
        self.session.save()
        self.redirect('/dist/login')


class DtResetPasswordHandler(DtAdminHandler):

    @authenticated
    def prepare(self):
        self.form = ChangePasswordForm(self)

    def get(self):
        self.render('distributor/cgPassword.html')

    def post(self):
        email = self.form.email.data
        dt_id = self.current_user
        dt_sub_id = self.get_current_subuser()
        if dt_sub_id:
            if self.auth_subuser_email(email, dt_sub_id):
                self.redirect('/dist/resetpasswd/auth')
                return
        else:
            if self.auth_email(email, dt_id):
                self.redirect('/dist/resetpasswd/auth')
                return
        self.render('distributor/cgPassword.html')

    def auth_email(self, email, dt_id):
        return self.db.selectSQL(
            "select 1 from dt_user where email=%s and status=2 and dt_id=%s",
            (email, dt_id)
        )

    def auth_subuser_email(self, email, dt_sub_id):
        return self.db.selectSQL("select 1 from dt_subuser where email=%s and dt_sub_id=%s", (email, dt_sub_id))


class DtResetPasswordAuthHandler(DtAdminHandler):

    @authenticated
    def get(self):
        self.render('distributor/cgPassword2.html')

    def post(self):
        form = AuthCodeForm(self)
        if not form.validate():
            self.render('distributor/cgPassword2.html')
            return
        auth_code = form.auth_code.data
        if self.check_auth_code(auth_code):
            self.redirect('/dist/resetpasswd/modify')
            return
        self.render('distributor/cgPassword2.html')

    def check_auth_code(self, auth_code):
        dt_id = self.current_user
        dt_sub_id = self.get_current_subuser()
        key = (str(dt_sub_id) if dt_sub_id else str(dt_id)) + ':AuthChangePass'
        # key = str(dt_id) + ':AuthChangePass'
        if self.rdb.get(key) == auth_code:
            return True
        return False


class DtResetPasswordAuthCodeHandler(DtAdminHandler):

    @asynchronous
    @coroutine
    @authenticated
    def get(self):
        msg = {'code': 406, 'msg': 'fail'}
        try:
            dt_id = self.current_user
            dt_sub_id = self.get_current_subuser()
            key = (str(dt_sub_id) if dt_sub_id else str(dt_id)) + \
                ':AuthChangePass'
            # key = str(dt_id) + ':AuthChangePass'
            if self.rdb.get(key):
                auth_code = self.rdb.get(key)
            else:
                auth_code = str(random.randint(10000, 999999))
            mobile = self.get_dt_sub_user_email(
                dt_sub_id)[0] if dt_sub_id else self.get_dt_user_mobile(dt_id)[0]
            http_client = AsyncHTTPClient()
            # 若是子帐号修改密码，验证邮箱。
            if dt_sub_id:
                data = {
                    'env': env,
                    'reciver': mobile,
                    'title': u'uline验证码',
                    'body': u'您的验证码是{},一个小时后失效。'.format(auth_code)
                }
                url = MESSAGE_URL + '/v1/email'
            else:
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

    def get_dt_user_mobile(self, dt_id):
        return self.db.selectSQL(
            "select mobile from dt_inlet_info where dt_id=%s", (dt_id,))

    def get_dt_sub_user_email(self, dt_sub_id):
        return self.db.selectSQL(
            "select email from dt_subuser where dt_sub_id=%s", (dt_sub_id, ))


class DtResetPasswordModifyHandler(DtAdminHandler):

    @authenticated
    def get(self):
        self.render('distributor/cgPassword3.html')

    def post(self):
        form = ModifyPasswordForm(self)
        new_pwd = form.newPwd.data
        check_pwd = form.checkPwd.data
        dt_id = self.current_user
        dt_sub_id = self.get_current_subuser()
        key = (str(dt_sub_id) if dt_sub_id else str(dt_id)) + ':AuthChangePass'
        #key = str(dt_id) + ':AuthChangePass'
        if not form.validate() and not (new_pwd == check_pwd):
            self.render('distributor/cgPassword3.html', form=form)
            return

        self.update_user_passwd(new_pwd)
        self.rdb.delete(key)

        self.redirect('/dist/')

    def update_user_passwd(self, new_pwd):
        _password = bcrypt_pwd_new(str(new_pwd))
        dt_id = self.current_user
        dt_sub_id = self.get_current_subuser()
        update_at = datetime.datetime.now()
        if dt_sub_id:
            query = """update dt_subuser set password=%s,
                        update_at=%s where dt_sub_id=%s"""
        else:
            query = """update dt_user set password=%s,
                        update_at=%s where dt_id=%s"""
        self.db.executeSQL(query, (_password, update_at,
                                   dt_sub_id if dt_sub_id else dt_id))
        # self.db.executeSQL(query, (_password, update_at, dt_id))


class DtFirstLoginGetAuthCodeHandler(DtAdminHandler):

    @asynchronous
    @coroutine
    # @authenticated
    def get(self):
        msg = {'code': 406, 'msg': 'fail'}
        try:
            dt_id = self.session.get('dt_codeid')
            key = str(dt_id) + ':AuthChangePass'
            if self.rdb.get(key):
                auth_code = self.rdb.get(key)
            else:
                auth_code = str(random.randint(10000, 999999))
            mobile = self.get_dt_user_email(dt_id)[0]

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

    def get_dt_user_email(self, dt_id):
        return self.db.selectSQL(
            "select mobile from dt_inlet_info where dt_id=%s", (dt_id,))


class DtFirstLoginAuthCodeCodeHandler(DtAdminHandler):

    # @authenticated
    def get(self):
        form = AuthCodeForm(self)
        if not form.validate():
            self.write({'code': 406, 'msg': '参数错误'})
        auth_code = form.auth_code.data
        if self.check_auth_code(auth_code):
            self.write({'code': 200, 'msg': 'success'})
        self.finish()

    def check_auth_code(self, auth_code):
        dt_id = self.session.get('dt_codeid')
        key = str(dt_id) + ':AuthChangePass'
        if self.rdb.get(key) == auth_code:
            return True
        return False


class DtFirstLoginModifyHandler(DtAdminHandler):

    # @authenticated
    def get(self):
        form = ModifyPasswordForm(self)
        new_pwd = form.newPwd.data
        check_pwd = form.checkPwd.data
        key = str(self.session.get('dt_codeid')) + ':AuthChangePass'
        if not form.validate() or (not (new_pwd == check_pwd)):
            self.write({'code': 406, 'msg': '参数错误'})
        else:
            self.update_user_passwd(new_pwd)
            self.rdb.delete(key)
            self.session['dt_id'] = self.session.get('dt_codeid')
            self.session.save()
            self.write({'code': 200, 'msg': 'ok'})
            self.finish()
        return

    def update_user_passwd(self, new_pwd):
        _password = bcrypt_pwd_new(str(new_pwd))
        update_at = datetime.datetime.now()
        query = """update dt_user set password=%s,
        update_at=%s where dt_id=%s"""
        self.db.executeSQL(query, (_password, update_at,
                                   self.session.get('dt_codeid')))


class DtForgetPasswordHandler(DtAdminHandler):

    def prepare(self):
        self.form = ChangePasswordForm(self)

    def get(self):
        self.render('distributor/fgPassword.html')

    @gen.coroutine
    def post(self):
        if not self.form.validate():
            error_form_html = self.render_string(
                'common/error_form.html', data=self.form)
            self.render('distributor/fgPassword.html',
                        error_form_html=error_form_html)
            return

        email = self.form.email.data
        with self.db.get_db() as cur:
            dt_id = yield self.get_dt_id(cur, email)

        if dt_id:
            token = hashlib.sha1(str(dt_id)).hexdigest()
            self.rdb.set(token, dt_id, 60 * 5)
            self.redirect('/dist/forgetpwd/auth?token={}'.format(token))
        else:
            self.render('distributor/fgPassword.html')

    @gen.coroutine
    def get_dt_id(self, cursor, email):
        query = """select dt_user.dt_id
                from dt_user
                inner join dt_inlet_info on dt_inlet_info.dt_id = dt_user.dt_id
                where dt_inlet_info.parent_id is NULL
                and dt_user.email=%s and dt_user.status=2;"""
        cursor.execute(query, (email,))
        ret = cursor.fetchone()
        if ret:
            ret = ret[0]
        raise gen.Return(ret)


class DtForgetPasswordAuthHandler(DtAdminHandler):

    def get(self):
        self.form = AuthTokenForm(self)
        token = self.form.token.data
        if not self.form.validate() and not self.rdb.get(token):
            self.redirect('/dist/forgetpwd')
            return
        self.render('distributor/fgPassword2.html', token=token)

    def post(self):
        form = AuthCodeTokenForm(self)
        token = form.token.data
        dt_id = self.rdb.get(token)
        auth_code = form.auth_code.data

        if not form.validate() and not dt_id:
            self.render('distributor/fgPassword.html')
            return

        if self.check_auth_code(dt_id, auth_code):
            self.redirect('/dist/forgetpwd/modify?token={}'.format(token))
            return
        self.render('distributor/fgPassword.html')

    def check_auth_code(self, dt_id, auth_code):
        key = str(dt_id) + ':AuthForgetPass'
        if self.rdb.get(key) == auth_code:
            return True
        return False


class DtForgetPasswordAuthCodeHandler(DtAdminHandler):

    @asynchronous
    @coroutine
    def get(self):
        msg = {'code': 406, 'msg': 'fail'}
        form = AuthTokenForm(self)
        token = form.token.data
        dt_id = self.rdb.get(token)
        if not form.validate() and not dt_id:
            self.write(msg)
        else:
            try:
                key = str(dt_id) + ':AuthForgetPass'
                if self.rdb.get(key):
                    auth_code = self.rdb.get(key)
                else:
                    auth_code = str(random.randint(10000, 999999))
                mobile = self.get_dt_user_email(dt_id)[0]

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

    def get_dt_user_email(self, dt_id):
        return self.db.selectSQL(
            "select mobile from dt_inlet_info where dt_id=%s", (dt_id,))


class DtForgetPasswordModifyHandler(DtAdminHandler):

    def get(self):
        self.form = AuthTokenForm(self)
        token = self.form.token.data
        if not self.form.validate() and not self.rdb.get(token):
            self.redirect('/dist/forgetpwd')
            return
        self.render('distributor/fgPassword3.html', token=token)

    def post(self):
        form = ModifyPasswordTokenForm(self)
        new_pwd = form.newPwd.data
        check_pwd = form.checkPwd.data
        token = form.token.data
        dt_id = self.rdb.get(token)
        if not dt_id:
            self.redirect('/dist/forgetpwd')
            return
        if not form.validate() and not (new_pwd == check_pwd):
            self.render('distributor/fgPassword3.html', form=form)

        key = str(dt_id) + ':AuthForgetPass'
        self.update_user_passwd(new_pwd, dt_id)
        self.rdb.delete(key)

        self.redirect('/dist/')

    def update_user_passwd(self, new_pwd, dt_id):
        _password = bcrypt_pwd_new(str(new_pwd))
        update_at = datetime.datetime.now()
        query = """update dt_user set password=%s,
        update_at=%s where dt_id=%s"""
        self.db.executeSQL(query, (_password, update_at, dt_id))
