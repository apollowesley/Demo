#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlalchemy
from sqlalchemy import orm

from uline.model.uline.info import Discount, MchInletInfo, DtInletInfo


def get_mch_subsidize_info(session, query_args, page=0, page_size=10, fetchone=False):
    mch_query = generate_mch_subsidize_query(session, query_args)
    chain_query = generate_chain_subsidize_query(session, query_args)
    subsidize_query = mch_query.union_all(chain_query)

    total_num = subsidize_query.count()
    subsidize_query = subsidize_query.order_by(Discount.create_at.desc())
    offset = page * page_size
    if offset:
        subsidize_query = subsidize_query.offset(offset)
    if page_size:
        subsidize_query = subsidize_query.limit(page_size)
    data = subsidize_query.first() if fetchone else subsidize_query.all()
    return total_num, data


def generate_mch_subsidize_query(session, query_args):
    subsidize_query = session.query(Discount.role_id, MchInletInfo.mch_name.label('role_name'),
                                    MchInletInfo.mch_shortname.label('role_shortname'),
                                    Discount.valid, Discount.create_at, DtInletInfo.dt_id, DtInletInfo.dt_name,
                                    Discount.rate)
    subsidize_query = subsidize_query.join(MchInletInfo, MchInletInfo.mch_id == Discount.role_id)
    subsidize_query = subsidize_query.join(DtInletInfo, DtInletInfo.dt_id == MchInletInfo.dt_id)

    subsidize_query = subsidize_query.filter(Discount.role == 'mch')
    status = query_args.get('status', 0)
    if status:
        subsidize_query = subsidize_query.filter(Discount.valid == status)
    mch_id = query_args.get('mch_id', '')
    if mch_id:
        subsidize_query = subsidize_query.filter(
            Discount.role_id.cast(sqlalchemy.String).like('%{}%'.format(mch_id)))

    mch_name = query_args.get('mch_name', '')
    if mch_name:
        subsidize_query = subsidize_query.filter(MchInletInfo.mch_name.like('%{}%'.format(mch_name)))

    dt_id = query_args.get('dt_id', '')
    if dt_id:
        subsidize_query = subsidize_query.filter(
            MchInletInfo.dt_id.cast(sqlalchemy.String).like('%{}%'.format(dt_id)))

    dt_name = query_args.get('dt_name', '')
    if dt_name:
        subsidize_query = subsidize_query.filter(DtInletInfo.dt_name.like('%{}%'.format(dt_name)))
    return subsidize_query


def generate_chain_subsidize_query(session, query_args):
    chain_inlet_info = orm.aliased(DtInletInfo)
    subsidize_query = session.query(Discount.role_id, chain_inlet_info.dt_name.label('role_name'),
                                    chain_inlet_info.dt_short_name.label('role_shortname'),
                                    Discount.valid, Discount.create_at, DtInletInfo.dt_id, DtInletInfo.dt_name,
                                    Discount.rate)
    subsidize_query = subsidize_query.join(chain_inlet_info, chain_inlet_info.dt_id == Discount.role_id)
    subsidize_query = subsidize_query.join(DtInletInfo, DtInletInfo.dt_id == chain_inlet_info.parent_id)

    subsidize_query = subsidize_query.filter(Discount.role == 'chain')
    status = query_args.get('status', 0)
    if status:
        subsidize_query = subsidize_query.filter(Discount.valid == status)
    mch_id = query_args.get('mch_id', '')
    if mch_id:
        subsidize_query = subsidize_query.filter(Discount.role_id.cast(sqlalchemy.String).like('%{}%'.format(mch_id)))

    mch_name = query_args.get('mch_name', '')
    if mch_name:
        subsidize_query = subsidize_query.filter(chain_inlet_info.dt_name.like('%{}%'.format(mch_name)))

    dt_id = query_args.get('dt_id', '')
    if dt_id:
        subsidize_query = subsidize_query.filter(
            chain_inlet_info.parent_id.cast(sqlalchemy.String).like('%{}%'.format(dt_id)))

    dt_name = query_args.get('dt_name', '')
    if dt_name:
        subsidize_query = subsidize_query.filter(DtInletInfo.dt_name.like('%{}%'.format(dt_name)))
    return subsidize_query
