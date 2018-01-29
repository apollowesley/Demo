#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import json
import functools
import types
import re
from datetime import datetime
from sqlalchemy import distinct
from uline.model.uline.info import EmployeeUserLog
from uline.model.uline.base import uline_session
from uline.model.uline.user import Employee
from uline.model.uline.other import SysType
from uline.model.uline.permit import (EmployeeRolePermit,
                                      Role, RolePermit, Permit)
from uline.settings import env

from sqlalchemy import func


def delete_role(dbsession, role_id, operate_id):
    """
    删除一个角色
    :param dbsession: uline_session实例(使用多线程应使用同一个实例)
    :param role_id: 角色ID
    :return: True/False, message
    """
    role = dbsession.query(Role).filter(Role.id == role_id).first()

    if not role:
        return False, "角色不存在"
    delete_employee_role = dbsession.query(EmployeeRolePermit).filter(EmployeeRolePermit.role_id == role_id)
    if delete_employee_role.all():
        role_name = role.name
        dbsession.execute(EmployeeUserLog.__table__.insert(),
                          [{'employee_id': role_.employee_id,
                            'comment': "去除" + role_name + "角色",
                            'eutype': 1,
                            'create_at': datetime.now(),
                            'operate_id': operate_id} for role_ in delete_employee_role])

        delete_employee_role.delete(synchronize_session=False)
    dbsession.delete(role)
    dbsession.commit()
    return True, "删除成功"


def update_role(dbsession, name, role_id, update_permits, sys_id, sys_type_id,
                sys_type_code, employee_id):
    """
    更新一个角色
    :param dbsession: uline_session实例(使用多线程应使用同一个实例)
    :param name: 角色名称
    :param role_id: 角色ID
    :return: True/False, message
    """
    if not name:
        return False, "角色名不能为空"

    role = dbsession.query(Role).filter(Role.id == role_id).first()

    if not role:
        return False, "角色不存在"

    if not role.name == name:
        role_exist = dbsession.query(Role.id).filter(
            Role.sys_type_id == sys_type_id,
            Role.sys_id == sys_id,
            Role.name == name
        ).first()

        if role_exist:
            return False, "角色名已存在"

    # 更新权限
    permits_status = set_role_permits(role.id, update_permits, sys_id, sys_type_id,
                                      sys_type_code, employee_id, dbsession)

    if permits_status:
        if role.name != name:
            role.name = name
            dbsession.commit()
        return True, "更新成功"

    return False, "更新失败，请重试"


def get_role(dbsession, sys_type_id, sys_id, get_type, page_index, page_size):
    """
    查询角色
    :param dbsession: uline_session实例(使用多线程应使用同一个实例)
    :param sys_type_id: 平台类型ID
    :param sys_id: 平台ID
    :param get_type: one:查询一个, more:分页查询, all:查询全部
    :param page_index: 当前页
    :param page_size: 查询总数
    :return: list 查询结果
    """

    models = []
    page_index = int(page_index)
    page_size = int(page_size)
    query_data = (Role.id, Role.name, Role.create_at, Role.sp_type, Role.is_follower)
    filter_data = (Role.sys_type_id == sys_type_id, Role.sys_id == sys_id)
    counts = dbsession.query(Role.id).filter(*filter_data).count()
    if get_type == "more":
        offset = (page_index - 1) * page_size
        models = dbsession.query(*query_data).filter(*filter_data) \
            .order_by(Role.create_at.desc()).offset(offset).limit(page_size).all()
    elif get_type == "all":
        models = dbsession.query(*query_data).filter(*filter_data) \
            .order_by(Role.create_at.desc()).all()
    else:
        models = dbsession.query(*query_data).filter(*filter_data) \
            .order_by(Role.create_at.desc()).first()

    sys_type_code = uline_session.query(SysType).filter(SysType.id == sys_type_id).one()
    if sys_type_code.code == "dt":
        build_in_role = uline_session.query(*query_data).filter(Role.sp_type == 2).first()
        models.insert(0, build_in_role)
    if sys_type_code.code in ["mch", "mr"]:
        build_in_role = uline_session.query(*query_data).filter(Role.sp_type == 3).first()
        models.insert(0, build_in_role)
    map_keys = ['role_id', 'role_name', 'create_at', 'sp_type', 'is_follower']
    result_dicts = [dict(zip(map_keys, d)) for d in models]
    for r in result_dicts:
        r['create_at'] = r['create_at'].strftime('%Y-%m-%d %H:%M:%S')
    return counts, result_dicts


def add_role(dbsession, name, sys_type_id, sys_id, sys_type_code, employee_id, update_permits, sp_type=0, is_follower=0,
             is_hq=1):
    """
    添加一个角色
    :param dbsession: uline_session实例(使用多线程应使用同一个实例)
    :param name: 角色名称
    :param sys_type_id: 平台类型ID
    :param sys_id: 平台ID
    :param is_hq: 是否是直营用户 0: 不是 1: 是
    :return: True/False, message
    """
    if not name:
        return False, "角色名不能为空"

    role = dbsession.query(Role.id).filter(
        Role.sys_type_id == sys_type_id,
        Role.sys_id == sys_id,
        Role.name == name
    ).first()

    if role:
        return False, "角色名已存在"

    dbsession.query()

    # 不能设置为管理员或者是boss
    if sp_type in ('255', '1'):
        return False, "权限超出范围"

    role = Role()
    role.name = name
    role.sys_id = sys_id
    role.sys_type_id = sys_type_id
    role.is_admin = 0
    role.is_boss = 0
    role.is_hq = is_hq
    role.is_follower = is_follower
    role.sp_type = sp_type

    dbsession.add(role)
    dbsession.commit()

    if role.id is not None:
        # 添加权限
        permits_status = set_role_permits(role.id, update_permits, sys_id, sys_type_id,
                                          sys_type_code, employee_id, dbsession)
        if permits_status:
            return True, "添加成功"

    # 权限添加失败，删除刚才添加的角色ID
    delete_role(dbsession, role.id, employee_id)
    return False, "添加失败，请重试"


def get_platform_permits(sys_id, sys_type_id, dbsession):
    '''
    获取某个平台用户的所有权限
    '''
    if not sys_id or not sys_type_id:
        return []
    map_key = ["id", "model_name", "model_url", "sys_type_id"]
    sub_query = dbsession.query(EmployeeRolePermit.role_id).join(
        Role, Role.id == EmployeeRolePermit.role_id).join(
        Employee, Employee.id == EmployeeRolePermit.employee_id).filter(
        Employee.sys_id == sys_id, Role.sp_type == 1,
        Role.sys_type_id == sys_type_id)

    query = dbsession.query(
        RolePermit.permit_id, Permit.model_name,
        Permit.model_url, Permit.sys_type_id).join(
        Permit, Permit.id == RolePermit.permit_id).filter(
        RolePermit.role_id.in_(sub_query),
        Permit.status == 1).order_by(Permit.model_url).distinct()

    return [dict(zip(map_key, row)) for row in query]


def get_platform_role_permits(role_id, sys_id, sys_type_id, dbsession,
                              maps=None):
    '''
    获取该平台用户的某个角色对应的所有权限
    Parameters:
        role_id: 角色id
        sys_id: 平台用户id
        sys_type_id: 所属平台id
    '''
    if not sys_id or not sys_type_id:
        return []
    map_key = ["id", "model_name", "model_url", "sys_type_id"]
    role_key = ["id", "is_follower", "is_hq", "sp_type", "sys_type_id", "sys_id"]
    sub_query = dbsession.query(
        Role.id, Role.is_follower, Role.is_hq, Role.sp_type,
        Role.sys_type_id, Role.sys_id).filter(
        Role.id == role_id).first()
    # 因为角色可能存在但没有权限,分两次查询数据库避免使用left join
    if not sub_query:
        return False, [], {}
    role_map = dict(zip(role_key, sub_query))
    if role_map["sp_type"] == 0 and (role_map["sys_type_id"] != sys_type_id or role_map["sys_id"] != sys_id):
        return False, [], {}
    query = dbsession.query(
        RolePermit.permit_id, Permit.model_name,
        Permit.model_url, Permit.sys_type_id).join(
        Permit, Permit.id == RolePermit.permit_id).filter(
        RolePermit.role_id == role_id,
        Permit.status == 1).order_by(Permit.model_url).distinct()

    return True, [dict(zip(map_key, row)) for row in query], role_map


def get_user_permits(employee_id, sys_type_id, dbsession):
    '''
    获取登录员工的在某个平台所有权限
    Parameters:
        employee_id: 员工id
        sys_type_id: 所属平台id
    '''
    if not employee_id or not sys_type_id:
        return []

    map_key = ["id", "model_name", "model_url", "sys_type_id"]

    query = dbsession.query(
        RolePermit.permit_id, Permit.model_name,
        Permit.model_url, Permit.sys_type_id).join(
        Permit, Permit.id == RolePermit.permit_id).join(
        EmployeeRolePermit, EmployeeRolePermit.role_id == RolePermit.role_id).filter(
        Permit.status == 1, Permit.sys_type_id == sys_type_id,
        EmployeeRolePermit.employee_id == employee_id).order_by(Permit.model_url).distinct()

    return [dict(zip(map_key, row)) for row in query]


def get_mr_sub_mch_permits(dbsession):
    '''
    连锁商户可以给门店设置角色,当角色is_fllower=1的时候需要给角色赋值商户平台的权限
    赋值的角色权限在数据库中sp_type=4 sys_type_code="mch"
    '''
    map_key = ["id", "model_name", "model_url"]
    sub_query = dbsession.query(SysType.id).filter(SysType.code == "mch")
    query = dbsession.query(
        RolePermit.permit_id, Permit.model_name,
        Permit.model_url).join(
        Permit, Permit.id == RolePermit.permit_id).join(
        Role, Role.id == RolePermit.role_id).filter(
        Role.sp_type == 4, Role.sys_type_id == sub_query,
        Permit.status == 1).order_by(Permit.model_url).distinct()

    return [dict(zip(map_key, row)) for row in query]


def set_role_permits(role_id, update_permits, sys_id, sys_type_id,
                     sys_type_code, employee_id, dbsession):
    '''
    给角色添加/回收权限
    Parameters:
        role_id: 角色id
        update_permits: 激活的权限集合
        sys_id: 平台用户id
        sys_type_id: 平台类型id
        sys_type_code: 平台类型code
        employee_id: 员工id
        dbsession: uline_session实例(使用多线程应使用同一个实例)
    Returns:
        True: 成功
        False: 角色或权限不在许可权限范围内
    Raises:
        TypeError: update_permits类型不对
    '''
    if isinstance(update_permits, (list, set)):
        update_permits = set(update_permits)
    else:
        raise TypeError("update_permits must be list or set")

    flag, role_permits, role_info = get_platform_role_permits(
        role_id, sys_id, sys_type_id, dbsession)
    # 只可修改本身创建的员工
    if not flag or (role_info["sys_type_id"] != sys_type_id and role_info["sys_id"] != sys_id):
        return False

    role_permits = {i["id"] for i in role_permits}
    # 连锁商户角色跨平台需特殊处理
    if sys_type_code == "mr" and role_info["is_follower"]:
        platform_permits = get_mr_sub_mch_permits(dbsession)
    else:
        platform_permits = get_platform_permits(sys_id, sys_type_id, dbsession)

    platform_permits = {i["id"] for i in platform_permits}
    # 把添加和回收的权限集合求出来
    active_permits = update_permits - role_permits
    inactive_permits = role_permits - update_permits
    # 添加的权限不能超出平台用户的权限
    if active_permits - platform_permits:
        return False
    # 写入新添的权限
    if active_permits:
        active_objs = []
        for i in active_permits:
            active_objs.append(
                RolePermit(role_id=role_id, permit_id=i)
            )
        dbsession.bulk_save_objects(active_objs)
    # 删除回收的权限
    if inactive_permits:
        dbsession.query(RolePermit).filter(
            RolePermit.role_id == role_id,
            RolePermit.permit_id.in_(list(inactive_permits))).delete(
            synchronize_session=False)
    dbsession.commit()
    return True


def _get_user_all_permits(employee_id, dbsession):
    '''
    获取登录员工的所有权限(不分平台)
    '''
    if not employee_id:
        return {}

    sub_query = dbsession.query(
        EmployeeRolePermit.role_id, Role.sp_type, Role.sys_type_id).join(
        Role, Role.id == EmployeeRolePermit.role_id).filter(
        EmployeeRolePermit.employee_id == employee_id)

    permits = {}
    sp_types = set()  # 存储角色类型
    role_ids = []
    for row in sub_query:
        sp_types.add(row[1])
        role_ids.append(row[0])
        if row[2] not in permits:
            permits[row[2]] = {}
            permits[row[2]]["is_boss"] = False
            permits[row[2]]["model_url"] = []
        if row[1] == 255:
            permits[row[2]]["is_boss"] = True

    if not permits:
        return {}, sp_types
    query = dbsession.query(
        RolePermit.role_id, Permit.model_url, Permit.sys_type_id).join(
        Permit, Permit.id == RolePermit.permit_id).filter(
        RolePermit.role_id.in_(role_ids), Permit.status == 1).distinct()

    for row in query:
        if row[2] in permits:
            permits[row[2]]["model_url"].append(row[1])
        else:
            # 特殊处理连锁商户
            permits[row[2]] = {}
            permits[row[2]]["is_boss"] = False
            permits[row[2]]["model_url"] = []
            permits[row[2]]["model_url"].append(row[1])

    return permits, sp_types


def _no_permission(handler, permits=None, sp_types=None):
    '''
    兼容前后端分离
    当前后端分离全部完成之后 需要删除此方法，权限统一返回状态码
    '''
    if handler.request.headers.get("Platform") in ["mch"]:
        handler.write(json.dumps(
            {'code': 10005, 'msg': u"无此接口权限"},
            ensure_ascii=False))
        handler.finish()
    else:
        if handler.request.headers.get("X-Requested-With"):
            handler.write(json.dumps(
                {'code': 10005, 'msg': u"无此接口权限"},
                ensure_ascii=False))
            handler.finish()
        else:
            if permits is None and sp_types is None:
                handler.redirect("/account/")
                return
            if not permits and 2 in sp_types:
                handler.redirect("/account/no_role?p=sm")
            # 以下判断跟is None不一样
            elif not permits:
                handler.redirect("/account/no_role")

            handler.redirect("/account/")


def check_permission(request):
    '''
    用于验证登录用户是否有请求接口的访问权限
    '''

    def inline_func(func):
        @functools.wraps(func)
        def _wrap(self, *args, **kwargs):
            paths = request_path if request_path else self.request.path
            if not isinstance(paths, (tuple, list)):
                paths = [paths]

            for i, path in enumerate(paths):
                path = path if path.startswith("/") else ("/" + path)
                # 当前5个后台独立,添加前缀
                re_match = re.match(r"(/dist|/official|/merchant|/bank|/inter_bank|/chain)", path)
                if re_match:
                    uri_prefix = re_match.group(0)
                    path = path[len(uri_prefix):]
                paths[i] = path

            sti = self.session.get("sys_type_id", "")
            if isinstance(sti, str) and not sti.isdigit():
                _no_permission(self)
                return

            sti = int(sti)
            permits, sp_types = _get_user_all_permits(self.session.get("employee_id"), self.udbsession)
            if not permits or sti not in permits:
                _no_permission(self, permits, sp_types)
                return

            if not permits[sti]["model_url"]:
                _no_permission(self, {}, sp_types)
                return

            for path in paths:
                if path in ("/", ""):
                    return func(self, *args, **kwargs)

                for url in permits[sti]["model_url"]:
                    if path.startswith(url):
                        return func(self, *args, **kwargs)

            if permits[sti]["is_boss"]:
                return func(self, *args, **kwargs)

            _no_permission(self)
            return

        return _wrap

    if isinstance(request, types.FunctionType):
        request_path = None
        return inline_func(request)
    request_path = request
    return inline_func


def permit_compatibility_platform(sys_type_code, permits):
    '''
    同时兼容招行和浦发页面,根据不同的银行返回不同的权限
    :param sys_type_code: 平台简称
    :param permits: 权限列表字典
    :return: permits(权限列表字典)
    '''
    result = []
    if sys_type_code == 'ibk':
        for row in permits:
            if row['model_url'] not in ('/recon/refund', '/recon/transaction',
                                        '/common/downloads_bill', '/capital/mch', '/subsidize/mch'):
                result.append(row)
    elif sys_type_code == 'bk':
        for row in permits:
            if env == 'CMBC_PROD':
                if row['model_url'] not in ('/inlet/inter_bank',):
                    result.append(row)
            else:
                if row['model_url'] not in ('/subsidize/mch',):
                    result.append(row)
    elif sys_type_code == 'ub':
        for row in permits:
            if env == 'CMBC_PROD':
                if row['model_url'] not in ('/inlet/inter_bank',):
                    result.append(row)
            else:
                if row['model_url'] not in ('/subsidize/mch',):
                    result.append(row)
    else:
        result = permits

    return result
