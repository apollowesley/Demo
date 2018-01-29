# -*- coding: utf-8 -*-
import json
from datetime import datetime
from tornado import gen
from tornado.web import authenticated
from uline.public.permit import check_permission
from uline.model.uline.other import SysType
from uline.public import common, log
from uline.handlers.baseHandlers import CommanHandler
from uline.model.uline.user import Employee, UnionEmployee, DtSubUser
from uline.model.uline.info import MchInletInfo, EmployeeUserLog, UserProfile
from uline.model.uline.permit import EmployeeRolePermit, Role
from .common import (get_old_employee_role, STATUS, get_employee_login,
                     get_employee_profile, get_employee_all_role, get_all_cs, query_role_name, get_headquarters, get_modify_id_sys_code)
from .sub_user_form import SubUserEditForm
from uline.model.uline.base import uline_session

INDEX_PAGE_SIZE = 10


class SubUserEditHandler(CommanHandler):
    """修改子账户的详细信息"""

    @authenticated
    @check_permission
    def prepare(self):
        self.form = SubUserEditForm(self)
        self.sys_type_code = self.session["sys_type_code"]
        self.employee_id = self.form.modify_id.data

    def get(self):
        response = common.scc_rsp(code=200, msg='操作成功')
        employee_profile = get_employee_profile(self.employee_id, diff="edit")
        employee_profile.pop("last_login")
        response["profile"] = employee_profile

        try:
            headquarters = get_headquarters(self.employee_id) if self.sys_type_code in ["mr"] else None
            all_role = get_employee_all_role(self.employee_id, self.sys_type_code, headquarters=headquarters)
            employee_role_id = get_old_employee_role(self.employee_id)
            for i in all_role:
                i["role"] = "true" if i['role_id'] in employee_role_id else "false"
            response['role'] = all_role

            # 连锁商户展示所有门店信息
            if self.sys_type_code in ["mr"]:
                if headquarters == 2:
                    left_cs = []
                    right_cs = []
                else:
                    all_cs_data = get_all_cs(self.employee_id)
                    employee_cs_id = uline_session.query(UnionEmployee).filter(
                        UnionEmployee.employee_id == self.employee_id).all()
                    mch_ids = [_id.sys_id for _id in employee_cs_id] if all(employee_cs_id) else []
                    right_cs = []
                    left_cs = []
                    for i in all_cs_data:
                        if i["sys_id"] in mch_ids:
                            right_cs.append(i)
                        else:
                            left_cs.append(i)
                response["left_cs"] = left_cs
                response["right_cs"] = right_cs
                response["headquarters"] = headquarters
        except Exception as err:
            log.exception.exception(err)
            response = common.scc_rsp(code=406, msg='操作失败')
        self.write(json.dumps(response))
        return

    @gen.coroutine
    def post(self):
        self.operate_employee_id = self.session["employee_id"]

        self.form.employee_id = self.operate_employee_id
        self.form.sys_type_code = self.sys_type_code

        employee_role = json.loads(self.get_argument('employee_role'))
        self.form.employee_role = employee_role
        if self.sys_type_code in ["mr"]:
            # 连锁商户门店信息
            junior_ids = json.loads(self.get_argument('junior_ids'))
            self.form.junior_ids = junior_ids

        self.old_user = get_employee_login(self.employee_id)

        if not self.form.validate():
            error_string = []
            for field_errors in self.form.errors.values():
                error_string.extend(field_errors)
            response = common.f_rsp(code=406, msg=error_string)
            self.write(response)
            return

        self._record = []
        try:
            # 获取原始员工登录信息
            old_profile = get_employee_profile(self.employee_id, diff="edit")
            self.old_role_id = get_old_employee_role(self.employee_id)
            self.salesman_role = uline_session.query(Role).filter(Role.sp_type == 2).one()

            # 更新员工登录档案信息
            yield self.update_employee_profile(old_profile)

            # 更新员工角色信息,并写入角色修改记录
            yield self.update_employee_role(employee_role, self.old_role_id)

            if self.sys_type_code in ["mr"]:
                self.update_chain_sub_user(junior_ids)
            if self._record:
                new_add_record = EmployeeUserLog(comment=",".join(self._record),
                                                 employee_id=self.employee_id,
                                                 operate_id=self.operate_employee_id,
                                                 eutype=1,
                                                 create_at=datetime.now())
                uline_session.add(new_add_record)

            uline_session.commit()
            # final_role_id = get_old_employee_role(self.employee_id)

            # 更新完所有信息后,如果员工不属于任何一个角色则取消员工登录的权利
            # if not final_role_id:
            #     uline_session.query(Employee).filter(Employee.id == self.employee_id).update({'status': 2})
            #     uline_session.query(UserProfile).filter(UserProfile.id == self.old_user.user_id).update({'status': 2})
            #     uline_session.commit()

            response = common.scc_rsp(msg=self.form.login_name.data)
        except Exception as err:
            log.exception.exception(err)
            uline_session.rollback()
            response = common.f_rsp(code=500, msg=["更新失败,请重新尝试"])
        self.write(response)
        return

    def update_chain_sub_user(self, _data):
        _data = map(int, _data)
        # 获取修改前连锁商户员工所属的门店
        headquarters = self.form.headquarters.data

        if headquarters == 1:

            old_css = uline_session.query(UnionEmployee.employee_id, UnionEmployee.sys_id).\
                filter(UnionEmployee.employee_id == self.employee_id).all()

            old_css = [cs_id[1] for cs_id in old_css] if len(old_css) > 1 or (
                len(old_css) == 1 and old_css[0][1] is not None) else []

            add_new = list(set(_data) - set(old_css))
            mch_sys_id = uline_session.query(SysType).filter(SysType.code == "mch").first()

            if add_new:
                if not old_css:
                    update_cs = uline_session.query(Employee).filter(Employee.sys_id == add_new[-1]).first()
                    uline_session.query(UnionEmployee).\
                        filter(UnionEmployee.employee_id == self.employee_id).\
                        update({'sys_id': update_cs.sys_id, 'sys_type_id': update_cs.sys_type_id,
                                'create_at': datetime.now()})
                    add_new.pop()
                if add_new:
                    uline_session.execute(UnionEmployee.__table__.insert(), [
                        {'sys_id': _id, 'employee_id': int(self.employee_id),
                         'sys_type_id': mch_sys_id.id, 'create_at': datetime.now()}
                        for _id in add_new])

            deles = list(set(old_css) - set(_data))

            if deles:
                dele_session = uline_session.query(UnionEmployee).filter(
                    UnionEmployee.sys_id.in_(deles),
                    UnionEmployee.employee_id == int(self.employee_id))
                dele_session.delete(synchronize_session=False)

        return

    @gen.coroutine
    def update_employee_profile(self, old_profile):

        diff_profile = {}
        diff_employee = {}
        change_defined = {"login_name": "登录名", "name": "员工名称", "email": "邮箱账号", "phone1": "电话号码"}
        change_str = "{}由{}修改为{}"
        for key, value in old_profile.items():
            if self.form.data.get(key) != value:
                if key in ["status", "login_name"]:
                    diff_employee.update({key: self.form.data.get(key)})
                if key in ["status", "name", "email", "phone1"]:
                    diff_profile.update({key: self.form.data.get(key)})
                if key in ["status"]:
                    self._record.append(STATUS[str(self.form.status.data)] + "账号")
                if key in ["login_name", "name", "email", "phone1"]:
                    self._record.append(change_str.format(
                        change_defined[key], value, self.form.data.get(key)))

        if diff_profile:
            diff_profile.update({"update_at": datetime.now()})
            uline_session.query(UserProfile).filter(
                UserProfile.id == self.old_user.user_id).update(diff_profile)

        if not old_profile.get("last_login") and "phone1" in diff_profile.keys():
            login_passwd = yield common.bcrypt_pwd(str(self.form.phone1.data))
            diff_employee.update({"login_passwd": login_passwd})

        if diff_employee:
            diff_employee.update({"update_at": datetime.now()})
            uline_session.query(Employee).filter(Employee.id == self.employee_id).update(diff_employee)

        if self.sys_type_code == "dt":
            dt_sub_user = uline_session.query(DtSubUser).filter(DtSubUser.dt_sub_id == self.employee_id)
            sub_query = dt_sub_user.first()
            if sub_query and self.salesman_role.id in self.old_role_id:
                dt_sub_user.update({"dt_sub_name": self.form.name.data, "status": self.form.status.data})

    @gen.coroutine
    def update_employee_role(self, new_role_id, old_role_id):

        # old_role_id = get_old_employee_role(self.employee_id)
        if not new_role_id and not old_role_id:
            return

        if not new_role_id and old_role_id:
            self.delete_role(old_role_id, new_role_id)
            return

        if new_role_id:
            new_role_id = map(int, new_role_id)
            update_new_role = list(set(new_role_id) - set(old_role_id))
            # 添加新角色
            if update_new_role:
                uline_session.execute(EmployeeRolePermit.__table__.insert(),
                                      [{'employee_id': self.employee_id, 'role_id': _id, }
                                       for _id in update_new_role])
                new_role_name = query_role_name(update_new_role)
                new_add_record = "新增{}角色权限".format(new_role_name)
                self._record.append(new_add_record)
                if self.sys_type_code == "dt":
                    dt_update_session = uline_session.query(DtSubUser).filter(
                        DtSubUser.dt_sub_id == self.employee_id).first()
                    if not dt_update_session:
                        if self.salesman_role.id in update_new_role:
                            password = yield common.bcrypt_pwd(str(self.form.phone1.data))
                            new_add_record = DtSubUser(dt_sub_id=self.employee_id,
                                                       dt_user_dt_id=self.current_user,
                                                       dt_sub_name=self.form.name.data,
                                                       email=self.form.email.data,
                                                       password=password,
                                                       status=self.form.status.data,
                                                       login_name=self.form.login_name.data,
                                                       phone=self.form.phone1.data)
                            uline_session.add(new_add_record)
                    else:
                        uline_session.query(DtSubUser).filter(DtSubUser.dt_sub_id == self.employee_id).update(
                            {"status": self.form.status.data})

            self.delete_role(old_role_id, new_role_id)

    def delete_role(self, old_role_id, new_role_id):
        # 删除旧角色
        delete_old_role = list(set(old_role_id) - set(new_role_id))
        if delete_old_role:
            dele_session = uline_session.query(EmployeeRolePermit).filter(
                EmployeeRolePermit.role_id.in_(delete_old_role),
                EmployeeRolePermit.employee_id == int(self.employee_id))
            dele_session.delete(synchronize_session=False)
            # 同步渠道商业务员专用表
            if self.sys_type_code == "dt":
                if self.salesman_role.id in delete_old_role:
                    uline_session.query(DtSubUser).filter(DtSubUser.dt_sub_id == self.employee_id).update({"status": 2})

            old_role_name = query_role_name(delete_old_role)
            delete_old_record = "去除{}角色权限".format(old_role_name)
            self._record.append(delete_old_record)

        return
