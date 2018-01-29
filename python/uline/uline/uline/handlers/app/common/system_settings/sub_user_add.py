# -*- coding: utf-8 -*-
import json
import random
import datetime
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.web import authenticated
from uline.public import common, log
from uline.handlers.baseHandlers import CommanHandler
from uline.model.uline.user import Employee, UnionEmployee, DtSubUser
from uline.model.uline.info import EmployeeUserLog, UserProfile
from uline.model.uline.base import uline_session
from uline.model.uline.other import SysType
from .sub_user_form import SubUserForm
from uline.settings import env, MESSAGE_URL
from .common import get_employee_login, get_login_suffix, get_employee_all_role, get_all_cs
from sqlalchemy.sql import func
from uline.public.permit import check_permission
from uline.model.uline.permit import Role, EmployeeRolePermit


class SubUserAddHandler(CommanHandler):
    """处理子账户请求"""

    @authenticated
    @check_permission
    def prepare(self):

        self.form = SubUserForm(self)
        self.sys_type_code = self.session["sys_type_code"]
        self.employee_id = self.session["employee_id"]
        self.employee = get_employee_login(self.employee_id)
        self.form.employee_id = self.employee_id
        self.form.sys_type_code = self.sys_type_code

    @gen.coroutine
    def get(self):

        response = common.scc_rsp(code=200, msg='操作成功')

        suffix = get_login_suffix(self.employee, self.sys_type_code)
        response["suffix"] = suffix

        try:
            response["role"] = get_employee_all_role(self.employee_id, self.sys_type_code)
            # 连锁商户展示所有门店信息
            if self.sys_type_code in ["mr"]:
                response['cs_data'] = get_all_cs(self.employee_id)

        except Exception as err:
            log.exception.exception(err)
            response = common.scc_rsp(code=406, msg='操作失败')
        self.write(json.dumps(response))
        return

    @gen.coroutine
    def post(self):
        employee_role = json.loads(self.get_argument('employee_role'))
        self.form.employee_role = employee_role
        if self.sys_type_code in ["mr"]:
            junior_ids = json.loads(self.get_argument('junior_ids'))
            self.form.junior_ids = junior_ids

        if not self.form.validate():
            error_string = []
            for field_errors in self.form.errors.values():
                error_string.extend(field_errors)
            response = common.f_rsp(code=406, msg=error_string)
            self.write(response)
            return

        new_employee_id = uline_session.query(func.max(Employee.id)).first()
        new_employee_id = new_employee_id[0] + random.randint(1, 3) if new_employee_id[0] else 10000000

        try:

            login_passwd = yield common.bcrypt_pwd(str(self.form.phone1.data))
            status = self.form.status.data
            new_employee_profile = UserProfile(
                id=new_employee_id, name=self.form.name.data,
                email=self.form.email.data, phone1=self.form.phone1.data,
                creator_id=self.employee.sys_id, status=status,
                create_at=datetime.datetime.now(), update_at=datetime.datetime.now()
            )
            uline_session.add(new_employee_profile)

            new_sub_user = Employee(id=new_employee_id,
                                    sys_type_id=self.employee.sys_type_id,
                                    sys_id=self.employee.sys_id,
                                    login_name=self.form.login_name.data,
                                    login_passwd=login_passwd,
                                    user_id=new_employee_id,
                                    creator_id=self.employee.id,
                                    status=status,
                                    create_at=datetime.datetime.now(),
                                    update_at=datetime.datetime.now()
                                    )

            uline_session.add(new_sub_user)

            # 连锁商户新建员工时,增加门店id列表,必填项 [{"sys_id"}]
            if self.sys_type_code in ["mr"]:
                # 如果不是总部
                headquarters = self.form.headquarters.data
                if headquarters == 1:
                    sys_type = uline_session.query(SysType).filter(SysType.code == "mch").one()

                    uline_session.execute(UnionEmployee.__table__.insert(), [
                        {'sys_id': mch,
                         'employee_id': new_employee_id,
                         'sys_type_id': sys_type.id,
                         "create_at": datetime.datetime.now()} for
                        mch in junior_ids])
                else:
                    mr_union = UnionEmployee(
                        sys_id=self.session["chain_id"],
                        employee_id=new_employee_id,
                        sys_type_id=self.session["sys_type_id"],
                        create_at=datetime.datetime.now()
                    )
                    uline_session.add(mr_union)

            # 角色用户信息存储,参数role_id是角色id列表[1,2,3]
            if employee_role:
                uline_session.execute(EmployeeRolePermit.__table__.insert(),
                                      [{'employee_id': new_employee_id,
                                        'role_id': _id} for _id in employee_role])

            new_add_record = EmployeeUserLog(comment="账号创建成功",
                                             employee_id=new_employee_id,
                                             operate_id=self.employee_id,
                                             eutype=1,
                                             create_at=datetime.datetime.now()
                                             )
            uline_session.add(new_add_record)

            if self.sys_type_code == "dt":
                role_id = uline_session.query(Role).filter(Role.sp_type == 2).one()
                int_role = map(int, employee_role)
                if role_id.id in int_role:
                    new_add_record = DtSubUser(dt_sub_id=new_employee_id, dt_user_dt_id=self.employee.sys_id,
                                               dt_sub_name=self.form.name.data,
                                               email=self.form.email.data,
                                               password=login_passwd,
                                               status=status,
                                               login_name=self.form.login_name.data,
                                               phone=self.form.phone1.data)
                    uline_session.add(new_add_record)

            # 发送激活信息
            yield self.send_activated_email()
            uline_session.commit()
            msg = '您已新增员工账号{}'.format(self.form.login_name.data)
            response = common.scc_rsp(code=200, msg=msg)
        except Exception as err:
            log.exception.exception(err)
            response = common.f_rsp(code=406, msg="操作失败,请重新尝试")
        self.write(response)
        return

    @gen.coroutine
    def send_activated_email(self):

        user_type_dict = {"bk": "银行", "ub": "uline官方", "ibk": "同业银行",
                          "dt": "渠道商", "mr": "连锁商户", "mch": "商户"}

        http_client = AsyncHTTPClient()
        login_url = {"DEV": "http://mch.stage.uline.cc/account/",
                     "LOCAL": "http://localhost:8893/account/",
                     "CMBC_PROD": "http://cms.cmbxm.mbcloud.com/account/",
                     "SPD_PROD": "http://cms.spd.uline.cc/account/",
                     "SPDLOCAL": "浦发内网域名"
                     }
        data = {'env': env, 'reciver': self.form.email.data, 'title': u'uline员工激活信息', 'body': u"""
        尊敬的{}：

        您在ULINE系统{}平台的员工账号已创建！

        以下是您的账户所需要的重要信息，请妥善保管，注意保密：
        登录账号：{}
        初始登录密码：{}
        登录地址：{}

        广州优畅信息技术有限公司
        客服电话：400-8047555""".format(self.form.name.data,
                                   user_type_dict[self.sys_type_code],
                                   self.form.login_name.data,
                                   self.form.phone1.data,
                                   login_url[env]
                                   )}
        url = MESSAGE_URL + '/v1/email'
        try:
            for send_time in range(3):
                response = yield http_client.fetch(url, body=json.dumps(data), method='POST')
                print(response.body)
                if response.body in ['2', 2]:
                    log.exception.info("员工{}的激活邮件发送成功".format(self.form.login_name.data))
                    break
            else:
                log.exception.info("员工{}的激活邮件发送失败".format(self.form.login_name.data))
            raise gen.Return
        except Exception:
            pass
