# -*- coding: utf-8 -*-

from __future__ import division
from uline.public.baseDB import DbClient

db = DbClient()


# 根据连锁商户的id，查询上级渠道商的id
def get_dt_id_for_chain_id(chain_id):
    query = """
        select parent_id from dt_inlet_info where dt_id = %s;
    """
    return db.selectSQL(query, (chain_id,), fetchone=True)


# 根据连锁商户id，查询上级渠道商的名称
def get_dt_name_for_chain_id(chain_id):
    dt_id = get_dt_id_for_chain_id(chain_id)
    query = """
        select dt_name from dt_user where dt_id = %s;
    """
    return db.selectSQL(query, (dt_id,), fetchone=True)


# 根据连锁门店的id，查询上级连锁商户的id
def get_chain_id_for_mch_id(mch_id):
    query = """
        select cs_id from mch_inlet_info where mch_id = %s;
    """
    return db.selectSQL(query, (mch_id,), fetchone=True)


# 根据连锁门店的id，查询上级连锁商户的简称
def get_chain_name_for_mch_id(mch_id):
    chain_id = get_chain_id_for_mch_id(mch_id)
    query = """
        select dt_short_name from dt_inlet_info where dt_id = %s;
    """
    ret = db.selectSQL(query, (chain_id,), fetchone=True)
    if ret:
        return ret
    else:
        return ('',)
