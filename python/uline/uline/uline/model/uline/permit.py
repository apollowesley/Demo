#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Liufei
# Create: '19/9/17'

from sqlalchemy import (
    BigInteger, Column, DateTime,
    Integer, String, text, Sequence, Index, TEXT,
    SmallInteger, UniqueConstraint, PrimaryKeyConstraint,
    ForeignKey)
from .base import Model as Base
from .base import uline_session


class Organization(Base):
    __tablename__ = 'organization'

    id = Column(Integer, Sequence('organization_id_seq'), primary_key=True)
    name = Column(String(128), nullable=False)
    sys_type_id = Column(BigInteger, ForeignKey("sys_type.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    sys_id = Column(BigInteger, nullable=False)
    parent_id = Column(BigInteger, nullable=False)
    sys_parent_id = Column(BigInteger, nullable=False)
    level = Column(SmallInteger, nullable=False)
    is_root = Column(SmallInteger, nullable=False)
    is_end = Column(SmallInteger, nullable=False)
    fullpath = Column(TEXT, nullable=False)
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))

    __table_args__ = (
        Index('organization_index', id, unique=True),
    )


class EmployeeRolePermit(Base):
    __tablename__ = 'employee_role_permit'

    id = Column(Integer, Sequence('employee_role_permit_id_seq'), primary_key=True)
    employee_id = Column(BigInteger, nullable=False)
    role_id = Column(BigInteger, ForeignKey("role.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    # 去掉这两个字段
    # permit_id = Column(BigInteger, ForeignKey("permit.id"), nullable=False)
    # model_url = Column(String(500), nullable=False)
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))

    __table_args__ = (
        Index('employee_role_permit_id_index', id, unique=True),
    )


class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, Sequence('role_id_seq'), primary_key=True)
    name = Column(String(128), nullable=False)
    sys_type_id = Column(BigInteger, ForeignKey("sys_type.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    sys_id = Column(BigInteger, nullable=False)
    is_boss = Column(SmallInteger, nullable=False)
    is_admin = Column(SmallInteger, nullable=False)
    is_hq = Column(SmallInteger, nullable=False)  # 是否是直营角色
    is_follower = Column(SmallInteger, nullable=False)
    sp_type = Column(SmallInteger, nullable=False)
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))

    __table_args__ = (
        Index('role_id_index', id, unique=True),
    )


class RolePermit(Base):
    __tablename__ = 'role_permit'

    id = Column(Integer, Sequence('role_permit_id_seq'), primary_key=True)
    role_id = Column(BigInteger, ForeignKey("role.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    permit_id = Column(BigInteger, ForeignKey("permit.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))

    __table_args__ = (
        Index('role_permit_id_index', id, unique=True),
    )


class Permit(Base):
    __tablename__ = 'permit'

    id = Column(Integer, Sequence('permit_id_seq'), primary_key=True)
    name = Column(String(128), nullable=False)
    sys_type_id = Column(BigInteger, ForeignKey("sys_type.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    sys_id = Column(BigInteger, nullable=False)
    model_name = Column(String(128), nullable=False)
    model_url = Column(String(500), nullable=False)
    is_boss = Column(SmallInteger, nullable=False)
    is_admin = Column(SmallInteger, nullable=False)
    is_hq = Column(SmallInteger, nullable=False)
    sp_type = Column(SmallInteger, nullable=False)
    status = Column(SmallInteger, nullable=False)
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))

    __table_args__ = (
        Index('permit_id_index', id, unique=True),
    )
