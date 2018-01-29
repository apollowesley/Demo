#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from uline.model.uline.user import Employee
from uline.model.uline.other import SysType
from uline.model.uline.permit import Role, EmployeeRolePermit
from uline.public import log
from tornado.gen import coroutine, Return
from uline.model.uline.base import uline_session
from uline.model.uline.info import EmployeeUserLog, UserProfile
from sqlalchemy.sql import func


def generate_new_user_id():
    user_id = uline_session.query(func.max(Employee.id)).first()
    user_id = user_id[0] + 1 if user_id[0] else 10000000
    return user_id


@coroutine
def employee_profile(sys_type_code, sys_id, email, login_passwd, name, phone1=None, city=None, sex=None):
    try:
        status = 2
        if sys_type_code == "bk":
            status = 1
        creator_id = 0
        create_at = update_at = datetime.datetime.now()
        user_id = generate_new_user_id()
        sys_type_id = uline_session.query(SysType).filter(SysType.code == sys_type_code).one()
        new_user = UserProfile(
            id=user_id,
            name=name,
            city=city,
            phone1=phone1,
            email=email,
            sex=sex,
            status=status,
            creator_id=creator_id,
            create_at=create_at,
            update_at=update_at
        )
        login_employee = Employee(
            id=user_id,
            sys_id=sys_id,
            login_passwd=login_passwd,
            login_name=str(sys_id) + "." + sys_type_code,

            sys_type_id=sys_type_id.id,
            create_at=create_at,
            update_at=update_at,
            creator_id=creator_id,
            status=status,
            user_id=user_id

        )
        uline_session.add(new_user)
        uline_session.add(login_employee)
        uline_session.commit()

        assert sys_type_code in ["mr", "dt", "bk"]
        if sys_type_code == "bk":
            role_id = uline_session.query(Role.id).filter(
                Role.sys_type_id == sys_type_id.id, Role.sp_type == 1, Role.is_hq == 0).one()
        else:
            role_id = uline_session.query(Role.id)\
                .filter(Role.sys_type_id == sys_type_id.id, Role.sp_type == 1).one()

        employee_role = EmployeeRolePermit(employee_id=user_id, role_id=role_id[0])
        uline_session.add(employee_role)

        new_create_record = EmployeeUserLog(eutype=1,
                                            employee_id=user_id,
                                            comment="成功创建账号",
                                            operate_id=0,
                                            create_at=create_at)
        uline_session.add(new_create_record)
        uline_session.commit()
    except Exception as err:
        log.exception.exception(err)
