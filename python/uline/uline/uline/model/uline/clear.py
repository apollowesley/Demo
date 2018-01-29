#!/usr/bin/env python
#-*- coding: utf-8 -*-
# Author: Ficapy
# Create: '11/4/16'
from sqlalchemy import BigInteger, Column, DateTime, Integer, String, text, Index, SmallInteger, Date, Sequence

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


class PreTradeClearInfo(Base):

    # 订单清分前置表
    __tablename__ = 'pre_trade_clear_info'

    id = Column(Integer, Sequence('pre_trade_clear_info_id_seq', start=1), primary_key=True)

    # 内部订单号
    out_trade_no = Column(String(64), nullable=False, server_default='')
    # 微信支付宝订单号
    transaction_id = Column(String(64), nullable=False, server_default='')
    # 渠道商ID
    dt_id = Column(BigInteger, nullable=False, server_default='0')
    # 商户ID
    mch_id = Column(BigInteger, nullable=False, server_default='0')
    # 商户支付类型ID
    mch_payment_id = Column(Integer, nullable=False, server_default='0')
    # uline支付通道ID
    uline_payment_id = Column(Integer, nullable=False, server_default='0')
    # uline清算配置ID
    uline_settle_id = Column(Integer, nullable=False, server_default='0')
    # 三方支付通道
    pay_channel = Column(String(64), nullable=False, server_default='')
    # 支付类型
    trade_type = Column(String(64), nullable=False, server_default='')
    # 支付平台注册商户信息表ID
    platform_mch_id = Column(Integer, nullable=False, server_default='0')
    # 交易金额
    total_fee = Column(BigInteger, nullable=False, server_default='0')
    # 商户费率
    mch_rate = Column(Integer, nullable=False, server_default='0')
    # 商户扣费
    mch_profit = Column(BigInteger, nullable=False, server_default='0')
    # 渠道商费率
    dt_rate = Column(Integer, nullable=False, server_default='0')
    # 渠道商扣费
    dt_profit = Column(BigInteger, nullable=False, server_default='0')
    # 支付平台费率
    pay_channel_rate = Column(Integer, nullable=False, server_default='0')
    # 支付平台扣费
    pay_channel_profit = Column(BigInteger, nullable=False, server_default='0')
    # 银行平台收益
    bp_profit = Column(BigInteger, nullable=False, server_default='0')
    remark = Column(String(64), nullable=False, server_default='')

    complete_at = Column(DateTime, nullable=False, server_default=text("now()"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))


class PreRefundClearInfo(Base):

    # 退款清分前置表
    __tablename__ = 'pre_refund_clear_info'

    id = Column(Integer, Sequence('pre_refund_clear_info_id_seq', start=1), primary_key=True)

    # 内部订单号
    out_trade_no = Column(String(64), nullable=False, server_default='')
    # 微信支付宝订单号
    transaction_id = Column(String(64), nullable=False, server_default='')
    # 退款单号
    out_refund_no = Column(String(64), nullable=False, server_default='')
    # 渠道商ID
    dt_id = Column(BigInteger, nullable=False, server_default='0')
    # 商户ID
    mch_id = Column(BigInteger, nullable=False, server_default='0')
    # 商户支付表id,mch_payment表
    mch_payment_id = Column(Integer, nullable=False, server_default='0')
    # uline支付通道id,uline_channel表
    uline_payment_id = Column(Integer, nullable=False, server_default='0')
    # uline清算配置ID
    uline_settle_id = Column(Integer, nullable=False, server_default='0')
    # 三方支付通道
    pay_channel = Column(String(64), nullable=False, server_default='')
    # 支付类型
    trade_type = Column(String(64), nullable=False, server_default='')
    # 三方支付平台注册id,platform_mch表
    platform_mch_id = Column(Integer, nullable=False, server_default='0')
    # 交易金额
    total_fee = Column(BigInteger, nullable=False, server_default='0')
    # 退款金额
    refund_fee = Column(BigInteger, nullable=False, server_default='0')
    # 商户费率
    mch_rate = Column(Integer, nullable=False, server_default='0')
    # 商户扣费
    mch_profit = Column(BigInteger, nullable=False, server_default='0')
    # 渠道商费率
    dt_rate = Column(Integer, nullable=False, server_default='0')
    # 渠道商扣费
    dt_profit = Column(BigInteger, nullable=False, server_default='0')
    # 支付平台费率
    pay_channel_rate = Column(Integer, nullable=False, server_default='0')
    # 支付平台扣费
    pay_channel_profit = Column(BigInteger, nullable=False, server_default='0')
    # 银行平台收益
    bp_profit = Column(BigInteger, nullable=False, server_default='0')
    remark = Column(String(64), nullable=False, server_default='')

    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))
    complete_at = Column(DateTime, nullable=False, server_default=text("now()"))


class PreD0ClearInfo(Base):

    # D0清分前置表
    __tablename__ = 'pre_d0_clear_info'

    id = Column(Integer, Sequence('pre_d0_clear_info_id_seq', start=1), primary_key=True)
    # 内部订单号
    out_trade_no = Column(String(64), nullable=False, server_default='')
    # 渠道商ID
    dt_id = Column(BigInteger, nullable=False, server_default='0')
    # 商户ID
    mch_id = Column(BigInteger, nullable=False, server_default='0')
    # 业务类型
    busitype = Column(SmallInteger, nullable=False, server_default='0')
    # 商户支付类型ID
    mch_payment_id = Column(Integer, nullable=False, server_default='0')
    # uline支付通道ID
    uline_payment_id = Column(Integer, nullable=False, server_default='0')
    # uline清算配置ID
    uline_settle_id = Column(Integer, nullable=False, server_default='0')
    # 三方支付通道
    pay_channel = Column(String(64), nullable=False, server_default='')
    # 结算方式（冗余uline_settle表）
    settlement = Column(Integer, nullable=False, server_default='0')

    # 提现费率
    draw_rate = Column(Integer, nullable=False, server_default='0')
    # 提现成本费
    draw_profit = Column(Integer, nullable=False, server_default='0')
    # 提现金额
    draw_fee = Column(BigInteger, nullable=False, server_default='0')
    # 扣费总额
    total_fee = Column(BigInteger, nullable=False, server_default='0')

    # 商户费率
    mch_rate = Column(Integer, nullable=False, server_default='0')
    # 商户扣费
    mch_fee = Column(BigInteger, nullable=False, server_default='0')
    # 渠道商费率
    dt_rate = Column(Integer, nullable=False, server_default='0')
    # 渠道商扣费
    dt_fee = Column(BigInteger, nullable=False, server_default='0')
    dt_profit = Column(BigInteger, nullable=False, server_default='0')
    # 银行平台收益
    bp_profit = Column(BigInteger, nullable=False, server_default='0')
    remark = Column(String(64), nullable=False, server_default='')

    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))
    complete_at = Column(DateTime, nullable=False, server_default=text("now()"))
