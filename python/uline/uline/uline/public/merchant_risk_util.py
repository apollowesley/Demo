#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uline.model.uline.other import MerchantRiskItem, MerchantRiskInfo
from uline.public import constants
from uline.model.uline.info import MchInletInfo, DtInletInfo
from sqlalchemy import literal


def get_merchant_risk_info(session, query_condictions, page=0, page_size=10, fetchone=False):
    mch_risk_query = generate_mch_risk_query(query_condictions, session)
    chain_risk_query = generate_chain_risk_query(query_condictions, session)

    merchant_risk_subquery_info = mch_risk_query.union_all(chain_risk_query).subquery()

    merchant_risk_query = session.query(merchant_risk_subquery_info)

    all_count = merchant_risk_query.count()

    merchant_risk_query = merchant_risk_query.order_by(merchant_risk_subquery_info.columns.create_at.desc())
    merchant_risk_query = merchant_risk_query.offset(page * page_size)
    if page_size > 0:
        merchant_risk_query = merchant_risk_query.limit(page_size)
    return all_count, merchant_risk_query.first() if fetchone else merchant_risk_query.all()


def get_all_merchant_risk_item(session, query_conditions, page=0, page_size=10, fetchone=False):
    has_risk = query_conditions.get('has_risk', 0)
    has_risk -= 1
    risk_query = session.query(MerchantRiskItem.id.label('risk_id'),
                               MerchantRiskItem.risk_type.label('risk_type'),
                               MerchantRiskItem.description.label('description'),
                               MerchantRiskItem.has_risk.label('has_risk'),
                               MerchantRiskItem.update_at.label('update_at'),
                               MerchantRiskInfo.source.label('source'),
                               MerchantRiskInfo.sys_type_id.label('merchant_type'),
                               MerchantRiskItem.create_at.label('create_at'))
    risk_query = risk_query.distinct(MerchantRiskItem.description)
    # 是否有风险
    if has_risk > -1:
        risk_query = risk_query.filter(
            MerchantRiskItem.has_risk > 0 if has_risk else MerchantRiskItem.has_risk == has_risk)

    # 风险类型
    risk_type = query_conditions.get('risk_type', '')
    if risk_type:
        risk_query = risk_query.filter(MerchantRiskItem.risk_type == risk_type)

    # 风险内容
    risk_content = query_conditions.get('risk_content', '')
    if risk_content:
        risk_query = risk_query.filter(MerchantRiskItem.description.like("%{}%".format(risk_content)))

    risk_id = query_conditions.get('risk_id', '')
    if risk_id:
        risk_query = risk_query.filter(MerchantRiskItem.id == risk_id)
    # risk_query = risk_query.group_by(MerchantRiskItem.id, MerchantRiskItem.description)
    risk_query = risk_query.order_by(MerchantRiskItem.description, MerchantRiskItem.update_at.desc())
    risk_sub_query = risk_query.subquery()
    risk_query = session.query(risk_sub_query).order_by(risk_sub_query.columns.update_at.desc())
    all_count = risk_query.count()
    merchant_risk_query = risk_query.offset(page * page_size)
    if page_size > 0:
        merchant_risk_query = merchant_risk_query.limit(page_size)
    return all_count, merchant_risk_query.first() if fetchone else merchant_risk_query.all()


def generate_mch_risk_query(query_condictions, session):
    has_risk = query_condictions.get('has_risk', 0)
    has_risk -= 1
    risk_query = session.query(MerchantRiskItem.risk_type.label('risk_type'),
                               MerchantRiskItem.description.label('description'),
                               MerchantRiskItem.has_risk.label('has_risk'),
                               MerchantRiskItem.update_at.label('update_at'),
                               MchInletInfo.mch_id.label('merchant_id'),
                               MerchantRiskInfo.source.label('source'),
                               MerchantRiskInfo.sys_type_id.label('merchant_type'),
                               MerchantRiskItem.create_at.label('create_at'))
    risk_query = risk_query.join(MerchantRiskInfo, MerchantRiskInfo.id == MerchantRiskItem.merchant_risk_id).join(
        MchInletInfo, MchInletInfo.mch_id == MerchantRiskInfo.sys_id)
    # 是否有风险
    if has_risk > -1:
        risk_query = risk_query.filter(
            MerchantRiskItem.has_risk > 0 if has_risk else MerchantRiskItem.has_risk == has_risk)

    # 风险类型
    risk_type = query_condictions.get('risk_type', '')
    if risk_type:
        risk_query = risk_query.filter(MerchantRiskItem.risk_type == risk_type)

    # 风险内容
    risk_content = query_condictions.get('risk_content', '')
    if risk_content:
        risk_query = risk_query.filter(MerchantRiskItem.description.like("%{}%".format(risk_content)))

    # 商户id
    merchant_id = query_condictions.get('merchant_id', '')
    if merchant_id:
        risk_query = risk_query.filter(MerchantRiskInfo.sys_id == merchant_id)

    # 商户类型，chain 或 mch
    merchant_sys_type = query_condictions.get('merchant_sys_type', '')
    if merchant_sys_type:
        risk_query = risk_query.filter(MerchantRiskInfo.sys_type_id == merchant_sys_type)
    bk_id = query_condictions.get('bk_id', '')
    if bk_id:
        risk_query = risk_query.filter(MchInletInfo.bk_id == bk_id)

    risk_id = query_condictions.get('risk_id', '')
    if risk_id:
        risk_query = risk_query.filter(MerchantRiskItem.id == risk_id)
    risk_query = risk_query.filter(MerchantRiskInfo.status == 1)
    risk_query = risk_query.filter(MerchantRiskItem.status == 1)
    return risk_query


def generate_chain_risk_query(query_condictions, session):
    has_risk = query_condictions.get('has_risk', 0)
    has_risk -= 1
    risk_query = session.query(MerchantRiskItem.risk_type.label('risk_type'),
                               MerchantRiskItem.description.label('description'),
                               MerchantRiskItem.has_risk.label('has_risk'),
                               MerchantRiskItem.update_at.label('update_at'),
                               DtInletInfo.dt_id.label('merchant_id'),
                               MerchantRiskInfo.source.label('source'),
                               literal('chain').label('merchant_type'),
                               MerchantRiskItem.create_at.label('create_at'))

    risk_query = risk_query.join(MerchantRiskInfo, MerchantRiskInfo.id == MerchantRiskItem.merchant_risk_id).join(
        DtInletInfo, DtInletInfo.dt_id == MerchantRiskInfo.sys_id)
    # 是否有风险
    if has_risk > -1:
        risk_query = risk_query.filter(
            MerchantRiskItem.has_risk > 0 if has_risk else MerchantRiskItem.has_risk == has_risk)

    # 风险类型
    risk_type = query_condictions.get('risk_type', '')
    if risk_type:
        risk_query = risk_query.filter(MerchantRiskItem.risk_type == risk_type)

    # 风险内容
    risk_content = query_condictions.get('risk_content', '')
    if risk_content:
        risk_query = risk_query.filter(MerchantRiskItem.description.like("%{}%".format(risk_content)))

    # 商户id
    merchant_id = query_condictions.get('merchant_id', '')
    if merchant_id:
        risk_query = risk_query.filter(MerchantRiskInfo.sys_id == merchant_id)

    # 商户类型，chain 或 mch
    merchant_sys_type = query_condictions.get('merchant_sys_type', '')
    if merchant_sys_type:
        risk_query = risk_query.filter(MerchantRiskInfo.sys_type_id == merchant_sys_type)
    bk_id = query_condictions.get('bk_id', '')
    if bk_id:
        risk_query = risk_query.filter(DtInletInfo.bk_id == bk_id)

    risk_id = query_condictions.get('risk_id', '')
    if risk_id:
        risk_query = risk_query.filter(MerchantRiskItem.id == risk_id)

    risk_query = risk_query.filter(MerchantRiskInfo.status == 1)
    risk_query = risk_query.filter(MerchantRiskItem.status == 1)
    return risk_query


def print_merchant_risk_type(risk_type):
    return constants.RISK_TYPE_MAP.get(risk_type, '')


def get_merchaint_risk_type_msg(risk_type):
    return constants.RISK_INFO_MAP.get(risk_type, '')
