# -*- coding: utf-8 -*-
import datetime
from tornado.gen import coroutine, Return
from tornado.web import authenticated, asynchronous
from uline.handlers.baseHandlers import CommanHandler
from .form import LoginForm, AuthCodeForm, ModifyPasswordForm, ForgetPasswordForm, AuthTokenForm, \
    AuthCodeTokenForm, ModifyPasswordTokenForm, changelogin
from uline.public import log
from uline.model.uline.user import Employee, UnionEmployee
from uline.model.uline.other import SysType
from uline.model.uline.info import UserProfile, MchInletInfo
from uline.model.uline.permit import Role, EmployeeRolePermit
from uline.model.uline.base import uline_session
import tcelery
from uline.public.common import bcrypt_pwd


tcelery.setup_nonblocking_producer()
INDEX_URL = {"mr": '/chain/',
             "mch": '/merchant/',
             "ub": '/official/',
             "bk": '/bank/',
             "ibk": '/inter_bank/',
             "dt": "/dist/"
             }


class IndexHandler(CommanHandler):
    def get(self):
        self.render('common/login.html')


class NoRoleWebpage(CommanHandler):
    def get(self):
        p = self.get_argument("p", "")
        is_role = self.get_secure_cookie("r_ticket")
        if is_role in (None, "0"):
            self.set_secure_cookie("r_ticket", "1")
            self.render('common/no_role_webpage.html', p=p)
            return

        self.set_secure_cookie("r_ticket", "0")
        self.redirect("/account/")


class LoginHandler(CommanHandler):
    def prepare(self):

        if self.session.session_id:
            self.session.clear_session()

        self.form = LoginForm(self)
        if not self.form.validate():
            self.write(dict(msg='请填写账号或密码', code=406))
            return

    @coroutine
    def post(self):

        self.login_name = self.form.login_name.data
        self.password = self.form.password.data
        self.right_user = uline_session.query(Employee).filter(Employee.login_name == self.login_name).first()

        # 验证账号密码及特殊情况
        auth_login_name_msg = yield self.auth_user()
        if auth_login_name_msg:
            self.write(dict(code=406, msg=auth_login_name_msg))
            return

        # 获取账号平台类型
        self.sys_type = uline_session.query(SysType).filter(SysType.id == self.right_user.sys_type_id).one()

        # 验证用户角色
        self.user_role = uline_session.query(Role).join(EmployeeRolePermit,
                                                        EmployeeRolePermit.role_id == Role.id).filter(
            EmployeeRolePermit.employee_id == self.right_user.id).all()
        # 如果没有角色或者只拥有业务员这个角色都不给登录
        if not self.user_role or (len(self.user_role)==1 and self.user_role[0].sp_type==2):
            url = "/account/no_role"
            if self.user_role:
                url = url + "?p=sm"
            self.write(dict(code=200, msg=u'success', url=url))
            return
        self.user_role = self.user_role[0]
        auth_role_msg = self.auth_role()
        if auth_role_msg:
            self.write(dict(code=406, msg=auth_role_msg))
            return

        # 获取账户信息
        self.user_profile = self.get_user_profile(self.right_user.id)

        sys_type_id, sys_type_code = self.sys_type.id, self.sys_type.code
        self.sys_id = self.right_user.sys_id

        if sys_type_code in ["mr", "mch", "dt"] or self.user_role.sp_type not in [1, 255]:
            if self.password in [self.user_profile.phone1, self.user_profile.phone2]:
                self.set_account_session(self.right_user, sys_type_code, sys_type_id, before=True)
                self.write(dict(msg=u'初次登录请修改密码', code=405))
                return

        if sys_type_code in ["bk", "ub"]:
            # 判断是不是同业银行
            sys_type_code = self.get_sys_type_code(self.right_user.sys_id, sys_type_code)
            self.set_account_session(self.right_user, sys_type_code, sys_type_id, before=False)
            self.write(dict(code=200, msg=u'success', url=INDEX_URL[sys_type_code]))
            return
        else:
            # 如果是连锁商户员工,随机取一个门店登录
            cs_shortname = None
            if sys_type_code == "mr":
                if self.user_role.sp_type not in [1, 255]:
                    sys_type_code = self.union_employee[1]
                    sys_type_id = self.union_employee[2]
                    self.sys_id = self.union_employee[0]
                    if self.user_role.is_follower == 1 or self.user_role.sp_type == 3:
                        cs_shortname = uline_session.query(MchInletInfo).filter(
                            MchInletInfo.mch_id == self.sys_id).one().mch_shortname
            self.set_account_session(self.right_user, sys_type_code, sys_type_id,
                                     before=False, cs_name=cs_shortname)

            # 更新登录时间
            uline_session.query(Employee.last_login).filter(Employee.id == self.right_user.id).update(
                {"last_login": datetime.datetime.now()})
            uline_session.commit()
            self.write(dict(code=200, msg=u'success', url=INDEX_URL[sys_type_code]))
            return

    @coroutine
    def auth_user(self):
        msg = ""
        if not self.right_user:
            msg = "账号不存在,请重新核对账号"
        else:
            right_password = yield bcrypt_pwd(self.password, self.right_user.login_passwd)
            if not right_password:
                msg = "密码错误,请重新输入"
            elif self.right_user.status in [2, "2"]:
                msg = "账号未激活,请联系管理员"
            else:
                # 某个渠道商下面只允许一家商户可登陆
                dt_mch = uline_session.query(Employee.sys_id, MchInletInfo.dt_id, SysType.code).join(MchInletInfo,
                                                                                                     MchInletInfo.mch_id == Employee.sys_id).join(
                    SysType, SysType.id == Employee.sys_type_id).filter(Employee.id == self.right_user.id).first()

                if dt_mch and str(dt_mch[1]) == '10000072751' and str(dt_mch[0]) != '100001544897' and dt_mch[2] == "mch":
                    msg = "此用户未开通登录权限,请联系渠道商"

        raise Return(msg)

    def set_account_session(self, right_user, sys_type_code, sys_type_id, before=True, cs_name=None):

        if before:
            # code_id 供初次修改密码使用,银行官方不支持
            self.session['code_id'] = right_user.id
            # 员工登录支持初次登录修改密码
            self.session['sys_type_code'] = sys_type_code

        else:
            # 如果是员工,存储员工上级管理员id,和名称
            self.session[self.map_current_user()[sys_type_code][0]] = self.sys_id
            self.session[self.map_current_user()[sys_type_code][1]] = self.user_profile.name
            self.session["sys_type_id"] = sys_type_id
            self.session["sys_type_code"] = sys_type_code
            self.session['employee_id'] = right_user.id
            if sys_type_code == "mch":
                self.session['cs_name'] = cs_name

            self.set_secure_cookie(self.map_current_user()[sys_type_code][0],
                                   str(self.session[self.map_current_user()[sys_type_code][0]]), expires_days=1)
            self.set_secure_cookie(self.map_current_user()[sys_type_code][1],
                                   str(self.session[self.map_current_user()[sys_type_code][0]]), expires_days=1)
        self.session.save()
        return

    def auth_role(self):
        msg = None
        if self.sys_type.code == "mch":
            cs = uline_session.query(MchInletInfo).filter(MchInletInfo.mch_id == self.right_user.sys_id).one().cs_id
            if cs:
                msg = "直营门店管理员账户无登录权限,请联系连锁商户管理员"
        elif self.sys_type.code == "mr" and self.user_role.sp_type not in [1, 255]:
            self.union_employee = uline_session.query(UnionEmployee.sys_id, SysType.code,
                                                      UnionEmployee.sys_type_id).join(SysType, UnionEmployee.sys_type_id == SysType.id).filter(
                UnionEmployee.employee_id == self.right_user.id).first()
            if not self.union_employee[0]:
                msg = "此账号没有门店管理权限,无权限登录,请联系商户管理员"
        return msg


# 退出登录


class LogoutHandler(CommanHandler):
    @authenticated
    def get(self):
        self.session.clear_session()
        self.clear_all_cookies()
        self.redirect('/account/')


class Employee_cs(CommanHandler):

    @authenticated
    def get(self):
        employee_id = self.session.get('employee_id')
        sys_type_id = self.session.get('sys_type_id')
        sys_id = self.session.get('mch_id')
        cs = uline_session.query(MchInletInfo).join(UnionEmployee, UnionEmployee.sys_id == MchInletInfo.mch_id).filter(
            UnionEmployee.sys_type_id == sys_type_id, UnionEmployee.employee_id == employee_id).all()
        ret = [dict(zip(['id', 'name'], [i.mch_id, i.mch_shortname])) for i in cs if str(i.mch_id) != str(sys_id)]
        self.write({"code": 200, "data": ret})
        return


class ChangeCs(CommanHandler):

    @authenticated
    def post(self):
        form = changelogin(self)
        cs_id = form.cs_id.data
        employee_id = self.session.get('employee_id')
        sys_type_id = self.session.get('sys_type_id')
        cs = uline_session.query(MchInletInfo).join(UnionEmployee, UnionEmployee.sys_id == MchInletInfo.mch_id).filter(
            UnionEmployee.sys_type_id == sys_type_id, UnionEmployee.employee_id == employee_id).all()
        cs_ids = {str(cs_.mch_id): cs_.mch_shortname for cs_ in cs}
        if str(cs_id) not in cs_ids.keys():
            self.write({"code": 406, "msg": "参数错误"})
            return
        else:
            self.session["mch_id"] = cs_id
            self.session["cs_name"] = cs_ids[str(cs_id)]
            self.session.save()
            self.write({"code": 200, "msg": "切换成功"})
            return


# 重置密码验证验证码
class ResetPasswordAuthHandler(CommanHandler):
    @authenticated
    def post(self):
        self.form = AuthCodeForm(self)
        if not self.form.validate():
            self.write(dict(code=406, msg="验证码错误"))
            return
        auth_code = self.form.auth_code.data
        employee_id = self.session["employee_id"]
        if self.check_auth_code(auth_code, employee_id):
            self.write(dict(code=200, msg="验证码正确"))
        else:
            self.write(dict(code=406, msg="验证码错误"))
        return


class ResetPasswordAuthCodeHandler(CommanHandler):
    @authenticated
    @coroutine
    def get(self):

        msg = {'code': 406, 'msg': 'fail'}
        try:
            query_id = self.session["employee_id"]
            auth_code, key = self.get_auth_code(query_id)
            message_tool, email, mobile = '', '', ''
            # 商户,连锁商户,门店,渠道商及其所有员工发送短信消息
            user_profile = self.get_user_profile(query_id)
            self.user_role = uline_session.query(Role).join(EmployeeRolePermit,
                                                            EmployeeRolePermit.role_id == Role.id).filter(
                EmployeeRolePermit.employee_id == query_id).first()
            if self.session["sys_type_code"] in ["mch", "mr", "dt"]:
                message_tool = "message"
                mobile = user_profile.phone1

            # 官方,银行发送邮件
            if self.session["sys_type_code"] in ["ub", "bk", "ibk"]:
                if self.user_role.sp_type not in [1, 255]:
                    message_tool = "message"
                    mobile = user_profile.phone1
                else:
                    email = user_profile.email
                    message_tool = "email"
            msg = yield self.send_auth_code(auth_code, key, mobile if message_tool == "message" else email,
                                            send_type=message_tool)
        except Exception as err:
            log.exception.info(err)
        self.write(msg)
        return


class ResetPasswordModifyHandler(CommanHandler):
    @authenticated
    def post(self):
        form = ModifyPasswordForm(self)
        new_pwd = form.newPwd.data
        self._id = self.session["employee_id"]
        if not form.validate():
            error_string = []
            for field_errors in form.errors.values():
                error_string.extend(field_errors)
            self.write({'code': 406, 'msg': "\n".join(error_string)})
            return
        self.update_password(new_pwd, self._id)
        self.write({'code': 200, 'msg': '密码设置成功'})
        return


# 初次登录设置密码
class FirstLoginGetAuthCodeHandler(CommanHandler):
    @coroutine
    def get(self):
        msg = {'code': 406, 'msg': 'fail'}
        try:
            code_id = self.session["code_id"]
            auth_code, key = self.get_auth_code(code_id)
            # 商户,连锁商户,门店,渠道商及其所有员工发送短信消息
            # if self.session["sys_type_code"] in ["mch", "mr", "dt"]:
            self.user_role = uline_session.query(Role).join(EmployeeRolePermit,
                                                            EmployeeRolePermit.role_id == Role.id).filter(
                EmployeeRolePermit.employee_id == self.session["code_id"]).first()
            if self.session['sys_type_code'] in ["mr", "mch", "dt"] or self.user_role.sp_type not in [1, 255]:

                user_profile = self.get_user_profile(code_id)
                mobile = user_profile.phone1
                msg = yield self.send_auth_code(auth_code, key, mobile, send_type="message")
        except Exception as err:
            log.exception.info(err)
        self.write(msg)
        return


# 第一次登录修改密码核对验证码


class FirstLoginAuthCodeCodeHandler(CommanHandler):
    def post(self):
        form = AuthCodeForm(self)
        if not form.validate():
            self.write({'code': 406, 'msg': '参数错误'})
        auth_code = form.auth_code.data
        code_id = self.session.get('code_id')
        if self.check_auth_code(auth_code, code_id):
            self.write({'code': 200, 'msg': 'success'})
        else:
            self.write({'code': 406, 'msg': '验证码错误,请重新输入'})
        self.finish()
        return


class FirstLoginModifyHandler(CommanHandler):
    def post(self):
        form = ModifyPasswordForm(self)
        new_pwd = form.newPwd.data
        code_id = self.session.get('code_id')
        if not form.validate():
            error_string = []
            for field_errors in form.errors.values():
                error_string.extend(field_errors)
            self.write({'code': 406, 'msg': "\n".join(error_string)})
            return
        self.update_password(new_pwd, code_id)
        self.write({'code': 200, 'msg': 'ok'})
        self.finish()
        return


# 忘记密码


class ForgetPasswordHandler(CommanHandler):

    def get(self):
        self.render('common/changePassword.html')

    def post(self):
        self.form = ForgetPasswordForm(self)
        if not self.form.validate():
            self.write({'code': 406, 'msg': '参数错误,请重新确认'})
            return
        login_name = self.form.login_name.data

        employee = uline_session.query(Employee).filter(Employee.login_name == login_name).first()
        if not employee or (employee and employee.status == 2):
            self.write({'code': 406, 'msg': '该账户不存在,请重新确认'})
            return

        # self.user_role = uline_session.query(Role).join(EmployeeRolePermit,
        #                                                 EmployeeRolePermit.role_id == Role.id).filter(
        #     EmployeeRolePermit.employee_id == employee.id).first()
        sys_type_code = uline_session.query(SysType).filter(SysType.id == employee.sys_type_id).one()

        if sys_type_code.code in ["ub", "bk"] and employee.creator_id == 0:
            self.write({'code': 406, 'msg': '银行,官方管理员账户不支持修改密码,如您忘记密码,请联系客服4008047555'})
            self.finish()
            return

        token = self.get_token(employee.id, 1800)
        self.write({'code': 200, 'token': token, 'sys_type_code': sys_type_code.code})
        self.finish()
        return


class ForgetPasswordAuthHandler(CommanHandler):
    def post(self):
        form = AuthCodeTokenForm(self)
        token = form.token.data
        login_id = self.rdb.get(token)
        auth_code = form.auth_code.data
        sys_type_code = form.sys_type_code.data
        if not form.validate() and not login_id:
            self.write({'code': 406, 'msg': '参数错误,请重新确认'})
            self.finish()
            return
        if self.check_auth_code(auth_code, login_id):
            self.write({'code': 200, 'token': token, 'sys_type_code': sys_type_code})
            return
        self.write({'code': 406, 'msg': '验证码错误,请重新输入'})
        return


class ForgetPasswordAuthCodeHandler(CommanHandler):
    @asynchronous
    @coroutine
    def get(self):
        msg = {'code': 406, 'msg': 'fail'}
        form = AuthTokenForm(self)
        token = form.token.data
        login_id = self.rdb.get(token)
        if not form.validate() and not login_id:
            self.write(msg)
        else:
            try:
                auth_code, key = self.get_auth_code(login_id)
                # 商户,连锁商户,门店,渠道商及其所有员工发送短信消息
                mobile = self.get_user_profile(login_id).phone1
                msg = yield self.send_auth_code(auth_code, key, mobile, send_type="message")

            except Exception as err:
                log.exception.info(err)
            self.write(msg)
            return


class ForgetPasswordModifyHandler(CommanHandler):
    def post(self):
        form = ModifyPasswordTokenForm(self)
        new_pwd = form.newPwd.data
        token = form.token.data
        login_id = self.rdb.get(token)
        if not login_id:
            self.write({'code': 406, 'msg': '参数错误,请重新尝试'})
            return
        if not form.validate():
            error_string = []
            for field_errors in form.errors.values():
                error_string.extend(field_errors)
            self.write({'code': 406, 'msg': "\n".join(error_string)})
            return
        self.update_password(new_pwd, login_id)
        self.write({'code': 200, 'msg': "success"})
        return
