#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '11/4/16'
from sqlalchemy import (
    BigInteger, Column, DateTime, Date,
    Integer, String, text, Sequence, Index, SmallInteger, ForeignKey
)
from uline_api.model.uline.base import Model as Base


class BalanceBankInfo(Base):
    __tablename__ = 'balance_bank_info'

    id = Column(
        Integer,
        Sequence('balance_bank_info_id_seq'),
        primary_key=True
    )
    bank_name = Column(String(64), nullable=False)
    bank_no = Column(String(64), nullable=False)

    __table_args__ = (
        Index('balance_bank_info_index', id),
    )

    @classmethod
    def get_bank_no(cls, bank_name):
        bank = cls.get_by(bank_name=bank_name).first()
        if bank is None:
            return None
        return bank.bank_no

    @classmethod
    def validate_bank_no(cls, bank_no):
        bank = cls.get_by(bank_no=bank_no).first()
        if bank is None:
            return False
        return True


class DtInletInfo(Base):
    __tablename__ = 'dt_inlet_info'

    dt_id = Column(BigInteger, primary_key=True)
    dt_name = Column(String(64), nullable=False)
    dt_type = Column(SmallInteger, nullable=False,
                     server_default=text("1"), default=1)
    dt_short_name = Column(String(64))
    province = Column(String(32), nullable=False)
    city = Column(String(32), nullable=False)
    address = Column(String(255), nullable=False)
    contact = Column(String(20), nullable=False)
    mobile = Column(String(11), nullable=False)
    service_phone = Column(String(15))
    email = Column(String(64), nullable=False)
    id_card_img_f = Column(String(200), nullable=False)
    id_card_img_b = Column(String(200), nullable=False)
    auth_status = Column(Integer, nullable=False)
    activated_status = Column(Integer, nullable=False)
    auth_at = Column(DateTime)
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))
    u_ind_code = Column(String(40))
    wx_ind_code = Column(String(40))
    ali_ind_code = Column(String(40))
    old_ind_code = Column(String(40))
    jd_ind_code = Column(String(40))

    license_num = Column(String(32), nullable=True)
    license_type = Column(String(32), nullable=True)
    license_start_date = Column(Date, nullable=True)
    license_end_date = Column(Date)
    license_period = Column(SmallInteger)
    license_scope = Column(String(500))
    license_img = Column(String(200), nullable=True)
    parent_id = Column(BigInteger)  # 上级渠道商的ID，如果为空说明不是连锁店
    wx_channel_id = Column(String(32), nullable=True)  # 微信端渠道号
    use_bank_channel_id = Column(SmallInteger, nullable=False,  # 是否使用银行的渠道号
                                 server_default=text("1"), default=1)
    wx_app_channel_id = Column(String(32), nullable=True)  # 微信端渠道号

    dt_sub_id = Column(BigInteger, nullable=True)  # 业务员id
    notify_url = Column(String(200))
    pay_notify_url = Column(String(200))
    chain_wechat_news = Column(Integer, server_default=text("1"))
    bk_id = Column(BigInteger, ForeignKey("bk_user.bk_id"), nullable=True)  # 所属银行id
    activate_email_tag = Column(Integer, server_default=text("1"))  # 1 为发送给商户,2为发送给渠道商

    __table_args__ = (
        Index('dt_inlet_info_email_uindex', email, unique=False),
        Index('dt_inlet_info_index', dt_id)
    )


class DtPayment(Base):
    __tablename__ = 'dt_payment'

    id = Column(Integer, Sequence('dt_payment_id_seq'), primary_key=True)
    dt_id = Column(BigInteger, nullable=False)
    # 渠道的结算费率,由银行设置
    settle_rate = Column(Integer, nullable=True)
    # uline支付类型id
    uline_payment_id = Column(Integer, nullable=True)
    # uline支付码(方便聚合支付查询子商户号)
    uline_payment_code = Column(String(64), nullable=True)
    # uline清算配置表id,uline_settle表外键
    uline_settle_id = Column(Integer, nullable=True)
    # 兼容以前旧系统的trade_type(JSAPI,NATIVE...),将被废除
    trade_type = Column(String(64), nullable=True)
    # 进件三方（微信支付宝等等） 返回的子商户号
    thirdparty_mch_id = Column(String(64), nullable=True)
    # 提现费率
    withdraw_rate = Column(Integer, nullable=True)
    # 单笔提现手续费
    withdraw_fee = Column(Integer, nullable=True)
    payment_type = Column(Integer, nullable=False)
    payment_rate = Column(Integer, nullable=False)
    activated_status = Column(Integer, nullable=False)
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))
    news_push_open_status = Column(Integer, server_default=text("3"))

    __table_args__ = (
        Index('dt_payment_index', id,
              unique=True),
    )


class IndustryInfo(Base):
    __tablename__ = 'industry_info'

    id = Column(Integer, Sequence('industry_info_id_seq'), primary_key=True)
    industry_name = Column(String(200))
    industry_code = Column(
        String(40), nullable=False, server_default=text("0"))

    __table_args__ = (
        Index('industry_info_index', id, unique=True),
    )

    @classmethod
    def get_industry_code(cls, industry_name):
        industry = cls.get_by(industry_name=industry_name).first()
        if industry is None:
            return None
        return industry.industry_code


class MchInletInfo(Base):
    __tablename__ = 'mch_inlet_info'

    mch_id = Column(BigInteger, primary_key=True)
    mch_name = Column(String(64), nullable=False)
    mch_shortname = Column(String(64), nullable=False)
    dt_id = Column(BigInteger, nullable=False)
    province = Column(String(32), nullable=False)
    city = Column(String(32), nullable=False)
    district = Column(String(32), nullable=True)
    address = Column(String(255), nullable=False)
    contact = Column(String(20), nullable=False)
    mobile = Column(String(11), nullable=False)
    service_phone = Column(String(15), nullable=False)
    email = Column(String(64), nullable=False)
    id_card_img_f = Column(String(200), nullable=False)
    id_card_img_b = Column(String(200), nullable=False)
    auth_status = Column(Integer, nullable=False, server_default=text("0"))
    activated_status = Column(
        Integer, nullable=False, server_default=text("0"))
    auth_at = Column(DateTime, nullable=False, server_default=text("now()"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))
    notify_count = Column(SmallInteger)
    notify_successed = Column(SmallInteger)
    notify_url = Column(String(200))
    u_ind_code = Column(String(40))
    wx_ind_code = Column(String(40))
    ali_ind_code = Column(String(40))
    old_ind_code = Column(String(40))
    jd_ind_code = Column(String(40))
    qq_ind_code = Column(String(40))

    license_num = Column(String(32), nullable=True)
    license_type = Column(String(32), nullable=True)
    license_start_date = Column(Date, nullable=True)
    license_end_date = Column(Date)
    license_period = Column(SmallInteger)
    license_scope = Column(String(500))
    license_img = Column(String(200), nullable=True)

    annex_img1 = Column(String(200), nullable=True)
    annex_img2 = Column(String(200), nullable=True)
    annex_img3 = Column(String(200), nullable=True)
    annex_img4 = Column(String(200), nullable=True)
    annex_img5 = Column(String(200), nullable=True)

    # 银联字段
    head_name = Column(String(20), nullable=True)
    head_mobile = Column(String(15), nullable=True)
    img_with_id_card = Column(String(200), nullable=True)

    pay_notify_url = Column(String(200))
    cs_id = Column(BigInteger)  # 上级连锁店的ID，如果为空说明是普通商户不是门店
    dt_sub_id = Column(BigInteger)
    open_or_close = Column(Integer, server_default=text("1"))
    bk_id = Column(BigInteger, ForeignKey("bk_user.bk_id"), nullable=True)
    activate_email_tag = Column(Integer, server_default=text("1"))  # 1 为发送给商户,2为发送给渠道商

    head_type = Column(String(64), nullable=True)

    __table_args__ = (
        Index('mch_info_dt_sub_id_index', dt_sub_id),
        Index('mch_inlet_info_index', mch_id),
    )


class D0WithdrawPay(Base):
    __tablename__ = 'd0_withdraw_fee'

    id = Column(Integer, primary_key=True)
    role = Column(BigInteger, nullable=False)
    role_type = Column(String(10), nullable=False)
    wx = Column(Integer, nullable=True)
    alipay = Column(Integer, nullable=True)
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))


class MchInletToWxInfo(Base):
    __tablename__ = 'mch_inlet_to_wx_info'

    id = Column(
        Integer, Sequence('mch_inlet_to_wx_info_id_seq'), primary_key=True)
    mch_id = Column(BigInteger, nullable=False)
    return_msg = Column(String(64), nullable=False)
    return_code = Column(String(64), nullable=False)
    result_msg = Column(String(64), nullable=False)
    result_code = Column(String(64), nullable=False)
    create_at = Column(DateTime, nullable=False)


class MchPayment(Base):
    __tablename__ = 'mch_payment'

    id = Column(Integer, Sequence('mch_payment_id_seq'), primary_key=True)
    mch_id = Column(BigInteger, nullable=False)
    dt_id = Column(BigInteger, nullable=True)
    #  商户结算费率,由渠道设置
    settle_rate = Column(Integer, nullable=True)
    # uline支付类型id
    uline_payment_id = Column(Integer, nullable=True)
    # uline支付码(方便聚合支付查询子商户号)
    uline_payment_code = Column(String(64), nullable=True)
    # uline清算配置表id
    uline_settle_id = Column(Integer, nullable=True)
    # 兼容旧系统的trade_type(JSAPI,NATIVE...),将被废除
    trade_type = Column(String(64), nullable=True)
    # 进件三方（微信支付宝等等） 返回的子商户号
    thirdparty_mch_id = Column(String(64), nullable=True)
    # 提现费率
    withdraw_rate = Column(Integer, nullable=True)
    # 单笔提现手续费
    withdraw_fee = Column(Integer, nullable=True)
    payment_type = Column(Integer, nullable=False)
    payment_rate = Column(Integer, nullable=False)
    activated_status = Column(Integer, nullable=False)
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))
    open_status = Column(Integer, server_default=text("3"))

    __table_args__ = (
        Index('mch_payment_index', id,
              unique=True),
    )


class WxFixedRate(Base):
    __tablename__ = 'wx_fixed_rate'

    id = Column(Integer, Sequence('wx_fixed_rate_id_seq'), primary_key=True)
    rate = Column(Integer, nullable=False)
    payment_type = Column(Integer, nullable=False)
    create_at = Column(DateTime, nullable=False)


class MchBalance(Base):
    __tablename__ = 'mch_balance'

    mch_id = Column(BigInteger, primary_key=True)
    balance_type = Column(Integer, nullable=False, server_default=text("0"))
    balance_name = Column(String(64), nullable=False)
    bank_no = Column(String(16), nullable=False)
    balance_account = Column(String(64), nullable=False)
    balance_way = Column(Integer, nullable=False, server_default=text("0"))
    id_card_no = Column(String(20))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))

    __table_args__ = (
        Index('mch_balance_index', mch_id, unique=True),
    )


class DtBalance(Base):
    __tablename__ = 'dt_balance'

    dt_id = Column(BigInteger, primary_key=True)
    balance_type = Column(Integer, nullable=False)
    balance_name = Column(String(64), nullable=False)
    bank_no = Column(String(16), nullable=False)
    balance_account = Column(String(64))
    balance_way = Column(Integer, nullable=False, server_default=text("0"))
    id_card_no = Column(String(20))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))

    __table_args__ = (
        Index('dt_balance_index', dt_id, unique=True),
    )


class DtInletToWxInfo(Base):
    __tablename__ = 'dt_inlet_to_wx_info'

    id = Column(
        Integer, Sequence('dt_inlet_to_wx_info_id_seq'), primary_key=True)
    dt_id = Column(BigInteger, nullable=False)
    return_msg = Column(String(64), nullable=False)
    return_code = Column(String(64), nullable=False)
    result_msg = Column(String(64), nullable=False)
    result_code = Column(String(64), nullable=False)
    create_at = Column(DateTime, nullable=False)


class UlineIndustryInfo(Base):
    __tablename__ = 'industry_uline_info'

    id = Column(Integer, primary_key=True)
    industry_name = Column(String(200))
    industry_code = Column(
        String(40), nullable=False, server_default=text("0"))
    wx_ind_code = Column(String(40), nullable=False, server_default=text("0"))
    ali_ind_code = Column(String(40), nullable=False, server_default=text("0"))
    new_ali_ind_code = Column(String(40))
    status = Column(Integer, nullable=False)
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))
    jd_ind_code = Column(String(40), nullable=False, server_default=text("0"))

    __table_args__ = (
        Index('industry_uline_info_index', id, unique=True),
    )

    @classmethod
    def get_industry_code(cls, industry_code):
        industry = cls.get_by(industry_code=industry_code).first()
        if industry is None:
            return False
        return True

    @classmethod
    def get_wx_ali_jd_code(cls, industry_code):
        ''''''
        industry = cls.get_by(industry_code=industry_code).first()
        return industry.wx_ind_code, industry.new_ali_ind_code, industry.jd_ind_code


class IndustryAliInfo(Base):
    __tablename__ = 'industry_ali_info'

    id = Column(Integer, primary_key=True)
    industry_code = Column(String(40), nullable=False)
    industry_name = Column(String(200), nullable=False)
    status = Column(Integer, nullable=False, server_default=text("1"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))

    __table_args__ = (
        Index('industry_ali_info_index', industry_code, unique=True),
    )


class IndustryJDInfo(Base):
    __tablename__ = 'industry_jd_info'

    id = Column(Integer, primary_key=True)
    industry_code = Column(String(40), nullable=False)
    industry_name = Column(String(200), nullable=False)
    status = Column(Integer, nullable=False, server_default=text("1"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))

    __table_args__ = (
        Index('industry_jd_info_index', industry_code, unique=True),
    )


class IndustryWxInfo(Base):
    __tablename__ = 'industry_wx_info'

    id = Column(Integer, primary_key=True)
    industry_code = Column(String(40), nullable=False)
    industry_name = Column(String(200), nullable=False)
    status = Column(Integer, nullable=False, server_default=text("1"))
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))

    __table_args__ = (
        Index('industry_wx_info_index', industry_code, unique=True),
    )


class PayConfigInfo(Base):
    __tablename__ = 'pay_config_info'

    id = Column(Integer, primary_key=True)
    # 角色id
    role_id = Column(BigInteger, primary_key=False)
    # 角色类型，'mch'为商户，'dt'为渠道商，'chain'为连锁商户，'cs'为门店
    role_type = Column(String(20), nullable=False)
    # 配置类型，微信为jsapi_path,appid_config,subscribe_appid
    config_name = Column(String(30), nullable=False)
    # 配置的值
    config_value = Column(String(200), nullable=False)
    # 费率通道
    channel = Column(Integer, nullable=False)
    create_time = Column(DateTime, nullable=False)
    update_time = Column(DateTime, nullable=False)


class RoleExtensionInfos(Base):
    __tablename__ = 'role_info_extension'

    id = Column(BigInteger, primary_key=True)
    role_id = Column(BigInteger, primary_key=False)
    role_type = Column(String(20), nullable=False)
    extension_name = Column(String(30), nullable=False)
    extension_value = Column(String(200), nullable=False)
    create_time = Column(DateTime, nullable=False, server_default=text("now()"))
    update_time = Column(DateTime, nullable=False, server_default=text("now()"))

class UserProfile(Base):
    __tablename__ = 'user_profile'

    id = Column(BigInteger, Sequence('user_profile_id_seq', metadata=Base.metadata, start=1), primary_key=True)
    name = Column(String(64), nullable=False)
    city = Column(String(256), nullable=True)
    sex = Column(String(64), nullable=True)
    status = Column(Integer, nullable=False)
    wx_id = Column(String(64))
    wx_open_id = Column(String(64))
    email = Column(String(64), nullable=False)
    phone1 = Column(String(64), nullable=True)
    phone2 = Column(String(64), nullable=True)
    last_login = Column(DateTime)
    creator_id = Column(BigInteger, nullable=False)
    create_at = Column(DateTime, nullable=False)
    update_at = Column(DateTime, nullable=True)

    __table_args__ = (

        Index('user_profile_user_id_index', id),

    )


class EmployeeUserLog(Base):
    __tablename__ = 'employee_user_log'

    id = Column(Integer, Sequence('employee_user_log_id_seq'), primary_key=True)

    employee_id = Column(BigInteger, ForeignKey("employee.id"), nullable=False)
    comment = Column(String(1024), nullable=False)
    create_at = Column(DateTime, nullable=False)
    operate_id = Column(BigInteger, nullable=False)
    eutype = Column(SmallInteger, nullable=False)
    __table_args__ = (

        Index('employee_user_log_employee_id_index', employee_id),

    )

class UlinePayment(Base):

    __tablename__ = 'uline_payment'

    id = Column(Integer, primary_key=True)
    # uline支付通道名称,用于页面显示
    name = Column(String(64), nullable=False, default="", server_default='')
    # uline支付类型码, 代替trade_type
    payment_code = Column(String(64), nullable=False, default=0, server_default='')
    # 三方支付平台(wx:微信,ali:支付宝,jd:京东,yl:银联)
    pay_channel = Column(String(64), nullable=False, default="", server_default='')
    # 对应微信和支付宝的支付方式(JSAPI,NATIVE,WEB....)
    trade_type = Column(String(64), nullable=False, default="", server_default='')
    # 对应旧系统的payment_type,将被废除
    payment_type = Column(Integer, nullable=False, default=0, server_default='0')
    # 三方平台的结算费率,从platform_mch冗余过来
    settle_rate = Column(SmallInteger, nullable=False, default=0, server_default='0')
    # 状态:1:激活,0:未激活
    status = Column(SmallInteger, nullable=False, default=0, server_default='0')
    # 审核状态,1: 审核,0:未审核
    check_status = Column(SmallInteger, nullable=False, default=0, server_default='0')
    # 通道id
    channel_code = Column(Integer, nullable=False, default=0, server_default='0')
    # 三方支付平台注册id,platform_mch表外键
    platform_mch_id = Column(Integer, nullable=False, default=0, server_default='0')
    remark = Column(String(512), nullable=False, default="", server_default='')
    create_at = Column(DateTime, nullable=False, server_default=text("now()"))
    update_at = Column(DateTime, nullable=False, server_default=text("now()"))
