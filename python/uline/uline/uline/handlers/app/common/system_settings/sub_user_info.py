# -*- coding: utf-8 -*-
import json
from tornado import gen
from tornado.web import authenticated
from uline.public import common, log
from uline.handlers.baseHandlers import CommanHandler
from uline.model.uline.base import uline_session
from uline.model.uline.user import Employee
from uline.model.uline.info import EmployeeUserLog, UserProfile
from uline.model.uline.permit import Role, EmployeeRolePermit
from .sub_user_form import SubUserInfoForm
from .common import STATUS, get_employee_profile, LOCAL_HTML, get_modify_id_sys_code
from sqlalchemy import desc


class SubUserInfoHandler(CommanHandler):
    """查询员工账户的详细信息"""

    @authenticated
    def prepare(self):
        self.form = SubUserInfoForm(self)
        self.sys_type_code = self.session["sys_type_code"]

    @gen.coroutine
    def get(self):

        if not self.form.validate():
            error_string = []
            for field_errors in self.form.errors.values():
                error_string.extend(field_errors)
            response = common.f_rsp(code=406, msg=error_string)
            self.write(response)
            return

        self.employee_id = self.form.employee_id.data
        self.profile_location = self.get_argument("profile_location", None)
        employee_profile = self.get_profile_detail(self.employee_id)
        if self.profile_location == "webpage":
            sp_type = uline_session.query(Role).join(EmployeeRolePermit, EmployeeRolePermit.role_id == Role.id).filter(
                EmployeeRolePermit.employee_id == self.employee_id).first()
            cs_name = self.session["cs_name"] if self.sys_type_code in ["mch"] else None
            data_html = self.render_string('common/employee_profile.html', sys_type_code=self.sys_type_code,
                                           data=employee_profile, sp_type=sp_type.sp_type, cs_name=cs_name)
            html = '{}/account/employee_profile.html'.format(LOCAL_HTML[self.sys_type_code])
            self.render(html, data_html=data_html, sys_type_code=self.sys_type_code)
        else:
            self.write(employee_profile)
        return

    def get_profile_detail(self, employee_id):

        # 获取员工个人登录资料
        profile = get_employee_profile(employee_id)
        profile["create_at"] = profile["create_at"].strftime("%Y-%m-%d %H:%M:%S")
        profile["status"] = STATUS[str(profile["status"])]

        # 获取员工资料变更信息
        change_records = self.get_employee_records(employee_id)

        # 获取员工角色信息
        employee_role = uline_session.query(Role.name).join(EmployeeRolePermit, EmployeeRolePermit.role_id == Role.id). \
            filter(EmployeeRolePermit.employee_id == employee_id).all()
        employee_role = ",".join(set([role[0] for role in employee_role])) if all(employee_role) else "无角色"
        profile["employee_role"] = employee_role

        # 获取已有门店简称
        if self.sys_type_code in ["mr"] or (self.sys_type_code in ["mch"] and self.session["cs_name"] is not None):

            cs_profile = self.get_cs_name()
            profile["employee_cs_name"] = cs_profile

        response = common.scc_rsp()
        response['employee_record'] = change_records
        response['employee_profile'] = profile
        return response

    def get_employee_records(self, employee_id):

        employee_record = uline_session.query(EmployeeUserLog.operate_id, EmployeeUserLog.comment,
                                              EmployeeUserLog.create_at, Employee.login_name, UserProfile.name)
        employee_record = employee_record.join(Employee, EmployeeUserLog.operate_id == Employee.id)
        employee_record = employee_record.join(UserProfile, UserProfile.id == Employee.user_id)
        employee_record = employee_record.filter(EmployeeUserLog.employee_id == employee_id).\
            order_by(desc(EmployeeUserLog.create_at)).all()

        # 前端显示按时间倒序排序
        records = [dict(zip(["operate_user", "comment", "create_at", "email", "name"], single_record)) for single_record
                   in employee_record]
        for i in records:
            i["create_at"] = i["create_at"].strftime("%Y-%m-%d %H:%M:%S")
        return records

    def get_cs_name(self):
        with self.db.get_db() as cur:
            ret = """select
                     sys_type.code,
                     mch_inlet_info.mch_shortname
                     from union_employee
                     LEFT  JOIN mch_inlet_info on mch_inlet_info.mch_id=union_employee.sys_id
                     LEFT join sys_type on sys_type.id=union_employee.sys_type_id
                     left join dt_inlet_info on dt_inlet_info.dt_id=union_employee.sys_id
                     where
                     union_employee.employee_id=%(employee_id)s
                     ;
                     """
            cur.execute(ret, {"employee_id": self.employee_id})
            ret = cur.fetchall()
            id_name = []
            if not ret:
                id_name.append("总部")
            for i in ret:
                if i[0] == "mr":
                    id_name.append("总部")
                if i[0] == "mch":
                    if not i[1]:
                        id_name.append("此账户不属于门店或总部")
                    else:
                        id_name.append(i[1])
            return ",".join(id_name)
