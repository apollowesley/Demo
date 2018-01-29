#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '11/4/16'

from sqlalchemy import BigInteger, Column, DateTime, String, SmallInteger, Index, INTEGER, Integer, Sequence, text, Date

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


class MchBook(Base):

    # 商户日切记账表
    __tablename__ = 'mch_book'

    id = Column(Integer, Sequence(
        'mch_book_id_seq', start=1), primary_key=True)
    mch_id = Column(BigInteger, nullable=False, server_default='0')
    dt_id = Column(BigInteger, nullable=False, server_default='0')
    #  三方支付平台,wx:微信,ali:支付宝
    pay_channel = Column(String(64), nullable=False, server_default='')
    # 商家收入,可提现余额
    profit_total = Column(BigInteger, nullable=False, server_default='0')
    bp_profit = Column(BigInteger, nullable=False, server_default='0')
    dt_profit = Column(BigInteger, nullable=False, server_default='0')
    # 总交易额
    trade_total = Column(BigInteger, nullable=False, server_default='0')
    # 退款总额
    refund_total = Column(BigInteger, nullable=False, server_default='0')
    # 退款冻结总额
    refund_freeze = Column(BigInteger, nullable=False, server_default='0')
    # d0提现总额
    d0_total = Column(BigInteger, nullable=False, server_default='0')
    # d0提现冻结总额
    d0_freeze = Column(BigInteger, nullable=False, server_default='0')
    # 日切时间
    cut_date = Column(Date, nullable=False, server_default=text("now()"))

    # 新增字段
    trade_count = Column(Integer, nullable=False, server_default='0')
    refund_count = Column(Integer, nullable=False, server_default='0')
    d0_count = Column(Integer, nullable=False, server_default='0')

    mch_trade_fee = Column(BigInteger, nullable=False, server_default='0')
    mch_d0_fee = Column(BigInteger, nullable=False, server_default='0')
    dt_trade_profit = Column(BigInteger, nullable=False, server_default='0')
    dt_d0_profit = Column(BigInteger, nullable=False, server_default='0')
    bp_trade_profit = Column(BigInteger, nullable=False, server_default='0')
    bp_d0_profit = Column(BigInteger, nullable=False, server_default='0')
    pay_channel_profit = Column(BigInteger, nullable=False, server_default='0')
    bank_d0_cost = Column(BigInteger, nullable=False, server_default='0')

    status = Column(SmallInteger, nullable=False, server_default='0')

    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))


class DtBook(Base):

    # 渠道日切记账表
    __tablename__ = 'dt_book'

    id = Column(Integer, Sequence(
        'dt_book_id_seq', start=1), primary_key=True)
    dt_id = Column(BigInteger, nullable=False, server_default='0')

    #  三方支付平台,wx:微信,ali:支付宝
    pay_channel = Column(String(64), nullable=False, server_default='')
    # 总收益
    profit_total = Column(BigInteger, nullable=False, server_default='0')

    # 日切时间
    cut_date = Column(Date, nullable=False, server_default=text("now()"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))


class BankBook(Base):

    # 银行日切记账表
    __tablename__ = 'bank_book'

    id = Column(Integer, Sequence(
        'bank_book_id_seq', start=1), primary_key=True)
    bank_id = Column(BigInteger, nullable=False, server_default='0')

    #  三方支付平台,wx:微信,ali:支付宝
    pay_channel = Column(String(64), nullable=False, server_default='')
    # 总收益
    profit_total = Column(BigInteger, nullable=False, server_default='0')

    # 日切时间
    cut_date = Column(Date, nullable=False, server_default=text("now()"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))


class PBook(Base):

    # 银行日切记账表
    __tablename__ = 'p_book'

    id = Column(Integer, Sequence(
        'bank_book_id_seq', start=1), primary_key=True)

    #  三方支付平台,wx:微信,ali:支付宝
    pay_channel = Column(String(64), nullable=False, server_default='')
    # 总收益
    profit_total = Column(BigInteger, nullable=False, server_default='0')

    # 日切时间
    cut_date = Column(Date, nullable=False, server_default=text("now()"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))
