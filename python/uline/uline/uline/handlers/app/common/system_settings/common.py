# -*- coding: utf-8 -*-
import json

from tornado.httpclient import AsyncHTTPClient
from uline.model.uline.user import UnionEmployee
from uline.model.uline.user import Employee, MchUser
from uline.model.uline.other import SysType
from uline.model.uline.info import UserProfile, MchInletInfo, DtInletInfo
from uline.model.uline.permit import Role, EmployeeRolePermit
from uline.model.uline.base import uline_session
from tornado import gen
from uline.settings import app_id, app_secret

STATUS = {"1": "启用", "2": "禁用"}
LOCAL_HTML = {"mch": "merchant", "mr": "chain", "dt": "distributor", "ub": "official", "bk": "bank",
              "ibk": "inter_bank"}


def get_employee_login(employee_id):
    employee = uline_session.query(Employee).filter(Employee.id == employee_id).one()
    return employee


def get_login_suffix(employee, sys_type_code):
    suffix = ""
    if sys_type_code == "bk":
        suffix = ["@", "bk"]
    if sys_type_code == "ub":
        suffix = ["@", "ulaiber"]
    if sys_type_code == "ibk":
        suffix = ["@", str(employee.sys_id), ".bk"]
    if sys_type_code in ["mr", "mch", "dt"]:
        suffix = ["@", str(employee.sys_id), ".", sys_type_code]
    suffix = "".join(suffix)
    return suffix


def get_user_profile(employee_id):
    user_profile = uline_session.query(UserProfile).join(
        Employee, Employee.user_id == UserProfile.id).filter(Employee.id == employee_id).first()
    return user_profile


def get_employee_profile(employee_id, diff="info"):

    login_profile = get_employee_login(employee_id)
    user_profile_ = get_user_profile(employee_id)

    if diff == "info":
        login_profile_tuple = ("create_at", "login_name", "id", "status")
        user_profile_tuple = ("email", "name", "phone1", "wx_id")
    if diff == "edit":
        login_profile_tuple = ("login_name", "status", "last_login")
        user_profile_tuple = ("email", "name", "phone1")

    profile = login_profile.to_dict(include=login_profile_tuple)
    user_profile = user_profile_.to_dict(include=user_profile_tuple)
    profile.update(user_profile)
    return profile


def get_employee_all_role(employee_id, sys_type_code, headquarters=None):
    employee = get_employee_login(employee_id)
    query_role = uline_session.query(Role).filter(Role.sys_id == employee.sys_id,
                                                  Role.sys_type_id == employee.sys_type_id, Role.sp_type == 0).all()

    role = [dict(zip(["role_id", "role_name", "is_follower"], [i.id, i.name, i.is_follower])) for i in query_role] if all(
        query_role) else []
    if sys_type_code in ["dt"]:
        salesman = uline_session.query(Role).filter(Role.sp_type == 2).one()
        role.append({"role_id": salesman.id, "role_name": salesman.name, "is_follower": salesman.is_follower})
    if sys_type_code in ["mch"]:
        salesman = uline_session.query(Role).filter(Role.sp_type == 3).one()
        role.append({"role_id": salesman.id, "role_name": salesman.name, "is_follower": salesman.is_follower})
    if sys_type_code in ["mr"]:
        if headquarters == 1:
            role = [role_ for role_ in role if role_["is_follower"] == 1]
            salesman = uline_session.query(Role).filter(Role.sp_type == 3).one()
            role.append({"role_id": salesman.id, "role_name": salesman.name, "is_follower": 1})
        elif headquarters == 2:
            role = [role_ for role_ in role if role_["is_follower"] == 0]
        else:
            salesman = uline_session.query(Role).filter(Role.sp_type == 3).one()
            role.append({"role_id": salesman.id, "role_name": salesman.name, "is_follower": 1})
            # 新增员工时前端分is_follower,1为员工,2为总部角色
    return role


def get_all_cs(employee_id):
    employee = get_employee_login(employee_id)
    query = uline_session.query(MchInletInfo.mch_shortname, MchInletInfo.mch_id).join(MchUser, MchUser.mch_id == MchInletInfo.mch_id).filter(
        MchInletInfo.cs_id == employee.sys_id, MchUser.status == 2).all()
    response = [dict(zip(['sys_name', 'sys_id'], list(x))) for x in query] if all(query) else []
    # response.append({"sys_name": "总部", "sys_id": employee.sys_id})
    return response


def query_role_name(role_id):
    names = uline_session.query(Role).filter(Role.id.in_(role_id)).all()
    name_str = ",".join([name.name for name in names])
    return name_str


@gen.coroutine
def get_access_token(rdb, refresh=False):
    access_token = rdb.get('access_token')
    if not refresh and access_token:
        raise gen.Return(access_token)
    res = yield AsyncHTTPClient().fetch(
        u"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
        .format(app_id, app_secret))
    res = json.loads(res.body)
    access_token = res['access_token']
    rdb.set('access_token', access_token, 7200)
    raise gen.Return(access_token)


def auth_wx_news_open(sys_type_code, employee_id):
    employee = get_employee_login(employee_id)
    if sys_type_code in ["mch"]:
        ret = uline_session.query(MchInletInfo.open_or_close).filter(MchInletInfo.mch_id == employee.sys_id).one()
    if sys_type_code in ["mr"]:
        ret = uline_session.query(DtInletInfo.chain_wechat_news).filter(DtInletInfo.dt_id == employee.sys_id).one()
    return ret


def auth_junior_id(junior_id, employee_id):
    junior_id = map(int, junior_id)
    all_cs = get_all_cs(employee_id)
    all_cs_id = [i["sys_id"] for i in all_cs] if all_cs else []
    cs_id_set = set(junior_id) - set(all_cs_id)
    msg = False if len(cs_id_set) != 0 else True
    return msg


def auth_employee_role(employee_role, sys_type_code, employee_id, headquarters):
    employee_role = map(int, employee_role)
    all_role_id = get_employee_all_role(employee_id, sys_type_code)
    if headquarters == 2:
        # 连锁商户权限
        role_id_list_chain = [i["role_id"] for i in all_role_id if i["is_follower"] == 0] if all(all_role_id) else []
        role_set = set(employee_role) - set(role_id_list_chain)
    elif headquarters == 1:
        # 门店权限
        role_id_list_cs = [i["role_id"] for i in all_role_id if i["is_follower"] == 1] if all(all_role_id) else []
        role_set = set(employee_role) - set(role_id_list_cs)
    else:
        role_id_list = [i["role_id"] for i in all_role_id] if all(all_role_id) else []
        role_set = set(employee_role) - set(role_id_list)

    msg = False if len(role_set) != 0 else True
    return msg


def get_old_employee_role(employee_id):

    employee_role = uline_session.query(EmployeeRolePermit).join(Role, Role.id == EmployeeRolePermit.role_id).filter(
        EmployeeRolePermit.employee_id == employee_id).all()
    return [int(role.role_id) for role in employee_role] if all(employee_role) else []


def get_headquarters(employee_id):

    employee_sys_type_id = uline_session.query(UnionEmployee).filter(UnionEmployee.employee_id == employee_id).first()
    sys_type_code = uline_session.query(SysType).filter(SysType.id == employee_sys_type_id.sys_type_id).one()
    if sys_type_code.code == "mr":
        headquarters = 2
    elif sys_type_code.code == "mch":
        headquarters = 1
    return headquarters


def get_modify_id_sys_code(employee_id):
    employee_login = get_employee_login(employee_id)
    sys_type_code = uline_session.query(SysType).filter(SysType.id == employee_login.sys_type_id).one()
    return sys_type_code.code
