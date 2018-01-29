#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '11/3/16'
from sqlalchemy import BigInteger, Column, DateTime, Integer, String, text, Sequence, Index, TEXT, SmallInteger, UniqueConstraint
from .base import Model as Base


class ActivatedDtInfo(Base):
    __tablename__ = 'activated_dt_info'

    id = Column(Integer, Sequence(
        'activated_dt_info_id_seq'), primary_key=True)
    dt_id = Column(BigInteger, nullable=False)
    payment_type = Column(Integer, nullable=False, server_default=text("0"))
    comment = Column(String(64), nullable=False)
    activated_status = Column(Integer, nullable=False,
                              server_default=text("0"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    activated_user = Column(String)

    __table_args__ = (
        Index('activated_dt_info_index', id,
              unique=True),
    )


class ActivatedMchInfo(Base):
    __tablename__ = 'activated_mch_info'

    id = Column(Integer, Sequence(
        'activated_mch_info_id_seq'), primary_key=True)
    mch_id = Column(BigInteger, nullable=False)
    payment_type = Column(Integer, nullable=False, server_default=text("0"))
    comment = Column(String(64), nullable=False)
    activated_status = Column(Integer, nullable=False,
                              server_default=text("0"))
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
    comment = Column(String(1024), nullable=False)
    auth_status = Column(Integer, nullable=False, server_default=text("0"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    auth_user = Column(String)

    __table_args__ = (
        Index('auth_dt_info_index', id,
              unique=True),
    )


class AuthMchInfo(Base):
    __tablename__ = 'auth_mch_info'

    id = Column(Integer, Sequence('auth_mch_info_id_seq'), primary_key=True)
    mch_id = Column(BigInteger, nullable=False)
    comment = Column(String(1024), nullable=False)
    auth_status = Column(Integer, nullable=False, server_default=text("0"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    auth_user = Column(String)

    __table_args__ = (
        Index('auth_mch_info_index', id,
              unique=True),
    )


class ActivatedMchEmailInfo(Base):
    __tablename__ = 'activated_mch_email_info'

    id = Column(Integer, Sequence(
        'activated_mch_email_info_id_seq'), primary_key=True)
    mch_id = Column(BigInteger, nullable=False)
    email = Column(String(64), nullable=False)
    comment = Column(String(64), nullable=False)
    status = Column(Integer, nullable=False, server_default=text("0"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))


class ActivatedDtEmailInfo(Base):
    __tablename__ = 'activated_dt_email_info'

    id = Column(Integer, Sequence(
        'activated_dt_email_info_id_seq'), primary_key=True)
    dt_id = Column(BigInteger, nullable=False)
    email = Column(String(64), nullable=False)
    comment = Column(String(64), nullable=False)
    status = Column(Integer, nullable=False, server_default=text("0"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))


class GatherMchsEmailInfo(Base):
    __tablename__ = 'gather_mchs_email_info'

    id = Column(Integer, Sequence(
        'gather_mchs_email_info_id_seq'), primary_key=True)
    dt_id = Column(BigInteger, nullable=False)
    email = Column(String(64), nullable=False)
    download_url = Column(String(128), nullable=False)
    status = Column(Integer, nullable=False, server_default=text("0"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))

    __table_args__ = (
        Index('gather_mchs_email_info_dt_id_index', dt_id),
    )


# 变更信息表
class ChangeRecord(Base):
    __tablename__ = 'change_record'
    id = Column(Integer, primary_key=True)
    mch_id = Column(BigInteger)
    bk_id = Column(BigInteger)
    dt_id = Column(BigInteger)
    change_type = Column(Integer)
    data_json = Column(TEXT)
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=True, default=text("now()"))
    status = Column(Integer)

# 日切变更信息表


class DailyCutRecord(Base):
    __tablename__ = 'daily_cut_record'
    id = Column(Integer, primary_key=True)
    role_id = Column(BigInteger)
    role_type = Column(String(64), nullable=False)
    record_json = Column(TEXT)
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=True, server_default=text("now()"))
    status = Column(Integer)


# class SysType(Base):
#     __tablename__ = 'sys_type'

#     id = Column(Integer, Sequence('sys_type_id_seq'), primary_key=True)

#     name = Column(String(64), nullable=False)
#     code = Column(String(64), nullable=False)
#     perfix_code = Column(String(64), nullable=False)

#     create_at = Column(DateTime, nullable=False)
#     update_at = Column(DateTime, nullable=True)

class SysType(Base):
    __tablename__ = 'sys_type'

    id = Column(Integer, Sequence('sys_type_id_seq'), primary_key=True)

    name = Column(String(64), nullable=False)
    code = Column(String(64), nullable=False)
    perfix_code = Column(String(64), nullable=False)

    create_at = Column(DateTime, nullable=False)
    update_at = Column(DateTime, nullable=True)
    __table_args__ = (UniqueConstraint(name, code),)


class MerchantRiskInfo(Base):
    """ 需要进件的商户风险信息表，包括连锁商户和普通商户 """
    __tablename__ = 'merchant_risk'
    id = Column(Integer, primary_key=True)
    # 商户id
    sys_id = Column(BigInteger)
    # 商户类型，目前仅有chain和mch
    sys_type_id = Column(String(64), nullable=False)
    # 来源,支付宝、微信或其他平台，每个商户对应到每个来源只有一条有效记录
    source = Column(String(64), nullable=False)
    # 是否有风险，0为无风险，1为有风险,2为大风险
    has_risk = Column(Integer)
    # 状态, 0为无效，1为有效
    status = Column(Integer, nullable=False)
    # 创建时间
    create_at = Column(DateTime, nullable=False)
    # 更新时间
    update_at = Column(DateTime, nullable=False)


class MerchantRiskItem(Base):
    """具体风险条目"""
    __tablename__ = 'merchant_risk_item'
    id = Column(Integer, primary_key=True)
    merchant_risk_id = Column(Integer)
    # 风险类型，riskinfo_cert_no,riskinfo_bank_card_no,riskinfo_business_license_no
    risk_type = Column(String(64), nullable=False)
    # 风险描述
    description = Column(String(100), nullable=True)
    # 风险内容详情， json数据格式，方便扩展
    content = Column(String(500), nullable=True)
    # 是否有风险，0为无风险，1为有风险,2为大风险
    has_risk = Column(Integer)
    # 状态, 0为无效，1为有效
    status = Column(Integer, nullable=False)
    # 创建时间
    create_at = Column(DateTime, nullable=False)
    # 更新时间
    update_at = Column(DateTime, nullable=False)


class TradeRiskInfo(Base):
    """交易风险信息表"""
    __tablename__ = 'trade_risk'
    id = Column(Integer, primary_key=True)
    #  角色id
    sys_id = Column(BigInteger)
    # 角色类型
    sys_type_id = Column(String(64), nullable=True)
    # 渠道号
    dt_id = Column(BigInteger, nullable=True)
    # uline订单号
    out_trade_no = Column(String(64), nullable=False)
    # 第三方订单号
    transaction_id = Column(String(64), nullable=True)
    # 平台， alipay, weixin....
    platform = Column(String(64), nullable=True)
    # 第三方pid
    platform_pid = Column(String(64), nullable=True)
    # 第三方平台编码, 冗余，和platform来确定平台费率通道
    channel_code = Column(String(64), nullable=True)
    # 第三方商户号
    sub_mch_id = Column(String(64), nullable=True)
    # 风险类型， 目前仅有欺诈
    risk_type = Column(String(64), nullable=True)
    # 风险描述
    description = Column(String(64), nullable=True)
    # 风险内容详情, 方便扩展，主要用于存储风险其他信息，json数据格式，如{"sourceId":"2088011993690428"}
    content = Column(TEXT, nullable=True)
    # 状态 1为待处理，2为处理结果，3忽略
    status = Column(Integer)
    # 处理结果, json数据，自己规定
    handle_result = Column(String(500), nullable=True)
    # 处理结果描述
    handler_message = Column(String(200), nullable=True)
    create_at = Column(DateTime, nullable=False)
    update_at = Column(DateTime, nullable=False)


class RiskControl(Base):
    """风控表"""
    __tablename__ = 'risk_control'
    id = Column(Integer, primary_key=True)
    sys_id = Column(BigInteger)
    sys_type_id = Column(String(64), nullable=True)
    credit = Column(String(200), nullable=True)
    pay = Column(String(200), nullable=True)
    settle = Column(String(200), nullable=True)
    create_at = Column(DateTime, nullable=False)
    update_at = Column(DateTime, nullable=False)


class InletAuthItem(Base):
    """进件审核条目表"""
    __tablename__ = "inlet_auth_items"
    id = Column(BigInteger, primary_key=True)
    sys_id = Column(BigInteger)
    # 条目对应目标类型，mch普通商户, dt渠道商, cs连锁门店, chain连锁商户
    sys_type_id = Column(String(64))
    # 进件审核列表显示名称，主要是为了区别商户名称变更
    sys_name = Column(String(64), nullable=True)
    # 简称
    sys_shortname = Column(String(64), nullable=True)
    # 对应渠道商信息
    dt_id = Column(BigInteger, nullable=True)
    dt_name = Column(String(64), nullable=True)
    bk_id = Column(BigInteger, nullable=True)
    # 更改前的商户信息，如果是新进件，则记录新进件的信息
    backup_content = Column(TEXT, nullable=True)
    # 关联对应的变更记录
    change_record_id = Column(BigInteger, nullable=False)
    # 进件的类型，1为新增，2为修改
    inlet_type = Column(SmallInteger, nullable=False)
    # 审核条目提交人id
    submitter_id = Column(BigInteger, nullable=False)
    # 审核条目提交人姓名
    submitter_name = Column(String(64))
    # 审核条目提交人类型,bk为银行人员，official为官方用户， chain:连锁商户, dt:渠道商，mch:普通商户，cs:连锁门店
    submitter_type = Column(String(10))
    # 审核状态
    auth_status = Column(Integer, nullable=False)
    # 审核信息
    auth_comment = Column(String(200), nullable=True)
    # 创建时间
    create_time = Column(DateTime, nullable=False)
    # 更新时间
    update_time = Column(DateTime, nullable=False)
    # 条目状态, 1为有效， 0位无效
    status = Column(Integer, nullable=False)
    # 条目是否为最新， 1位最新， 2位历史
    newest = Column(Integer, nullable=True)
    # 对公对私账户， 1为对公，2为对私
    balance_type = Column(SmallInteger, nullable=True)
