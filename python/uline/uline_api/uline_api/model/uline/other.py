#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '11/3/16'
from sqlalchemy import BigInteger, Column, DateTime, Integer, String, text, Sequence, Index, TEXT

from uline_api.model.uline.base import Model as Base


class ActivatedDtInfo(Base):
    __tablename__ = 'activated_dt_info'

    id = Column(Integer, Sequence('activated_dt_info_id_seq'), primary_key=True)
    dt_id = Column(BigInteger, nullable=False)
    payment_type = Column(Integer, nullable=False, server_default=text("0"))
    comment = Column(String(64), nullable=False)
    activated_status = Column(Integer, nullable=False, server_default=text("0"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    activated_user = Column(String)

    __table_args__ = (
        Index('activated_dt_info_index', id, unique=True),
    )


class ActivatedMchInfo(Base):
    __tablename__ = 'activated_mch_info'

    id = Column(Integer, Sequence('activated_mch_info_id_seq'), primary_key=True)
    mch_id = Column(BigInteger, nullable=False)
    payment_type = Column(Integer, nullable=False, server_default=text("0"))
    comment = Column(String(64), nullable=False)
    activated_status = Column(Integer, nullable=False, server_default=text("0"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    activated_user = Column(String)

    __table_args__ = (
        Index('activated_mch_info_index', id,
              unique=True),
    )


class AuthDtInfo(Base):
    __tablename__ = 'auth_dt_info'

    id = Column(Integer, Sequence('auth_dt_info_id_seq'), primary_key=True)
    dt_id = Column(BigInteger, nullable=False)
    comment = Column(String(64), nullable=False)
    auth_status = Column(Integer, nullable=False, server_default=text("0"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    auth_user = Column(String)

    __table_args__ = (
        Index('auth_dt_info_index', id, unique=True),
    )


class AuthMchInfo(Base):
    __tablename__ = 'auth_mch_info'

    id = Column(Integer, Sequence('auth_mch_info_id_seq'), primary_key=True)
    mch_id = Column(BigInteger, nullable=False)
    comment = Column(String(64), nullable=False)
    auth_status = Column(Integer, nullable=False, server_default=text("0"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    auth_user = Column(String)

    __table_args__ = (
        Index('auth_mch_info_index', id, unique=True),
    )


class ActivatedMchEmailInfo(Base):
    __tablename__ = 'activated_mch_email_info'

    id = Column(Integer, Sequence('activated_mch_email_info_id_seq'), primary_key=True)
    mch_id = Column(BigInteger, nullable=False)
    email = Column(String(64), nullable=False)
    comment = Column(String(64), nullable=False)
    status = Column(Integer, nullable=False, server_default=text("0"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))


class ActivatedDtEmailInfo(Base):
    __tablename__ = 'activated_dt_email_info'

    id = Column(Integer, Sequence('activated_dt_email_info_id_seq'), primary_key=True)
    dt_id = Column(BigInteger, nullable=False)
    email = Column(String(64), nullable=False)
    comment = Column(String(64), nullable=False)
    status = Column(Integer, nullable=False, server_default=text("0"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))


class ChangeRecord(Base):
    __tablename__ = 'change_record'

    id = Column(Integer, Sequence('change_record_id_seq'), primary_key=True)
    mch_id = Column(BigInteger, nullable=True)
    bk_id = Column(BigInteger, nullable=True)
    dt_id = Column(BigInteger, nullable=True)
    data_json = Column(TEXT, nullable=False)
    change_type = Column(Integer, nullable=False)
    status = Column(Integer, nullable=False)
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))

class SysType(Base):
    __tablename__ = 'sys_type'

    id = Column(Integer, Sequence('sys_type_id_seq'), primary_key=True)

    name = Column(String(64), nullable=False)
    code = Column(String(64), nullable=False)
    perfix_code = Column(String(64), nullable=False)

    create_at = Column(DateTime, nullable=False)
    update_at = Column(DateTime, nullable=True)

