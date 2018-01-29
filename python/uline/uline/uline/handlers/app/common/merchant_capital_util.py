#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date, timedelta

import sqlalchemy

from uline.model.uline.d0 import D0Withdraw
from uline.model.uline.info import MchInletInfo, DtInletInfo
from uline.model.uline.clear import MchClearInfo


D0_WITHDRAW_INFO = {1:'等待划付',2:'划付成功',3:'划付失败'}

def get_merchant_capital_list(session, query_condictions, page=0, page_size=10, fetchone=False):
    # 暂时只认d0提现
    create_at_start = query_condictions.get('create_at_start', None)
    if not create_at_start:
        create_at_start = '2015-01-01'

    # 结束时间
    create_at_end = query_condictions.get('create_at_end', None)
    if not create_at_end:
        create_at_end = date.today()
    create_at_end += timedelta(days=1)

    mch_clear_no = query_condictions.get('mch_clear_no', None)

    # 账户类型 支付宝 或 微信
    channel = query_condictions.get('channel', None)

    # 商户名称
    mch_name = query_condictions.get('mch_name', None)
    mch_shortname = query_condictions.get('mch_shortname', None)
    # 商户ID
    mch_id = query_condictions.get('mch_id', None)

    # 渠道商名称
    dt_name = query_condictions.get('dt_name', None)
    # 渠道商id
    dt_id = query_condictions.get('dt_id', None)

    # 结算卡号
    settle_card = query_condictions.get('settle_card', None)

    # 划付状态
    pay_status = query_condictions.get('pay_status', None)

    # 暂时只有提现信息

    withdraw_query = session.query(MchClearInfo.create_at, MchClearInfo.mch_clear_no, MchClearInfo.business_type,
                                   MchClearInfo.channel, MchClearInfo.trade_amount, MchInletInfo.mch_name,
                                   MchInletInfo.mch_shortname, D0Withdraw.rcvacctname, D0Withdraw.rcvacctno,
                                   MchInletInfo.mch_id, D0Withdraw.rcvbanksettleno, D0Withdraw.rcvbankname,
                                   D0Withdraw.pay_status, DtInletInfo.dt_id, DtInletInfo.dt_name, MchClearInfo.remarks,
                                   MchInletInfo.cs_id
                                   )
    withdraw_query = withdraw_query.join(D0Withdraw,
                                         D0Withdraw.d0_trand_id.cast(sqlalchemy.String) == MchClearInfo.out_trade_no)
    withdraw_query = withdraw_query.join(MchInletInfo, MchInletInfo.mch_id == MchClearInfo.mch_id)

    withdraw_query = withdraw_query.join(DtInletInfo, DtInletInfo.dt_id == MchInletInfo.dt_id)

    if dt_name:
        withdraw_query = withdraw_query.filter(DtInletInfo.dt_name.like("%{}%".format(dt_name)))

    if dt_id:
        withdraw_query = withdraw_query.filter(D0Withdraw.dt_id.cast(sqlalchemy.String).like("%{}%".format(dt_id)))

    withdraw_query = withdraw_query.filter(MchClearInfo.create_at > create_at_start).filter(
        MchClearInfo.create_at < create_at_end)

    withdraw_query = withdraw_query.filter(MchClearInfo.business_type == 3)

    if mch_clear_no:
        withdraw_query = withdraw_query.filter(MchClearInfo.mch_clear_no == mch_clear_no)

    if channel:
        withdraw_query = withdraw_query.filter(D0Withdraw.channel == channel)

    if pay_status:
        withdraw_query = withdraw_query.filter(D0Withdraw.pay_status == pay_status)

    if mch_name:
        withdraw_query = withdraw_query.filter(MchInletInfo.mch_name.like("%{}%".format(mch_name)))

    if mch_shortname:
        withdraw_query = withdraw_query.filter(MchInletInfo.mch_shortname.like("%{}%".format(mch_shortname)))

    if mch_id:
        withdraw_query = withdraw_query.filter(MchClearInfo.mch_id.cast(sqlalchemy.String).like("%{}%".format(mch_id)))
    if settle_card:
        withdraw_query = withdraw_query.filter(D0Withdraw.rcvacctno == settle_card)

    all_count = withdraw_query.count()
    withdraw_query = withdraw_query.order_by(MchClearInfo.create_at.desc())
    withdraw_query = withdraw_query.offset(page * page_size)
    if page_size > 0:
        withdraw_query = withdraw_query.limit(page_size)
    return all_count, withdraw_query.first() if fetchone else withdraw_query.all()


def get_capital_pay_status(business_type, pay_status):
    if business_type == 3:
        return D0_WITHDRAW_INFO.get(int(pay_status), '')
    else:
        return ''