#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '11/4/16'
from sqlalchemy import BigInteger, Column, DateTime, Integer, String, text, Index, SmallInteger, Date

from .base import Model as Base


class MchClearInfo(Base):
    __tablename__ = 'mch_clear_info'

    mch_clear_no = Column(BigInteger, primary_key=True)
    mch_id = Column(BigInteger, nullable=False)
    out_trade_no = Column(String(32), nullable=False)
    mch_daily_balance_no = Column(BigInteger)
    trade_amount = Column(BigInteger, nullable=False)
    profit_rate = Column(Integer, nullable=False)
    mch_profit = Column(Integer, nullable=False)
    payment_type = Column(Integer)
    create_at = Column(DateTime, nullable=False)
    update_at = Column(DateTime, nullable=False)

    business_type = Column(SmallInteger)
    current_balance = Column(BigInteger)
    trade_date = Column(Date, index=True)
    channel = Column(String(32))
    remarks = Column(String(256))

    __table_args__ = (
        Index('mch_clear_info_mch_clear_no_uindex', mch_clear_no,
              unique=True),
    )


class PClearInfo(Base):
    __tablename__ = 'p_clear_info'

    p_clear_no = Column(BigInteger, primary_key=True)
    out_trade_no = Column(String(32), nullable=False)
    p_daily_balance_no = Column(BigInteger)
    trade_amount = Column(BigInteger, nullable=False)
    profit_rate = Column(Integer, nullable=False)
    p_profit = Column(Integer, nullable=False)
    payment_type = Column(Integer)
    service_fee = Column(Integer, nullable=False)
    service_rate = Column(Integer, nullable=False)
    create_at = Column(DateTime, nullable=False)
    update_at = Column(DateTime, nullable=False)
    trade_date = Column(Date, index=True)

    channel = Column(String(32))
    __table_args__ = (
        Index('p_clear_info_p_clear_no_uindex', p_clear_no,
              unique=True),
    )


class DtClearInfo(Base):
    __tablename__ = 'dt_clear_info'

    dt_clear_no = Column(BigInteger, primary_key=True)
    dt_id = Column(BigInteger, nullable=False)
    mch_id = Column(BigInteger, nullable=False)
    dt_daily_balance_no = Column(BigInteger)
    payment_type = Column(Integer)
    out_trade_no = Column(String(32), nullable=False)
    trade_amount = Column(BigInteger, nullable=False)
    profit_rate = Column(Integer, nullable=False)
    dt_profit = Column(Integer, nullable=False)
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))

    business_type = Column(SmallInteger)
    current_balance = Column(BigInteger)
    trade_date = Column(Date, index=True)
    channel = Column(String(32))
    remarks = Column(String(256))

    __table_args__ = (
        Index('dt_clear_info_dt_clear_no_uindex', dt_clear_no,
              unique=True),
    )
