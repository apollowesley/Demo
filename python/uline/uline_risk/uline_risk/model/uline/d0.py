#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '23/4/17'

from sqlalchemy import BigInteger, Column, DateTime, String, SmallInteger

from .base import Model as Base


class MchAsset(Base):
    __tablename__ = 'mch_asset'

    id = Column(BigInteger, primary_key=True)

    mch_id = Column(BigInteger, unique=True)
    wx_total = Column(BigInteger)
    wx_freeze = Column(BigInteger)
    ali_total = Column(BigInteger)
    ali_freeze = Column(BigInteger)


class D0Withdraw(Base):
    __tablename__ = 'd0_withdraw'

    id = Column(String(64), primary_key=True)
    d0_trand_id = Column(BigInteger, index=True)
    mch_d0_trand_id = Column(String(64), index=True)
    mch_id = Column(BigInteger, nullable=False)

    busitype = Column(SmallInteger)
    rcvacctno = Column(String(64))
    rcvbankname = Column(String(128))
    rcvbanksettleno = Column(String(12))
    rcvacctname = Column(String(64))

    raw_tranamt = Column(BigInteger, nullable=True)
    fee = Column(BigInteger)
    dt_id = Column(BigInteger)
    dt_fee = Column(BigInteger)
    p_fee = Column(BigInteger)
    tranamt = Column(BigInteger, nullable=False)

    pay_start_time = Column(DateTime)
    pay_end_time = Column(DateTime)
    pay_status = Column(SmallInteger, nullable=False)
    failure_details = Column(String(128))
    check_status = Column(SmallInteger)
    channel = Column(String)
    create_at = Column(DateTime, nullable=False)

    # 借款id,还款id,附加还款id
    loan_id = Column(BigInteger)
    repayment_id = Column(BigInteger)
    addition_repayment_id = Column(BigInteger)

    # 还款金额,未偿还金额
    repayment_amount = Column(BigInteger)
    addition_repayment_amount = Column(BigInteger)
