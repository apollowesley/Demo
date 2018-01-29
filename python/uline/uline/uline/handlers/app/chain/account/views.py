# -*- coding: utf-8 -*-
import re
import hashlib
import datetime
import json
import random
from tornado import gen
from tornado.gen import coroutine, Return
from tornado.httpclient import AsyncHTTPClient
from tornado.web import authenticated, HTTPError, asynchronous

from uline.settings import MESSAGE_URL, env
from uline.handlers.baseHandlers import ChainAdminHandler
from uline.public.baseDB import DbClient
from .form import (
    LoginForm, ForgetPasswordForm, ChangePasswordForm,
    AuthCodeForm, ModifyPasswordForm, AuthTokenForm,
    AuthCodeTokenForm, ModifyPasswordTokenForm
)
from uline.public.common import bcrypt_pwd, bcrypt_pwd_new
from uline.public import log
from uline.public.permit import check_permission


import tcelery

tcelery.setup_nonblocking_producer()


class ChainIndexHandler(ChainAdminHandler):

    @authenticated
    @check_permission
    def get(self):
        self.render('chain/account/index.html')


class ChainLoginHandler(ChainAdminHandler):
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
                self.redirect('/chain/login')
            else:
                self.dbClient = DbClient()
                self.rdsClient = self.application.client

    def get(self):
        if self.get_current_user():
            self.redirect('/chain/')
            return
        self.render(
            'chain/account/login.html',
            passwdMsg='', form=self.form, status=1
        )

    @coroutine
    def post(self):
        chain_id = self.form.chain_id.data
        password = self.form.password.data
        if re.match(r'\d+$', chain_id):
            db_ret = yield self.auth_user(chain_id, password)
        else:
            db_ret = False
        if db_ret:
            chain_id = db_ret[0]
            self.session['chain_codeid'] = chain_id
            self.session['chain_name'] = db_ret[2]
            self.session.save()
            mobile = yield self.get_chain_user_mobile(chain_id)
            if mobile == password:
                self.render(
                    'chain/account/login.html',
                    passwdMsg='', form=self.form, status=2
                )
            else:
                self.session['chain_id'] = chain_id
                self.session['chain_name'] = db_ret[2]
                # 用来区分当前用户是一个渠道商还是连锁商户
                self.session['user_type'] = "chain"
                self.session.save()
                self.redirect('/chain/')
        else:
            self.render(
                'chain/account/login.html',
                passwdMsg=u'账号或密码错误',
                form=self.form, status=1
            )

    @coroutine
    def auth_user(self, chain_id, password):
        valid = False
        selSql = """select du.dt_id,du.password,du.dt_name from dt_user as du
                  inner join dt_inlet_info as dii on dii.dt_id = du.dt_id
                  where du.dt_id=%s and du.status=2 and dii.parent_id is not null"""
        db_ret = self.dbClient.selectSQL(selSql, (chain_id,))
        if db_ret:
            valid = yield bcrypt_pwd(password, db_ret[1])
        raise Return(valid and db_ret)

    # @coroutine
    # def auth_subuser(self, email, password):
    #     valid = False
    #     selSql = "select dt_sub_id,password,dt_sub_name,dt_user_dt_id from dt_subuser where email=%s"
    #     db_ret = self.dbClient.selectSQL(selSql, (email,))
    #     if db_ret:
    #         valid = yield bcrypt_pwd(password, db_ret[1])
    #     raise Return(valid and db_ret)

    @coroutine
    def get_chain_user_mobile(self, chain_id):
        ret = self.db.selectSQL(
            "select mobile from dt_inlet_info where dt_id=%s and parent_id is not null", (chain_id,))
        raise gen.Return(ret[0])


class ChainLogoutHandler(ChainAdminHandler):

    @authenticated
    def get(self):
        self.session['chain_id'] = None
        self.session['chain_sub_id'] = None
        self.session['user_type'] = None
        self.session.save()
        self.redirect('/chain/login')


class ChainResetPasswordHandler(ChainAdminHandler):
    @authenticated
    def prepare(self):
        self.form = ChangePasswordForm(self)
        self.chain_id = self.current_user

    def get(self):
        self.render('chain/cgPassword.html')

    def post(self):
        p_chain_id = self.form.chain_id.data
        if p_chain_id == str(self.chain_id):
            self.redirect('/chain/resetpasswd/auth')
        else:
            self.render('chain/cgPassword.html')


class ChainResetPasswordAuthHandler(ChainAdminHandler):

    @authenticated
    def get(self):
        self.render('chain/cgPassword2.html')

    def post(self):
        form = AuthCodeForm(self)
        if not form.validate():
            self.render('chain/cgPassword2.html')
            return
        auth_code = form.auth_code.data
        if self.check_auth_code(auth_code):
            self.redirect('/chain/resetpasswd/modify')
            return
        self.render('chain/cgPassword2.html')

    def check_auth_code(self, auth_code):
        chain = self.get_current_user()
        key = str(chain) + ':AuthChangePass'
        if self.rdb.get(key) == auth_code:
            return True
        return False

    @authenticated
    def get(self):
        self.render('chain/cgPassword2.html')


class ChainResetPasswordAuthCodeHandler(ChainAdminHandler):

    @asynchronous
    @coroutine
    @authenticated
    def get(self):
        msg = {'code': 406, 'msg': 'fail'}
        try:
            chain_id = self.get_current_user()
            key = str(chain_id) + ':AuthChangePass'

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


class ChainResetPasswordModifyHandler(ChainAdminHandler):
    @authenticated
    def get(self):
        self.render('chain/cgPassword3.html')

    def post(self):
        form = ModifyPasswordForm(self)
        new_pwd = form.newPwd.data
        check_pwd = form.checkPwd.data
        chain_id = self.current_user
        key = str(chain_id) + ':AuthChangePass'
        if not form.validate() and not (new_pwd == check_pwd):
            self.render('chain/cgPassword3.html', form=form)
            return

        self.update_user_passwd(new_pwd)
        self.rdb.delete(key)

        self.redirect('/chain/')

    def update_user_passwd(self, new_pwd):
        _password = bcrypt_pwd_new(str(new_pwd))
        mch_id = self.current_user
        update_at = datetime.datetime.now()
        query = """
            update dt_user set password=%s, update_at=%s where dt_id=%s
        """
        self.db.executeSQL(query, (_password, update_at, mch_id))


class ChainFirstLoginGetAuthCodeHandler(ChainAdminHandler):

    @asynchronous
    @coroutine
    # @authenticated
    def get(self):
        msg = {'code': 406, 'msg': 'fail'}
        try:
            chain_id = self.session.get('chain_codeid')
            key = str(chain_id) + ':AuthChangePass'
            if self.rdb.get(key):
                auth_code = self.rdb.get(key)
            else:
                auth_code = str(random.randint(10000, 999999))
            mobile = self.get_chain_user_email(chain_id)[0]

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

    def get_chain_user_email(self, chain_id):
        return self.db.selectSQL(
            "select mobile from dt_inlet_info where dt_id=%s", (chain_id,))


class ChainFirstLoginAuthCodeCodeHandler(ChainAdminHandler):

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
        chain_id = self.session.get('chain_codeid')
        key = str(chain_id) + ':AuthChangePass'
        if self.rdb.get(key) == auth_code:
            return True
        return False


class ChainFirstLoginModifyHandler(ChainAdminHandler):

    def get(self):
        form = ModifyPasswordForm(self)
        new_pwd = form.newPwd.data
        check_pwd = form.checkPwd.data
        key = str(self.session.get('chain_codeid')) + ':AuthChangePass'
        if not form.validate() or (not (new_pwd == check_pwd)):
            self.write({'code': 406, 'msg': '参数错误'})
        else:
            edit_status = self.update_user_passwd(new_pwd)
            if edit_status:
                self.rdb.delete(key)
                self.session['chain_id'] = None
                self.session['chain_sub_id'] = None
                self.session['user_type'] = None
                self.session.save()
                self.write({'code': 200, 'msg': 'ok'})
                self.finish()
                return
            else:
                self.write({'code': 406, 'msg': '无效的连锁商户编号'})
                return
        return

    def update_user_passwd(self, new_pwd):
        _password = bcrypt_pwd_new(str(new_pwd))
        update_at = datetime.datetime.now()
        chain_id = self.session.get('chain_codeid')
        ret = self.db.selectSQL("""
            select 1 from dt_inlet_info where dt_id=%s
            and parent_id is not null
        """, (chain_id, ))
        if ret:
            query = """update dt_user set password=%s, update_at=%s
                        where dt_id=%s"""
            self.db.executeSQL(query, (_password, update_at, chain_id))
            return True
        else:
            return False


class ChainForgetPasswordHandler(ChainAdminHandler):

    def prepare(self):
        self.form = ForgetPasswordForm(self)

    def get(self):
        self.render('chain/fgPassword.html')

    @gen.coroutine
    def post(self):
        if not self.form.validate():
            error_form_html = self.render_string(
                'common/error_form.html', data=self.form)
            self.render('chain/fgPassword.html', error_form_html=error_form_html)
            return
        chain_id = self.form.chain_id.data
        token = hashlib.sha1(str(chain_id)).hexdigest()
        self.rdb.set(token, chain_id, 60 * 5)
        self.redirect('/chain/forgetpwd/auth?token={}'.format(token))


class ChainForgetPasswordAuthHandler(ChainAdminHandler):

    def get(self):
        self.form = AuthTokenForm(self)
        token = self.form.token.data
        if not self.form.validate() and not self.rdb.get(token):
            self.redirect('/chain/forgetpwd')
            return
        self.render('chain/fgPassword2.html', token=token)

    def post(self):
        form = AuthCodeTokenForm(self)
        token = form.token.data
        chain_id = self.rdb.get(token)
        auth_code = form.auth_code.data

        if not form.validate() and not chain_id:
            self.render('chain/fgPassword.html')
            return

        if self.check_auth_code(chain_id, auth_code):
            self.redirect('/chain/forgetpwd/modify?token={}'.format(token))
            return
        self.render('chain/fgPassword.html')

    def check_auth_code(self, chain_id, auth_code):
        key = str(chain_id) + ':AuthForgetPass'
        if self.rdb.get(key) == auth_code:
            return True
        return False


class ChainForgetPasswordAuthCodeHandler(ChainAdminHandler):

    @asynchronous
    @coroutine
    def get(self):
        msg = {'code': 406, 'msg': 'fail'}
        form = AuthTokenForm(self)
        token = form.token.data
        chain_id = self.rdb.get(token)
        if not form.validate() and not chain_id:
            self.write(msg)
        else:
            try:
                key = str(chain_id) + ':AuthForgetPass'
                if self.rdb.get(key):
                    auth_code = self.rdb.get(key)
                else:
                    auth_code = str(random.randint(10000, 999999))
                mobile = self.get_chain_user_email(chain_id)[0]

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

    def get_chain_user_email(self, chain_id):
        return self.db.selectSQL(
            "select mobile from dt_inlet_info where dt_id=%s and parent_id is not null", (
                chain_id,)
        )


class ChainForgetPasswordModifyHandler(ChainAdminHandler):

    def get(self):
        self.form = AuthTokenForm(self)
        token = self.form.token.data
        if not self.form.validate() and not self.rdb.get(token):
            self.redirect('/chain/forgetpwd')
            return
        self.render('chain/fgPassword3.html', token=token)

    def post(self):
        form = ModifyPasswordTokenForm(self)
        new_pwd = form.newPwd.data
        check_pwd = form.checkPwd.data
        token = form.token.data
        chain_id = self.rdb.get(token)
        if not chain_id:
            self.redirect('/chain/forgetpwd')
            return
        if not form.validate() and not (new_pwd == check_pwd):
            self.render('chain/fgPassword3.html', form=form)
            return

        key = str(chain_id) + ':AuthForgetPass'
        self.update_user_passwd(new_pwd, chain_id)
        self.rdb.delete(key)

        self.redirect('/chain/')

    def update_user_passwd(self, new_pwd, chain_id):
        _password = bcrypt_pwd_new(str(new_pwd))
        update_at = datetime.datetime.now()
        query = """
            update dt_user set password=%s, update_at=%s where dt_id = %s;
        """
        self.db.executeSQL(query, (_password, update_at, chain_id))
