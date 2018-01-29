#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from uline_risk.model.uline.other import TradeRiskInfo
from uline_risk.model.uline.info import MchInletInfo, DtInletInfo


def get_trade_risk_info(session, query_condictions={}, page=0, page_size=10, fetchone=False):
    create_at_start = query_condictions.get('create_at_start', '')
    create_at_end = query_condictions.get('create_at_end', '')
    if not create_at_start:
        create_at_start = '2015-01-01'
    if not create_at_end:
        create_at_end = datetime.today()
    if isinstance(create_at_end, str):
        create_at_end = datetime.strptime(create_at_end, '%Y-%m-%d')
    create_at_end = create_at_end + timedelta(days=1)
    trade_risk_query = session.query(TradeRiskInfo.create_at, MchInletInfo.mch_name, MchInletInfo.mch_id,
                                     MchInletInfo.mch_shortname, DtInletInfo.dt_id, DtInletInfo.dt_name,
                                     TradeRiskInfo.platform, TradeRiskInfo.transaction_id, TradeRiskInfo.risk_type,
                                     TradeRiskInfo.description, TradeRiskInfo.out_trade_no, TradeRiskInfo.status,
                                     TradeRiskInfo.handler_message, TradeRiskInfo.id, TradeRiskInfo.sub_mch_id
                                     )
    trade_risk_query = trade_risk_query.join(MchInletInfo, MchInletInfo.mch_id == TradeRiskInfo.sys_id)
    trade_risk_query = trade_risk_query.join(DtInletInfo, DtInletInfo.dt_id == MchInletInfo.dt_id)
    trade_risk_query = trade_risk_query.filter(TradeRiskInfo.create_at > create_at_start).filter(
        TradeRiskInfo.create_at < create_at_end)

    handle_status = query_condictions.get('handle_status', 0)
    if handle_status:
        trade_risk_query = trade_risk_query.filter(TradeRiskInfo.status == handle_status)

    merchant_id = query_condictions.get('merchant_id', '')
    if merchant_id:
        trade_risk_query = trade_risk_query.filter(TradeRiskInfo.sys_id == merchant_id)

    merchant_name = query_condictions.get('merchant_name', '')
    if merchant_name:
        trade_risk_query = trade_risk_query.filter(MchInletInfo.mch_name.like('%{}%'.format(merchant_name)))

    merchant_shortname = query_condictions.get('merchant_shortname', '')
    if merchant_shortname:
        trade_risk_query = trade_risk_query.filter(MchInletInfo.mch_shortname.like('%{}%'.format(merchant_shortname)))

    dt_id = query_condictions.get('dt_id', '')
    if dt_id:
        trade_risk_query = trade_risk_query.filter(DtInletInfo.dt_id == dt_id)

    dt_name = query_condictions.get('dt_name', '')
    if dt_name:
        trade_risk_query = trade_risk_query.filter(DtInletInfo.dt_name.like('%{}%'.format(dt_name)))

    bk_id = query_condictions.get('bk_id', '')
    if bk_id:
        if isinstance(bk_id, list):
            trade_risk_query = trade_risk_query.filter(MchInletInfo.bk_id.in_(bk_id))
        else:
            trade_risk_query = trade_risk_query.filter(MchInletInfo.bk_id == bk_id)

    risk_id = query_condictions.get('risk_id', '')
    if risk_id:
        trade_risk_query = trade_risk_query.filter(TradeRiskInfo.id == risk_id)

    all_count = trade_risk_query.count()
    trade_risk_query = trade_risk_query.order_by(TradeRiskInfo.create_at.desc())
    trade_risk_query = trade_risk_query.offset(page * page_size)
    if page_size > 0:
        trade_risk_query = trade_risk_query.limit(page_size)
    return all_count, trade_risk_query.first() if fetchone else trade_risk_query.all()
