#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '11/3/16'

from sqlalchemy import (
    BigInteger, Column, DateTime,
    Integer, String, text, Sequence, Index,
    SmallInteger, UniqueConstraint, PrimaryKeyConstraint,
    ForeignKey)
from .base import Model as Base
from .base import uline_session


class BkUser(Base):
    __tablename__ = 'bk_user'

    bk_id = Column(Integer, Sequence('tb_bk_id_seq', metadata=Base.metadata,
                                     start=10000000), primary_key=True)
    bk_name = Column(String(64), nullable=False)
    email = Column(String(64), nullable=False)
    password = Column(String(256), nullable=False)
    api_key = Column(String(64))
    bk_type = Column(SmallInteger)
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))
    __table_args__ = (
        Index('bk_user_email_uindex', email,
              unique=True),
        Index('bk_user_index', bk_id, unique=True),
    )


class BkSubUser(Base):
    __tablename__ = 'bk_subuser'

    bk_sub_id = Column(Integer, Sequence('tb_bk_sub_id_seq', metadata=Base.metadata,
                                         start=10000000), primary_key=True)

    bk_user_bk_id = Column(Integer, ForeignKey('bk_user.bk_id'))
    bk_sub_name = Column(String(64), nullable=False)
    email = Column(String(64), nullable=False)
    password = Column(String(256), nullable=False)
    api_key = Column(String(64))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))

    __table_args__ = (
        Index('bk_subuser_email_uindex', email,
              unique=True),
        Index('bk_subuser_index', bk_sub_id, unique=True),
    )


class DtUser(Base):
    __tablename__ = 'dt_user'

    dt_id = Column(BigInteger, Sequence(
        'tb_dt_id_seq', metadata=Base.metadata, start=10000000), primary_key=True)
    dt_name = Column(String(64), nullable=False)
    email = Column(String(64), nullable=False)
    password = Column(String(256), nullable=False)
    api_key = Column(String(64))
    status = Column(Integer, nullable=False, server_default=text("0"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))
    wx_sub_mch_id = Column(String(64))
    mch_pay_key = Column(String(64))
    wx_app_sub_mch_id = Column(String(64))
    rate = Column(SmallInteger)
    refund_password = Column(String(256))
    ali_sub_mch_id = Column(String(64))
    # 支付宝商户等级
    ali_level = Column(String(32))
    # 京东商户号
    jd_sub_mch_id = Column(String(32))
    # qq钱包商户号
    qq_sub_mch_id = Column(String(32))

    # 银联字段
    # 等级
    unionpay_level = Column(String(32))
    # 限额
    unionpay_limit = Column(String(32))

    __table_args__ = (
        Index('dt_user_email_uindex', email, unique=False),
        Index('dt_user_index', dt_id,
              unique=True)
    )


class DtSubUser(Base):
    __tablename__ = 'dt_subuser'

    dt_sub_id = Column(BigInteger, Sequence('tb_dt_sub_id_seq', metadata=Base.metadata,
                                            start=10000000), primary_key=True)
    dt_user_dt_id = Column(BigInteger)
    dt_sub_name = Column(String(64), nullable=False)
    login_name = Column(String(64), nullable=False)
    email = Column(String(64), nullable=False)
    phone = Column(String(64), nullable=False)
    password = Column(String(256), nullable=False)
    api_key = Column(String(64))
    status = Column(Integer, nullable=False, server_default=text("1"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))

    __table_args__ = (
        Index('dt_subuser_index', dt_sub_id, unique=True),
    )


class MchUser(Base):
    __tablename__ = 'mch_user'

    mch_id = Column(BigInteger, Sequence('tb_mch_id_seq',
                                         metadata=Base.metadata, start=1000000000), primary_key=True)
    mch_name = Column(String(64), nullable=False)
    email = Column(String(64), nullable=False)
    password = Column(String(256), nullable=False)
    wx_sub_mch_id = Column(String(64))
    mch_pay_key = Column(String(64))
    status = Column(Integer, nullable=False)
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))
    api_key = Column(String(64))
    alipay_sub_mch_id = Column(String(64))
    ali_sub_mch_id = Column(String(64))
    # 支付宝商户等级
    ali_level = Column(String(32))
    # 是否使用渠道商微信支付(1表示不使用, 2表示使用)
    wx_use_parent = Column(SmallInteger, default=1)
    rate = Column(SmallInteger)
    wx_app_sub_mch_id = Column(String(64))
    refund_password = Column(String(256))
    # 京东商户号
    jd_sub_mch_id = Column(String(32))

    # qq钱包商户号
    qq_sub_mch_id = Column(String(32))

    # 银联字段
    # 等级
    unionpay_level = Column(String(32))
    # 限额
    unionpay_limit = Column(String(32))
    unionpay_sub_mch_id = Column(String(32))

    __table_args__ = (
        Index('mch_user_index', mch_id,
              unique=True),
    )


class MchSubUser(Base):
    """商户员工表"""

    __tablename__ = 'mch_subuser'
    mch_sub_id = Column(BigInteger, Sequence('tb_dt_sub_id_seq', metadata=Base.metadata,
                                             start=10000000), primary_key=True)
    mch_id = Column(BigInteger)
    scene_id = Column(String(256), unique=True)
    mch_sub_name = Column(String(64), nullable=False)
    login_name = Column(String(64), nullable=False, unique=True)
    email = Column(String(64), nullable=False)
    phone = Column(String(64), nullable=False)
    password = Column(String(256), nullable=False)
    # api_key = Column(String(64)
    wx_id = Column(String(64))
    wx_open_id = Column(String(64))
    status = Column(Integer, nullable=False, server_default=text("1"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))

    __table_args__ = (
        Index('mch_subuser_index', mch_sub_id, unique=True),
    )


class MchUserMchSubUser(Base):
    """
    如果员工属于连锁商户, 该表存储对应的门店。
    如果员工不属于连锁商户， 该表存储对应的商户。
    """

    __tablename__ = 'mch_user_mch_subuser'

    id = Column(Integer, Sequence(
        'tb_mch_user_subuser_id_seq', metadata=Base.metadata, start=1), primary_key=True)
    mch_id = Column(BigInteger, nullable=True)
    mch_sub_id = Column(BigInteger, nullable=False)
    dt_id = Column(BigInteger)
    new_employee_id = Column(BigInteger)

    __table_args__ = (
        UniqueConstraint(mch_id, mch_sub_id),
        Index('mch_mchuser_subuser_index', mch_id),
    )


class UbUser(Base):
    __tablename__ = 'ub_user'

    ub_id = Column(Integer, Sequence(
        'tb_ub_id_seq', metadata=Base.metadata, start=100000), primary_key=True)
    ub_name = Column(String(16), nullable=False)
    email = Column(String(64), nullable=False)
    api_key = Column(String(64))
    password = Column(String(256), nullable=False)
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))

    __table_args__ = (
        Index('ub_user_index', ub_id, unique=True),
    )


class Employee(Base):
    __tablename__ = 'employee'

    id = Column(BigInteger, Sequence('employee_employee_id_seq', metadata=Base.metadata, start=10000000),
                primary_key=True)
    sys_type_id = Column(Integer, ForeignKey("sys_type.id"), nullable=False)
    sys_id = Column(BigInteger, nullable=False)
    login_name = Column(String(64), nullable=False, unique=True)
    login_passwd = Column(String(256), nullable=False)
    user_id = Column(Integer, nullable=False)
    status = Column(Integer, nullable=False)
    last_login = Column(DateTime)
    creator_id = Column(BigInteger, nullable=False)
    create_at = Column(DateTime, nullable=False)
    update_at = Column(DateTime, nullable=True)

    __table_args__ = (

        Index('employee_sys_id_index', sys_id),

    )


class UnionEmployee(Base):
    __tablename__ = 'union_employee'

    id = Column(Integer, Sequence('union_employee_id_seq'), primary_key=True)
    employee_id = Column(BigInteger, nullable=False)
    sys_type_id = Column(Integer, ForeignKey("sys_type.id"), nullable=False)
    sys_id = Column(BigInteger)
    create_at = Column(DateTime, nullable=False)

    __table_args__ = (UniqueConstraint(employee_id, sys_id), Index('union_employee_index', sys_id),)
