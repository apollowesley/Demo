#!/usr/bin/env python
# -*- coding:utf-8 -*-
from uline.model.uline.base import uline_session
from uline.model.uline.user import Employee, UnionEmployee, BkUser,\
    DtUser, UbUser, MchUser, MchUserMchSubUser, MchSubUser, DtSubUser
from uline.model.uline.info import EmployeeUserLog, MchInletInfo, DtInletInfo, UserProfile
from uline.model.uline.other import SysType
from sqlalchemy.sql import func
import datetime
from uline.public.db import initdb
import logging
import os
from uline.settings import DEFAULT_BANK_ID

import time
from uline.model.uline.permit import EmployeeRolePermit, Role, RolePermit, Permit

logger = logging.getLogger('employee')
file_path = os.path.dirname(__file__)
logger.setLevel(logging.DEBUG)
log_path = os.path.join(file_path, "log/uline_employee.log")
# if not os.path.isfile(log_path):
#     f = open(log_path, "wb")
#     f.close()
filelog = logging.FileHandler(log_path)
streamhandler = logging.StreamHandler()
streamhandler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
filelog.setFormatter(formatter)
streamhandler.setFormatter(formatter)

logger.addHandler(filelog)
# logger.addHandler(streamhandler)
logger.info('uline_employee')


def generate_new_user_id():
    user_id = uline_session.query(func.max(Employee.id)).first()
    user_id = user_id[0] + 1 if user_id[0] else 10000000
    return user_id


def update_employee_role(user_id, role_id):
    employee_role = EmployeeRolePermit(employee_id=user_id, role_id=role_id)
    uline_session.add(employee_role)


def migrate_mch_data():
    mchs = uline_session.query(MchUser.mch_id, MchUser.mch_name, MchUser.email,
                               MchUser.password, MchUser.status, MchInletInfo.mobile,
                               MchInletInfo.city, MchUser.create_at, MchUser.update_at, MchInletInfo.cs_id).join(MchInletInfo, MchInletInfo.mch_id == MchUser.mch_id).all()
    mch_sys_id = uline_session.query(SysType).filter(SysType.code == "mch").first()
    role_id = uline_session.query(Role).filter(Role.sp_type == 1, Role.sys_type_id == mch_sys_id.id).first()
    user_id = generate_new_user_id()

    deal_mch = []
    for mch in mchs:
        mch_list = list(mch)
        mch_list[4] = 1 if mch_list[4] == 2 else 2
        if mch_list[9] is not None:
            mch_list[4] = 2
        mch_list.append(user_id)
        user_id += 1
        deal_mch.append(mch_list)

    for i in range(1, 50):
        single_mchs = deal_mch[(i - 1) * 10000:i * 10000]
        if not single_mchs:
            break
        uline_session.execute(UserProfile.__table__.insert(),
                              [{'id': mch[10],
                                'name':mch[1],
                                'city':mch[6],
                                'status':mch[4],
                                'email':mch[2],
                                'phone1':mch[5],
                                'creator_id':0,
                                'create_at':mch[7],
                                'update_at':mch[8]} for mch in single_mchs])
        uline_session.commit()

        uline_session.execute(Employee.__table__.insert(),
                              [{'id': mch[10],
                                'sys_type_id':mch_sys_id.id,
                                'sys_id':mch[0],
                                'login_name':"".join([str(mch[0]), ".mch"]),
                                'login_passwd':mch[3],
                                'user_id':mch[10],
                                'status':mch[4],
                                'creator_id':0,
                                'create_at':mch[7],
                                'update_at':mch[8]} for mch in single_mchs])
        uline_session.commit()

        uline_session.execute(EmployeeRolePermit.__table__.insert(),
                              [{'employee_id': mch[10],
                                'role_id':role_id.id
                                } for mch in single_mchs if mch[9] is None])
        uline_session.commit()

    return


def sys_update():

    records = [{"name": "商户", "code": "mch", "perfix_code": ".mch"},
               {"name": "连锁商", "code": "mr", "perfix_code": ".mr"},
               {"name": "渠道商", "code": "dt", "perfix_code": ".dt"},
               {"name": "银行", "code": "bk", "perfix_code": ".bk"},
               {"name": "官方", "code": "ub", "perfix_code": ".ulaiber"}, ]
    data = 0
    for new_record in records:
        try:
            _record = SysType(
                name=new_record["name"],
                code=new_record["code"],
                perfix_code=new_record["perfix_code"],
                create_at=datetime.datetime.now(),
                update_at=datetime.datetime.now()
            )
            uline_session.add(_record)
            uline_session.commit()
            data += 1
            logger.info("{}平台类型已写入平台信息表".format(new_record["name"]))
        except Exception as err:
            logger.debug("{}平台类型已写入信息出现错误{}".format(new_record["name"], err))
            continue
            # pass
    logger.debug("平台信息共写入{}条信息".format(data))

    return


def migrate_dt_data():
    dts = uline_session.query(DtUser.dt_id, DtUser.dt_name, DtUser.email,
                              DtUser.password, DtUser.status,
                              DtInletInfo.mobile, DtInletInfo.city,
                              DtUser.create_at, DtUser.update_at, DtInletInfo.parent_id).join(DtInletInfo,
                                                                                              DtInletInfo.dt_id == DtUser.dt_id).all()
    data = 0
    dt_sys_id = uline_session.query(SysType.id).filter(SysType.code == "dt").first()
    mr_sys_id = uline_session.query(SysType.id).filter(SysType.code == "mr").first()
    dt_role_id = uline_session.query(Role).filter(Role.sp_type == 1, Role.sys_type_id == dt_sys_id[0]).first()
    mr_role_id = uline_session.query(Role).filter(Role.sp_type == 1, Role.sys_type_id == mr_sys_id[0]).first()
    user_id = generate_new_user_id()

    for dt in dts:
        try:
            status = 1 if dt[4] == 2 else 2
            new_user = UserProfile(id=user_id,
                                   name=dt[1],
                                   city=dt[6],
                                   status=status,
                                   email=dt[2],
                                   phone1=dt[5],
                                   creator_id=0,
                                   create_at=dt[7],
                                   update_at=dt[8])

            sys_type_id = dt_sys_id[0] if not dt[9] else mr_sys_id[0]

            login_name = "".join([str(dt[0]), ".dt"]) if not dt[9] else "".join([str(dt[0]), ".mr"])
            new_employee_login = Employee(id=user_id,
                                          sys_type_id=sys_type_id,
                                          sys_id=dt[0],
                                          login_name=login_name, login_passwd=dt[3], user_id=user_id, status=status,
                                          creator_id=0, create_at=dt[7], update_at=dt[8])

            uline_session.add(new_user)
            uline_session.add(new_employee_login)
            uline_session.commit()

            role_id = dt_role_id if not dt[9] else mr_role_id
            update_employee_role(user_id, role_id.id)

            uline_session.commit()
            data += 1
            user_id += 1
            logger.info("渠道商管理员{}信息已成功创建".format(dt[0]))
        except Exception as err:
            logger.info("渠道商管理员{}信息创建失败{}".format(dt[0], err))
            continue
    logger.debug("渠道商管理员用户共写入{}条信息".format(data))

    pass


def migrate_bk_data():

    bks = uline_session.query(BkUser).all()
    bk_sys_id = uline_session.query(SysType).filter(SysType.code == "bk").first()
    main_bk_role_id = uline_session.query(Role).filter(Role.sp_type == 1, Role.sys_type_id == bk_sys_id.id).first()
    inter_bk_role_id = uline_session.query(Role).filter(
        Role.sp_type == 1, Role.sys_type_id == bk_sys_id.id, Role.is_hq == 0).first()

    main_bk = [bk for bk in bks if bk.bk_id == DEFAULT_BANK_ID][0]
    main_user_id = generate_new_user_id()
    status = 1
    new_user = UserProfile(id=main_user_id, name=main_bk.bk_name, status=status, email=main_bk.email, creator_id=0,
                           create_at=main_bk.create_at, update_at=main_bk.update_at)

    id_employee_login = Employee(id=main_user_id, sys_type_id=bk_sys_id.id, sys_id=main_bk.bk_id,
                                 login_name="".join([str(main_bk.bk_id), ".bk"]), login_passwd=main_bk.password,
                                 user_id=main_user_id, status=status, creator_id=0, create_at=main_bk.create_at,
                                 update_at=main_bk.update_at)

    uline_session.add(new_user)
    uline_session.add(id_employee_login)
    uline_session.commit()
    update_employee_role(main_user_id, main_bk_role_id.id)
    uline_session.commit()
    logger.info("银行管理员id登录账号{}信息已成功创建".format(main_bk.bk_id))

    # 更新银行,使用id.bk登录
    data = 0
    user_id = generate_new_user_id()
    for bk in bks:
        try:
            if bk.bk_type == 2:
                new_user = UserProfile(id=user_id, name=bk.bk_name, status=status, email=bk.email,
                                       creator_id=0, create_at=bk.create_at, update_at=bk.update_at)

                new_employee_login = Employee(id=user_id, sys_type_id=bk_sys_id.id, sys_id=bk.bk_id,
                                              login_name="".join([str(bk.bk_id), ".bk"]), login_passwd=bk.password, user_id=user_id, status=status,
                                              creator_id=0, create_at=bk.create_at, update_at=bk.update_at)

                uline_session.add(new_user)
                uline_session.add(new_employee_login)
                uline_session.commit()
                update_employee_role(user_id, inter_bk_role_id.id)
                uline_session.commit()
                data += 1
                logger.info("银行管理员id登录账号{}信息已成功创建".format(bk.bk_id))

            else:
                if bk.bk_id != DEFAULT_BANK_ID:
                    new_user = UserProfile(id=user_id, name=bk.bk_name, status=status, email=bk.email, creator_id=main_user_id,
                                           create_at=bk.create_at, update_at=bk.update_at)

                    login_name_ = bk.email.split("@")[0] + "@bk"
                    id_employee_login = Employee(id=user_id,
                                                 sys_type_id=bk_sys_id.id,
                                                 sys_id=main_bk.bk_id,
                                                 login_name=login_name_,
                                                 login_passwd=bk.password,
                                                 user_id=user_id,
                                                 status=status,
                                                 creator_id=main_user_id,
                                                 create_at=bk.create_at,
                                                 update_at=bk.update_at)

                    uline_session.add(new_user)
                    uline_session.add(id_employee_login)
                    uline_session.commit()
                    data += 1
                    logger.info("银行管理员id登录账号{}信息已成功创建".format(bk.bk_id))
            user_id += 1
        except Exception as err:
            logger.info("银行管理员id登录账号{}信息创建失败{}".format(bk.bk_id, err))
            continue

    logger.debug("银行管理员用户共写入{}条信息".format(data))
    pass


def migrate_official_data():
    try:
        ub = uline_session.query(UbUser).filter(UbUser.email == "ulaiber@ulaiber.com").one()
        ub_sys_id = uline_session.query(SysType.id).filter(SysType.code == "ub").first()
        ub_role_id = uline_session.query(Role).filter(Role.sp_type == 1, Role.sys_type_id == ub_sys_id[0]).first()

        # 更新官方,使用id.bk登录
        user_id = generate_new_user_id()
        status = 1
        new_user = UserProfile(id=user_id, name=ub.ub_name, status=status, email=ub.email, creator_id=0,
                               create_at=ub.create_at, update_at=ub.update_at)

        new_main_ub_login = Employee(id=user_id, sys_type_id=ub_sys_id[0],
                                     sys_id=ub.ub_id, login_name=ub.email,
                                     login_passwd=ub.password, user_id=user_id,
                                     status=status, creator_id=0, create_at=ub.create_at, update_at=ub.update_at)
        uline_session.add(new_user)
        uline_session.add(new_main_ub_login)
        uline_session.commit()

        update_employee_role(user_id, ub_role_id.id)
        uline_session.commit()
        logger.info("官方用户ulaiber@ulaiber.com信息已成功创建")
    except Exception as err:
        logger.info("官方用户ulaiber@ulaiber.com信息创建失败{}".format(err))
    pass


def migrate_mch_employee_data():

    mch_employee = uline_session.query(MchUserMchSubUser.mch_sub_id, MchUserMchSubUser.mch_id,
                                       MchSubUser.status, MchSubUser.password,
                                       MchSubUser.email, MchSubUser.phone,
                                       MchSubUser.login_name, MchSubUser.mch_sub_name,
                                       MchSubUser.create_at, MchSubUser.update_at, MchUserMchSubUser.dt_id,
                                       MchSubUser.wx_id, MchSubUser.wx_open_id).\
        join(MchSubUser, MchSubUser.mch_sub_id == MchUserMchSubUser.mch_sub_id).all()

    mch_employee_single = []
    mch_sub_id = []
    operate_name = []
    for employee in mch_employee:
        if employee[0] not in mch_sub_id:
            mch_sub_id.append(employee[0])
            mch_employee_single.append(employee)
            login_name = "".join([str(employee[1]), ".mch"]) if not employee[10] else "".join(
                [str(employee[10]), ".mr"])
            operate_name.append(login_name)

    operate_id = uline_session.query(Employee).filter(Employee.login_name.in_(tuple(operate_name))).all()

    operate_ = {str(employee.sys_id): employee.id for employee in operate_id}
    mch_sys_id = uline_session.query(SysType.id).filter(SysType.code == "mch").first()
    mr_sys_id = uline_session.query(SysType.id).filter(SysType.code == "mr").first()

    data = 0
    employee_role_id = uline_session.query(Role).filter(Role.sp_type == 3, Role.sys_type_id == mch_sys_id[0]).first()
    user_id = generate_new_user_id()

    for mch in mch_employee_single:
        try:
            creator_id = operate_[str(mch[1])] if not mch[10] else operate_[str(mch[10])]
            new_user = UserProfile(
                id=user_id,
                name=mch[7],
                status=mch[2],
                email=mch[4],
                phone1=mch[5],
                creator_id=creator_id,
                create_at=mch[8],
                update_at=mch[9],
                wx_id=mch[11],
                wx_open_id=mch[12]
            )

            sys_type_id = mch_sys_id[0] if not mch[10] else mr_sys_id[0]
            login_name = "".join([str(mch[6]), ".mch"]) if not mch[10] else "".join([str(mch[6]), ".mr"])

            new_employee_login = Employee(
                id=user_id,
                sys_type_id=sys_type_id,
                sys_id=mch[1] if not mch[10] else mch[10],
                login_name=login_name,
                login_passwd=mch[3],
                user_id=user_id,
                status=mch[2],
                creator_id=creator_id,
                create_at=mch[8],
                update_at=mch[9]
            )

            uline_session.add(new_user)
            # uline_session.commit()

            uline_session.add(new_employee_login)
            # uline_session.commit()

            new_create_record = EmployeeUserLog(eutype=1, employee_id=user_id, comment="成功创建账号",
                                                operate_id=creator_id, create_at=datetime.datetime.now())
            uline_session.add(new_create_record)
            update_employee_role(user_id, employee_role_id.id)

            uline_session.query(MchUserMchSubUser).filter(MchUserMchSubUser.mch_sub_id ==
                                                          mch[0]).update({'new_employee_id': user_id})
            logger.info("普通商户员工{}信息已成功创建".format(login_name))
            data += 1
            user_id += 1
            uline_session.commit()
        except Exception as err:
            logger.info("普通商户员工{}信息创建失败{}".format(login_name, err))
            continue
    logger.debug("商户员工用户共写入{}条信息".format(data))
    pass


def migrate_employee_cs_data():
    mch_sys_id = uline_session.query(SysType.id).filter(SysType.code == "mch").first()
    m_data = uline_session.query(MchUserMchSubUser).filter(MchUserMchSubUser.dt_id != None).all()
    data = 0

    for _data in m_data:
        try:
            insert_ = UnionEmployee(
                employee_id=_data.new_employee_id,
                sys_type_id=mch_sys_id[0],
                sys_id=_data.mch_id,
                create_at=datetime.datetime.now()
            )
            uline_session.add(insert_)
            uline_session.commit()
            logger.info("普通商户员工{}信息创建成功".format(_data.mch_id))
            data += 1
        except Exception as err:
            logger.info("普通商户员工{}信息创建失败{}".format(_data.mch_id, err))
            continue
    logger.debug("商户员工和门店信息共写入{}条信息".format(data))

    pass


def migrate_dt_employee_data():
    dt_employee = uline_session.query(DtSubUser).all()
    data = 0
    dt_sys_id = uline_session.query(SysType.id).filter(SysType.code == "dt").first()
    dt_role_id = uline_session.query(Role).filter(Role.sp_type == 2, Role.sys_type_id == dt_sys_id[0]).first()

    for dt in dt_employee:
        try:
            user_id = dt.dt_sub_id
            new_user = UserProfile(
                id=user_id, name=dt.dt_sub_name, status=2, email=dt.email, phone1=dt.phone,
                creator_id=dt.dt_user_dt_id, create_at=dt.create_at, update_at=dt.update_at
            )
            mch_sys_id = uline_session.query(SysType.id).filter(SysType.code == "dt").first()
            login_name = "".join([dt.login_name, ".dt"])
            new_employee_login = Employee(
                id=user_id,
                sys_type_id=mch_sys_id[0],
                sys_id=dt.dt_user_dt_id,
                login_name=login_name, login_passwd=dt.password,
                user_id=user_id,
                status=2, creator_id=dt.dt_user_dt_id, create_at=dt.create_at,
                update_at=dt.update_at
            )

            uline_session.add(new_user)
            # uline_session.commit()

            uline_session.add(new_employee_login)

            new_create_record = EmployeeUserLog(eutype=1, employee_id=user_id, comment="成功创建账号信息",
                                                operate_id=0, create_at=datetime.datetime.now())
            uline_session.add(new_create_record)

            update_employee_role(user_id, dt_role_id.id)
            uline_session.commit()
            data += 1
            logger.info("渠道商用户信息{}已成功创建".format(user_id))
        except Exception as err:
            logger.info("渠道商用户信息{}创建失败{}".format(user_id, err))
            continue
    logger.debug("渠道商员工信息共写入{}条信息".format(data))

    pass


def role_update():
    '''
    添加系统默认角色
    '''

    dbsession = uline_session()
    sys_query = dbsession.query(SysType).all()
    sys_map = {}
    # 提取平台id
    for row in sys_query:
        sys_map[row.code] = row.id

    records = [
        # 默认is_admin 各个平台的默认角色
        {"name": "商户", "code": "mch", "is_admin": 1, "sp_type": 1},
        {"name": "渠道商", "code": "dt", "is_admin": 1, "sp_type": 1},
        {"name": "官方", "code": "ub", "is_admin": 1, "sp_type": 1},
        {"name": "连锁商", "code": "mr", "is_admin": 1, "sp_type": 1},
        {"name": "银行", "code": "bk", "is_admin": 1, "sp_type": 1},
        {"name": "同业银行", "code": "bk", "is_admin": 1, "sp_type": 1, "is_hq": 0},

        # 特殊内置角色
        {"name": "业务员", "code": "dt", "is_admin": 0, "sp_type": 2},
        {"name": "收银员", "code": "mch", "is_admin": 0, "sp_type": 3, "is_follower": 1},
        {"name": "连锁门店管理员", "code": "mch", "is_admin": 0, "sp_type": 4},



        # 默认is_boss 各个平台的超级管理员
        {"name": "商户-超级管理员", "code": "mch", "is_boss": 1, "sp_type": 255},
        {"name": "渠道商-超级管理员", "code": "dt", "is_boss": 1, "sp_type": 255},
        {"name": "官方-超级管理员", "code": "ub", "is_boss": 1, "sp_type": 255},
        {"name": "连锁商-超级管理员", "code": "mr", "is_boss": 1, "sp_type": 255},
        {"name": "银行-超级管理员", "code": "bk", "is_boss": 1, "sp_type": 255},
        {"name": "同业银行-超级管理员", "code": "bk", "is_boss": 1, "sp_type": 255, "is_hq": 0}
    ]
    data = 0
    for new_record in records:
        try:
            cnow = datetime.datetime.now()
            _record = Role(
                name=new_record["name"],
                sys_type_id=sys_map[new_record["code"]],
                is_hq=new_record.get("is_hq", 1),
                is_boss=new_record.get("is_boss", 0),
                is_admin=new_record.get("is_admin", 0),
                sp_type=new_record.get("sp_type", 0),
                is_follower=new_record.get("is_follower", 0),
                sys_id=0,
                create_at=cnow,
                update_at=cnow
            )
            uline_session.add(_record)
            uline_session.commit()
            data += 1
            logger.info("{}默认角色已写入角色信息表".format(new_record["name"]))
        except Exception as err:
            logger.info("{}默认角色写入信息出现错误{}".format(new_record["name"], err))
            continue
            # pass
    logger.debug("管理员角色信息共写入{}条信息".format(data))

    return


def permit_update():
    '''
    添加各个平台所需权限
    '''

    dbsession = uline_session()
    sys_query = dbsession.query(SysType).all()
    sys_map = {}
    # 提取平台id
    for row in sys_query:
        sys_map[row.code] = row.id

    records = [
        # 渠道商权限
        {"code": "dt", "model_url": "/inlet/dt", "name": "渠道商-渠道进件", "model_name": "渠道进件"},
        {"code": "dt", "model_url": "/inlet/mch", "name": "渠道商-普通商户进件", "model_name": "普通商户进件"},
        {"code": "dt", "model_url": "/inlet/chain", "name": "渠道商-连锁商户进件", "model_name": "连锁商户进件"},
        {"code": "dt", "model_url": "/inlet/cs", "name": "渠道商-连锁门店进件", "model_name": "连锁门店进件"},
        {"code": "dt", "model_url": "/common/downloads_bill", "name": "渠道商-商户对账单", "model_name": "商户对账单"},
        {"code": "dt", "model_url": "/balance/mch", "name": "渠道商-商户结算", "model_name": "商户结算"},
        {"code": "dt", "model_url": "/balance/dt", "name": "渠道商-渠道结算", "model_name": "渠道结算"},
        {"code": "dt", "model_url": "/transaction/trade", "name": "渠道商-商户交易", "model_name": "商户交易"},
        {"code": "dt", "model_url": "/transaction/refund", "name": "渠道商-商户退款", "model_name": "商户退款"},
        {"code": "dt", "model_url": "/stats/transaction", "name": "渠道商-渠道交易统计", "model_name": "渠道交易统计"},
        {"code": "dt", "model_url": "/stats/mch", "name": "渠道商-商户交易统计", "model_name": "商户交易统计"},
        {"code": "dt", "model_url": "/common/settings/sub_user", "name": "渠道商-员工账号管理", "model_name": "员工账号管理"},
        {"code": "dt", "model_url": "/common/role", "name": "渠道商-角色管理", "model_name": "角色管理"},
        {"code": "dt", "model_url": "/settings/email", "name": "渠道商-商户开户邮件汇总", "model_name": "商户开户邮件汇总"},


        # 商户权限
        {"code": "mch", "model_url": "/inlet/mch", "name": "商户-商户进件", "model_name": "商户进件"},
        {"code": "mch", "model_url": "/common/downloads_bill", "name": "商户-商户对账单", "model_name": "商户对账单"},
        {"code": "mch", "model_url": "/balance/mch", "name": "商户-商户结算", "model_name": "商户结算"},
        {"code": "mch", "model_url": "/transaction/trade", "name": "商户-商户交易", "model_name": "商户交易"},
        {"code": "mch", "model_url": "/transaction/refund", "name": "商户-商户退款", "model_name": "商户退款"},
        {"code": "mch", "model_url": "/stats/transaction", "name": "商户-交易统计", "model_name": "交易统计"},
        {"code": "mch", "model_url": "/capital", "name": "商户-资金流水", "model_name": "资金流水"},
        {"code": "mch", "model_url": "/settings/refund/password", "name": "商户-退款密码管理", "model_name": "退款密码管理"},
        {"code": "mch", "model_url": "/common/settings/send", "name": "商户-公众号交易提醒", "model_name": "公众号交易提醒"},
        {"code": "mch", "model_url": "/common/role", "name": "商户-角色管理", "model_name": "角色管理"},
        {"code": "mch", "model_url": "/common/settings/sub_user", "name": "商户-员工账号管理", "model_name": "员工账号管理"},


        # 连锁商户权限
        {"code": "mr", "model_url": "/inlet/chain", "name": "连锁商户-商户进件", "model_name": "商户进件"},
        {"code": "mr", "model_url": "/inlet/cs", "name": "连锁商户-门店进件", "model_name": "门店进件"},
        {"code": "mr", "model_url": "/common/downloads_bill", "name": "连锁商户-商户对账单", "model_name": "商户对账单"},
        {"code": "mr", "model_url": "/balance/cs", "name": "连锁商户-门店结算", "model_name": "门店结算"},
        {"code": "mr", "model_url": "/transaction/trade", "name": "连锁商户-门店交易", "model_name": "门店交易"},
        {"code": "mr", "model_url": "/transaction/refund", "name": "连锁商户-门店退款", "model_name": "门店退款"},
        {"code": "mr", "model_url": "/settings/refund/password", "name": "连锁商户-退款密码管理", "model_name": "退款密码管理"},
        {"code": "mr", "model_url": "/common/settings/send", "name": "连锁商户-公众号交易提醒", "model_name": "公众号交易提醒"},
        {"code": "mr", "model_url": "/common/role", "name": "连锁商户-角色管理", "model_name": "角色管理"},
        {"code": "mr", "model_url": "/common/settings/sub_user", "name": "连锁商户-员工账号管理", "model_name": "员工账号管理"},


        # 银行权限
        {"code": "bk", "model_url": "/inlet/inter_bank", "name": "银行-同业银行进件", "model_name": "同业银行进件"},
        {"code": "bk", "model_url": "/inlet/dt", "name": "银行-渠道进件", "model_name": "渠道进件"},
        {"code": "bk", "model_url": "/inlet/mch", "name": "银行-普通商户进件", "model_name": "普通商户进件"},
        {"code": "bk", "model_url": "/inlet/chain", "name": "银行-连锁商户进件", "model_name": "连锁商户进件"},
        {"code": "bk", "model_url": "/inlet/cs", "name": "银行-连锁门店进件", "model_name": "连锁门店进件"},
        {"code": "bk", "model_url": "/recon/transaction", "name": "银行-交易对账异常", "model_name": "交易对账异常"},
        {"code": "bk", "model_url": "/recon/refund", "name": "银行-退款对账异常", "model_name": "退款对账异常"},
        {"code": "bk", "model_url": "/common/downloads_bill", "name": "银行-商户对账单", "model_name": "商户对账单"},
        {"code": "bk", "model_url": "/balance/mch", "name": "银行-商户结算", "model_name": "商户结算"},
        {"code": "bk", "model_url": "/balance/dt", "name": "银行-渠道结算", "model_name": "渠道结算"},
        {"code": "bk", "model_url": "/transaction/trade", "name": "银行-商户交易", "model_name": "商户交易"},
        {"code": "bk", "model_url": "/transaction/refund", "name": "银行-商户退款", "model_name": "商户退款"},
        {"code": "bk", "model_url": "/stats/transaction", "name": "银行-银行交易统计", "model_name": "银行交易统计"},
        {"code": "bk", "model_url": "/stats/dist", "name": "银行-渠道交易统计", "model_name": "渠道交易统计"},
        {"code": "bk", "model_url": "/stats/mch", "name": "银行-商户交易统计", "model_name": "商户交易统计"},
        {"code": "bk", "model_url": "/capital/mch", "name": "银行-转入转出", "model_name": "转入转出"},
        {"code": "bk", "model_url": "/subsidize/mch", "name": "银行-活动商户管理", "model_name": "活动商户管理"},
        {"code": "bk", "model_url": "/common/role", "name": "银行-角色管理", "model_name": "角色管理"},
        {"code": "bk", "model_url": "/common/settings/sub_user", "name": "银行-员工账号管理", "model_name": "员工账号管理"},
        {"code": "bk", "model_url": "/risk/merchant", "name": "银行-监控中心-商户风险信息", "model_name": "商户风险信息"},
        {"code": "bk", "model_url": "/risk/trade", "name": "银行-监控中心-交易风险信息", "model_name": "交易风险信息"},

        # 官方权限
        {"code": "ub", "model_url": "/inlet/inter_bank", "name": "官方-同业银行进件", "model_name": "同业银行进件"},
        {"code": "ub", "model_url": "/inlet/dt", "name": "官方-渠道进件", "model_name": "渠道进件"},
        {"code": "ub", "model_url": "/inlet/mch", "name": "官方-商户进件", "model_name": "商户进件"},
        {"code": "ub", "model_url": "/inlet/chain", "name": "官方-连锁商户进件", "model_name": "连锁商户进件"},
        {"code": "ub", "model_url": "/inlet/cs", "name": "官方-连锁门店进件", "model_name": "连锁门店进件"},
        {"code": "ub", "model_url": "/recon/transaction", "name": "官方-交易对账异常", "model_name": "交易对账异常"},
        {"code": "ub", "model_url": "/recon/refund", "name": "官方-退款对账异常", "model_name": "退款对账异常"},
        {"code": "ub", "model_url": "/common/downloads_bill", "name": "官方-商户对账单", "model_name": "商户对账单"},
        {"code": "ub", "model_url": "/balance/mch", "name": "官方-商户结算", "model_name": "商户结算"},
        {"code": "ub", "model_url": "/balance/dt", "name": "官方-渠道结算", "model_name": "渠道结算"},
        {"code": "ub", "model_url": "/transaction/trade", "name": "官方-商户交易", "model_name": "商户交易"},
        {"code": "ub", "model_url": "/transaction/refund", "name": "官方-商户退款", "model_name": "商户退款"},
        {"code": "ub", "model_url": "/stats/transaction", "name": "官方-平台交易统计", "model_name": "平台交易统计"},
        {"code": "ub", "model_url": "/stats/dist", "name": "官方-渠道交易统计", "model_name": "渠道交易统计"},
        {"code": "ub", "model_url": "/stats/mch", "name": "官方-商户交易统计", "model_name": "商户交易统计"},
        {"code": "ub", "model_url": "/capital/mch", "name": "官方-转入转出", "model_name": "转入转出"},
        {"code": "ub", "model_url": "/operations/message/send", "name": "官方-短信推送管理", "model_name": "短信推送管理"},
        {"code": "ub", "model_url": "/subsidize/mch", "name": "官方-活动商户管理", "model_name": "活动商户管理"},
        {"code": "ub", "model_url": "/common/role", "name": "官方-角色管理", "model_name": "角色管理"},
        {"code": "ub", "model_url": "/common/settings/sub_user", "name": "官方-员工账号管理", "model_name": "员工账号管理"},
        {"code": "ub", "model_url": "/risk/merchant", "name": "官方-监控中心-商户风险信息", "model_name": "商户风险信息"},
        {"code": "ub", "model_url": "/risk/trade", "name": "官方-监控中心-交易风险信息", "model_name": "交易风险信息"},
    ]
    data = 0
    for new_record in records:
        try:
            cnow = datetime.datetime.now()
            _record = Permit(
                name=new_record["name"],
                model_name=new_record["model_name"],
                model_url=new_record["model_url"],
                sys_type_id=sys_map[new_record["code"]],
                is_hq=new_record.get("is_hq", 1),
                status=1,
                sp_type=0,
                sys_id=0,
                is_boss=0,
                is_admin=0,
                create_at=cnow,
                update_at=cnow
            )
            uline_session.add(_record)
            uline_session.commit()
            data += 1
            logger.info("{}权限已写入角色信息表".format(new_record["name"]))
        except Exception as err:
            logger.info("{}权限写入信息出现错误{}".format(new_record["name"], err))
            continue
            # pass
    logger.debug("权限信息共写入{}条信息".format(data))

    return


def role_permit_update():
    '''
    添加各个平台所需权限
    '''

    dbsession = uline_session()
    sys_query = dbsession.query(SysType).all()
    sys_map = {}
    # 提取平台id
    for row in sys_query:
        sys_map[row.id] = row.code
    permits_query = dbsession.query(Permit).all()
    permits = {}
    for row in permits_query:
        if row.sys_type_id not in permits:
            permits[row.sys_type_id] = {}
            permits[row.sys_type_id]["pids"] = set()
        permits[row.sys_type_id][row.model_name] = row.id
        permits[row.sys_type_id]["pids"].add(row.id)
    role_query = dbsession.query(Role).all()
    records = {}
    cnow = datetime.datetime.now()
    for row in role_query:
        if row.sp_type == 1:
            if sys_map[row.sys_type_id] == "bk":
                if row.is_hq == 0:
                    records[row.id] = permits[row.sys_type_id]["pids"].copy()
                    records[row.id].remove(permits[row.sys_type_id][u"同业银行进件"])
                    continue
            records[row.id] = permits[row.sys_type_id]["pids"].copy()

        elif row.sp_type == 3:
            records[row.id] = set()
            for k, v in permits[row.sys_type_id].iteritems():
                print(k)

            records[row.id].add(permits[row.sys_type_id][u"商户交易"])
            records[row.id].add(permits[row.sys_type_id][u"商户退款"])
        elif row.sp_type == 4:
            records[row.id] = permits[row.sys_type_id]["pids"].copy()
            records[row.id].remove(permits[row.sys_type_id][u"角色管理"])
            records[row.id].remove(permits[row.sys_type_id][u"员工账号管理"])
            records[row.id].remove(permits[row.sys_type_id][u"公众号交易提醒"])
            records[row.id].remove(permits[row.sys_type_id][u"退款密码管理"])

    data = 0
    role_permit_list = []
    for role_id, ids in records.iteritems():
        for permit_id in ids:
            try:
                cnow = datetime.datetime.now()
                _record = RolePermit(
                    role_id=role_id,
                    permit_id=permit_id,
                    create_at=cnow,
                    update_at=cnow
                )
                uline_session.add(_record)
                uline_session.commit()
                data += 1
                logger.info("{}---{}角色权限已写入角色信息表".format(role_id, permit_id))
            except Exception as err:
                logger.info("{}-{}角色权限写入信息出现错误{}".format(role_id, permit_id, err))
                continue
            # pass
    logger.debug("角色权限信息共写入{}条信息".format(data))

    return


if __name__ == "__main__":

    initdb()
    sys_update()
    logger.info("~~~~~~~~~~~~~~~~~~~这是可爱的分隔符~~~~~~~~~~~~~~~~")

    role_update()
    logger.info("~~~~~~~~~~~~~~~~~~~这是可爱的分隔符~~~~~~~~~~~~~~~~")

    permit_update()
    logger.info("~~~~~~~~~~~~~~~~~~~这是可爱的分隔符~~~~~~~~~~~~~~~~")

    role_permit_update()
    logger.info("~~~~~~~~~~~~~~~~~~~这是可爱的分隔符~~~~~~~~~~~~~~~~")

    migrate_dt_employee_data()
    logger.info("~~~~~~~~~~~~~~~~~~~这是可爱的分隔符~~~~~~~~~~~~~~~~")

    migrate_mch_data()
    logger.info("~~~~~~~~~~~~~~~~~~~这是可爱的分隔符~~~~~~~~~~~~~~~~")

    migrate_dt_data()
    logger.info("~~~~~~~~~~~~~~~~~~~这是可爱的分隔符~~~~~~~~~~~~~~~~")

    migrate_bk_data()
    logger.info("~~~~~~~~~~~~~~~~~~~这是可爱的分隔符~~~~~~~~~~~~~~~~")

    migrate_official_data()
    logger.info("~~~~~~~~~~~~~~~~~~~这是可爱的分隔符~~~~~~~~~~~~~~~~")

    migrate_mch_employee_data()
    logger.info("~~~~~~~~~~~~~~~~~~~这是可爱的分隔符~~~~~~~~~~~~~~~~")

    migrate_employee_cs_data()
