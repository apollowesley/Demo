# -*- coding: utf-8 -*-
import json
from datetime import timedelta
from datetime import datetime
from .common import STATUS, get_employee_all_role, LOCAL_HTML
from tornado.web import authenticated
from uline.handlers.baseHandlers import CommanHandler
from collections import defaultdict
from uline.model.uline.base import uline_session
from uline.model.uline.info import MchInletInfo
from uline.model.uline.user import UnionEmployee
from sqlalchemy import cast, String
from uline.public.permit import check_permission
from .sub_user_form import SubUserIndexForm
INDEX_PAGE_SIZE = 10


class GetCsprofile(CommanHandler):

    def get(self):
        self.sys_type_code = self.session["sys_type_code"]
        query_id_name = self.get_argument("query_id_name", None)
        res_mch = uline_session.query(MchInletInfo.mch_id, MchInletInfo.mch_shortname)
        if query_id_name.isdigit():
            res = res_mch.filter(cast(MchInletInfo.mch_id, String).like('%' + query_id_name + '%'))
        else:
            res = res_mch.filter(MchInletInfo.mch_name.like('%' + query_id_name + '%'))
        res = res.filter(MchInletInfo.cs_id == self.get_user_id(self.sys_type_code))
        res = res.all()
        sys_id = self.get_user_id(self.sys_type_code)
        if str(sys_id).find(query_id_name) != -1 or "总部".find(query_id_name) != -1:
            res.append((sys_id, "总部"))
        ret = [dict(zip(['id', 'name'], i)) for i in res]
        self.write({"data": ret})
        return


# class SearchRole(CommanHandler):
#
#     @authenticated
#     def get(self):
#
#         # 获取员工角色信息
#         employee_id = self.session["employee_id"]
#         sys_type_code = self.session["sys_type_code"]
#         employee_role = get_employee_all_role(employee_id, sys_type_code)
#
#         role = [dict(zip(["role_id", "role_name"], role)) for role in employee_role]
#
#         self.write(json.dumps(dict(role=role, code=200)))
#         return


class SubUserIndexHandler(CommanHandler):
    """处理子账户索引请求"""

    def prepare(self):
        self.form = SubUserIndexForm(self)

    @authenticated
    @check_permission
    def get(self):

        self.page_index = int(self.get_argument("p", 1))
        self.sys_type_code = self.session["sys_type_code"]
        self.sys_type_id = self.session["sys_type_id"]
        employee_id = self.session["employee_id"]

        self.sys_id = self.get_user_id(self.sys_type_code)

        # 获取员工角色信息
        role = get_employee_all_role(employee_id, self.sys_type_code)

        with self.db.get_db() as cur:
            sub_users, total_number = self.get_employees(cur)
            navigate_html = self.get_navigate_html(total_number)

        for sub_user in sub_users:
            sub_user["create_at"] = sub_user["create_at"].strftime("%Y-%m-%d %H:%M:%S")

        # if self.form.create_at_start.data:
        #     self.form.create_at_start.data = self.form.create_at_start.data.strftime("%Y-%m-%d")
        # if self.form.create_at_end.data:
        #     self.form.create_at_end.data = self.form.create_at_end.data.strftime("%Y-%m-%d")

        data_html = self.render_string('common/staffManagement.html', sys_type_code=self.sys_type_code,
                                       navigate_html=navigate_html, form=self.form, data=sub_users, role=role)

        html = '{}/system_settings/SubUserIndex.html'.format(LOCAL_HTML[self.sys_type_code])
        self.render(html, data_html=data_html, total_num=total_number)
        # self.write(json.dumps(dict(code=200,
        #                            data=sub_users,
        #                            total_num=total_number
        #                            )))
        return

    def get_employees(self, cur):

        status = self.form.status.data or None
        create_at_start = self.form.create_at_start.data or None
        create_at_end = self.form.create_at_end.data or None
        employee_name = self.form.employee_name.data or None
        employee_id = self.form.employee_id.data or None
        role_id = self.form.role_id.data or None
        self.form.mch_name = ""

        create_at_end = create_at_end + timedelta(days=1) if create_at_end else datetime.now()

        if not create_at_start:
            create_at_start = datetime(2010, 1, 1, 0, 0, 0, 0)

        query = """select
                       employee.id,
                       user_profile.name,
                       employee.login_name,
                       employee.status,
                       employee.create_at,
                       user_profile.wx_id,
                      role.name
                       from employee
                       left join user_profile on employee.user_id = user_profile.id
                       left join employee_role_permit on employee_role_permit.employee_id = employee.id
                       left join role on role.id = employee_role_permit.role_id
                       where employee.sys_id = %(current_id)s
                       and (employee.sys_type_id = %(sys_type_id)s)
                       and (role.sp_type<>1 or role.sp_type is null)
                       and (employee_role_permit.role_id = %(role_id)s or %(role_id)s is null)
                       and(employee.status = %(status)s or %(status)s is null)
                       and(user_profile.name::VARCHAR ~ E%(employee_name)s or %(employee_name)s is null)
                       and(employee.id::VARCHAR ~ %(employee_id)s or %(employee_id)s is null)
                       AND (employee.create_at BETWEEN %(create_at_start)s::TIMESTAMP AND %(create_at_end)s::TIMESTAMP OR %(create_at_start)s IS NULL OR %(create_at_end)s IS NULL )
                       ;
                       """

        cur.execute(query, {'current_id': self.sys_id, 'sys_type_id': self.sys_type_id, 'status': status,
                            'employee_name': self.db.escape(employee_name), 'employee_id': employee_id,
                            'create_at_start': create_at_start, 'create_at_end': create_at_end,
                            'role_id': role_id})

        ret = cur.fetchall()
        if ret:
            ret, total_number = self.role_deal(ret)
            if self.sys_type_code == "mr":
                ret, total_number = self.chain_cs_name(cur, employee_id, ret)

        if ret:
            ret, total_number = self.deal_ret(ret, cur)
            _profile = (
                "employee_id", "employee_name", "login_name", "status", "create_at", "wx_id", "role_name", "cs_name")
            ret = [dict(zip(_profile, employee_user)) for employee_user in ret]
            for i in ret:
                i["status"] = STATUS[str(i["status"])]
        else:
            total_number = 0
        return ret, total_number

    def deal_ret(self, ret, cur):

        no_rights = [x for x in ret if x[3] == 2]
        # no_rights = sorted(no_rights, key=lambda tuple_e: tuple_e[4], reverse=True)

        have_rights = [x for x in ret if x[3] == 1]
        have_rights = sorted(have_rights, key=lambda tuple_e: tuple_e[4], reverse=True)

        have_rights.extend(no_rights)
        employee = have_rights[(self.page_index - 1) * 10:self.page_index * 10]

        return employee, len(ret)

    def chain_cs_name(self, cur, employee_id, ret):

        employee_id = [employee[0] for employee in ret]
        all_employee = {str(i[0]): list(i) for i in ret}
        mch_id = self.form.mch_id.data or None
        mch_name = ""
        if mch_id:
            mch_name_ = uline_session.query(MchInletInfo).filter(MchInletInfo.mch_id == mch_id).first()
            mch_name = mch_name_.mch_shortname if mch_name_ else "总部"

        cs_employee = uline_session.query(UnionEmployee).filter(UnionEmployee.sys_id == mch_id).all()
        cs_employee_set = set([employee.employee_id for employee in cs_employee]) if cs_employee else set()

        final_employee = cs_employee_set & set(employee_id) if mch_id else employee_id

        self.form.mch_name = mch_name

        if not final_employee:
            cs_ret, total_number = [], 0
        else:
            ret = """select
                    union_employee.employee_id,
                    sys_type.code,
                    mch_inlet_info.mch_shortname
                    from union_employee
                    LEFT  JOIN mch_inlet_info on mch_inlet_info.mch_id=union_employee.sys_id
                    LEFT join sys_type on sys_type.id=union_employee.sys_type_id
                    where
                    union_employee.employee_id in %(employee_id)s
                    ;
                    """
            cur.execute(ret, {'mch_id': mch_id,
                              "employee_id": tuple(final_employee)})
            cs_profile = cur.fetchall()
            sub_range = defaultdict(list)
            for x in cs_profile:
                if not sub_range[x[0]]:
                    sub_range[x[0]].extend(x)
                    if not x[2]:
                        cs_name_dict = {"mch": "", "mr": "总部"}
                        sub_range[x[0]][2] = cs_name_dict[x[1]]
                else:
                    if x[2]:
                        cs_name = sub_range[x[0]][2]
                        sub_range[x[0]][2] = ','.join([cs_name, x[2]]) if cs_name else x[2]
            cs_profile = sub_range.values()
            cs_profile = {str(i[0]): list(i) for i in cs_profile}
            cs_ret = []
            for key, value in all_employee.items():
                if cs_profile.get(key):
                    all_employee[key].append(cs_profile.get(key)[2])
                    cs_ret.append(all_employee.get(key))
            total_number = len(cs_ret)
        return [cs_ret, total_number]

    def role_deal(self, ret):
        sub_range = defaultdict(list)
        for i in ret:
            if not sub_range[i[0]]:
                sub_range[i[0]].extend(i)
                if not sub_range[i[0]][6]:
                    sub_range[i[0]][6] = "未设置角色"
            else:
                if i[6]:
                    role_name = sub_range[i[0]][6]
                    sub_range[i[0]][6] = ','.join([role_name, i[6]]) if role_name else i[6]
        role_details = sub_range.values()
        return [role_details, len(role_details)]
