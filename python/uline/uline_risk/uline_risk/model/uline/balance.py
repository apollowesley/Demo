#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '11/4/16'

from sqlalchemy import BigInteger, Column, DateTime, String, SmallInteger, Index, INTEGER

from .base import Model as Base


class MchDailyBalanceInfo(Base):
    __tablename__ = 'mch_daily_balance_info'

    mch_daily_balance_no = Column(BigInteger, primary_key=True)
    mch_trand_id = Column(BigInteger, index=True)
    mch_id = Column(BigInteger, nullable=False)
    busitype = Column(SmallInteger, nullable=False)
    rcvacctno = Column(String(64), nullable=False)
    rcvbankname = Column(String(128), nullable=False)
    rcvbanksettleno = Column(String(12), nullable=False)
    rcvacctname = Column(String(64), nullable=False)
    tranamt = Column(BigInteger, nullable=False)
    need_pay_time = Column(DateTime, nullable=False)
    pay_start_time = Column(DateTime)
    pay_end_time = Column(DateTime)
    pay_status = Column(SmallInteger, nullable=False)
    failure_details = Column(String(128))
    check_status = Column(SmallInteger, nullable=False)
    day_tx_amount = Column(BigInteger, nullable=False)
    day_refund_amount = Column(BigInteger, nullable=False)
    day_tx_net_amout = Column(BigInteger, nullable=False)
    day_profit_amount = Column(BigInteger, nullable=False)
    day_tx_count = Column(BigInteger, nullable=False)
    day_refund_count = Column(BigInteger, nullable=False)
    clear_report_status = Column(SmallInteger)
    clear_report_id = Column(String(32))
    channel = Column(String)
    create_at = Column(DateTime, nullable=False)

    d0_withdraw = Column(BigInteger)
    d0_withdraw_fee = Column(BigInteger)
    discount_amount = Column(BigInteger)

    __table_args__ = (
        Index('mch_daily_balance_info_mch_daily_balance_no_uindex', mch_daily_balance_no,
              unique=True),
    )


class PDailyBalanceInfo(Base):
    __tablename__ = 'p_daily_balance_info'

    p_daily_balance_no = Column(BigInteger, primary_key=True)
    p_trand_id = Column(BigInteger, index=True)
    busitype = Column(SmallInteger, nullable=False)
    rcvacctno = Column(String(64), nullable=False)
    rcvbankname = Column(String(128), nullable=False)
    rcvbanksettleno = Column(String(12), nullable=False)
    rcvacctname = Column(String(64), nullable=False)
    p_tranamt = Column(BigInteger, nullable=False)
    bk_tranamt = Column(BigInteger, nullable=False)
    service_fee = Column(BigInteger, nullable=False)
    need_pay_time = Column(DateTime, nullable=False)
    pay_start_time = Column(DateTime)
    pay_end_time = Column(DateTime)
    pay_status = Column(SmallInteger, nullable=False)
    failure_details = Column(String(128))
    check_status = Column(SmallInteger, nullable=False)
    day_tx_amount = Column(BigInteger, nullable=False)
    day_refund_amount = Column(BigInteger, nullable=False)
    day_tx_net_amout = Column(BigInteger, nullable=False)
    day_profit_amount = Column(BigInteger, nullable=False)
    day_tx_count = Column(BigInteger, nullable=False)
    day_refund_count = Column(BigInteger, nullable=False)
    clear_report_id = Column(String(32))
    clear_report_status = Column(SmallInteger)
    channel = Column(String)
    create_at = Column(DateTime, nullable=False)

    d0_withdraw_profit = Column(BigInteger)
    discount_amount = Column(BigInteger)
    __table_args__ = (
        Index('p_daily_balance_info_p_daily_balance_no_uindex', p_daily_balance_no,
              unique=True),
    )


class DtDailyBalanceInfo(Base):
    __tablename__ = 'dt_daily_balance_info'

    dt_daily_balance_no = Column(BigInteger, primary_key=True)
    dt_trand_id = Column(BigInteger, index=True)
    dt_id = Column(BigInteger, nullable=False)
    busitype = Column(SmallInteger, nullable=False)
    rcvacctno = Column(String(64), nullable=False)
    rcvbankname = Column(String(128), nullable=False)
    rcvbanksettleno = Column(String(12), nullable=False)
    rcvacctname = Column(String(64), nullable=False)
    tranamt = Column(BigInteger, nullable=False)
    need_pay_time = Column(DateTime, nullable=False)
    pay_start_time = Column(DateTime)
    pay_end_time = Column(DateTime)
    pay_status = Column(SmallInteger, nullable=False)
    failure_details = Column(String(128))
    check_status = Column(SmallInteger, nullable=False)
    day_tx_amount = Column(BigInteger, nullable=False)
    day_refund_amount = Column(BigInteger, nullable=False)
    day_tx_net_amout = Column(BigInteger, nullable=False)
    day_profit_amount = Column(BigInteger, nullable=False)
    day_tx_count = Column(BigInteger, nullable=False)
    day_refund_count = Column(BigInteger, nullable=False)
    clear_report_id = Column(String(32))
    clear_report_status = Column(SmallInteger)
    channel = Column(String)
    create_at = Column(DateTime, nullable=False)

    d0_withdraw_profit = Column(BigInteger)

    __table_args__ = (
        Index('dt_daily_balance_info_dt_daily_balance_no_uindex', dt_daily_balance_no, unique=True),
    )


class CsDailyBalanceInfo(Base):
    __tablename__ = 'cs_daily_balance_info'

    cs_daily_balance_no = Column(BigInteger, primary_key=True, index=True)
    cs_trand_id = Column(BigInteger, index=True)
    cs_id = Column(BigInteger, nullable=False)
    busitype = Column(SmallInteger, nullable=False)
    rcvacctno = Column(String(64), nullable=False)
    rcvbankname = Column(String(128), nullable=False)
    rcvbanksettleno = Column(String(12), nullable=False)
    rcvacctname = Column(String(64), nullable=False)
    raw_tranamt = Column(BigInteger, nullable=False)
    tranamt = Column(BigInteger, nullable=False)
    parent_id = Column(BigInteger, nullable=True)
    rate = Column(INTEGER, nullable=True)
    need_pay_time = Column(DateTime, nullable=False)
    pay_start_time = Column(DateTime)
    pay_end_time = Column(DateTime)
    pay_status = Column(SmallInteger, nullable=False)
    failure_details = Column(String(128))
    check_status = Column(SmallInteger, nullable=False)
    day_tx_amount = Column(BigInteger, nullable=False)
    day_refund_amount = Column(BigInteger, nullable=False)
    day_tx_net_amout = Column(BigInteger, nullable=False)
    day_profit_amount = Column(BigInteger, nullable=False)
    day_tx_count = Column(BigInteger, nullable=False)
    day_refund_count = Column(BigInteger, nullable=False)
    clear_report_id = Column(String(32))
    channel = Column(String)
    create_at = Column(DateTime, nullable=False)
