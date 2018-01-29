#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @author: leiyutian
# @createTime: 2017-06-02, 14:16:28 GMT+0800
# @description: description

from datetime import date, timedelta
import re


def query_mch_inlet_infos(db, conditions, offset, query_role=1):
    """获取商户进件信息

    Arguments:
        db {[type]} -- 数据库连接
        conditions {dict} -- 查询条件
        offset {int} -- 偏移量
        query_role {int} -- 查询角色， 1：渠道商，2.官方， 3. 银行, 4. 连锁商户；默认是渠道商1

        conditions:{
            auth_status: 审核条件，
            create_at_start： 商户创建起始时间，
            create_at_end：商户创建结束时间，
            dt_id：商户所属渠道商id，
            dt_name：商户所属渠道商名称，
            activated_status：商户激活状态
            mch_name： 商户名称
            mch_id：商户id
            short_name：商户简称
            is_cs：是否查询连锁门店
            cs_id：门店所属商户id
            cs_name：门店所属商户名称
            dt_sub_id：门店业务员
        }

    Returns:
        list -- 查询的到的数据列表
    """
    # 返回列表,过滤、分页
    query = "SELECT {} FROM {} where {} ORDER BY mch_inlet_info.create_at DESC OFFSET %(offset)s ROWS FETCH NEXT 10 ROWS ONLY;"
    select_colums = ""
    tables = ""
    is_cs = conditions.get('is_cs', False)
    if query_role in [4]:
        select_colums = """mch_inlet_info.mch_id, mch_inlet_info.mch_name, mch_inlet_info.mch_shortname,
                          mch_inlet_info.activated_status, mch_inlet_info.auth_status,mch_inlet_info.cs_id,
                          COUNT(*) OVER () AS total"""
        tables = """mch_inlet_info"""
    elif query_role in [1, 2, 3]:
        if is_cs:
            select_colums = """mch_inlet_info.mch_id,dt_user.dt_name,mch_inlet_info.mch_shortname,
                               mch_inlet_info.activated_status,mch_inlet_info.auth_status,bk_user.bk_type,mch_inlet_info.cs_id,
                               COUNT(*) OVER () AS total"""
            tables = """ mch_inlet_info  INNER JOIN dt_user  ON mch_inlet_info.cs_id=dt_user.dt_id INNER JOIN bk_user ON bk_user.bk_id=mch_inlet_info.bk_id"""
        else:
            select_colums = """mch_inlet_info.mch_id,mch_inlet_info.mch_name,mch_inlet_info.mch_shortname,
                           mch_inlet_info.activated_status,mch_inlet_info.auth_status,mch_inlet_info.cs_id,
                           dt_user.dt_name, COUNT(*) OVER () AS total"""
            tables = """ mch_inlet_info  INNER JOIN dt_user  ON mch_inlet_info.dt_id=dt_user.dt_id"""

    where_clauses = []

    auth_status = conditions.get('auth_status', None)
    # if query_role == 1:
    #     if auth_status == 1:
    #         auth_status = [1, 4]
    #     elif auth_status in [2, 3]:
    #         auth_status = [auth_status, ]
    if auth_status is not None:
        # if isinstance(auth_status, list):
        where_clauses.append("""mch_inlet_info.auth_status in %(auth_status)s""")
        conditions['auth_status'] = auth_status
        # else:
        #     where_clauses.append("""mch_inlet_info.auth_status=%(auth_status)s""")

    create_at_start = conditions.get('create_at_start', None)
    if not conditions.get('create_at_start', None):
        create_at_start = "2013-01-01"
    conditions['create_at_start'] = create_at_start

    create_at_end = conditions.get('create_at_end', None)
    if not create_at_end:
        create_at_end = date.today()
        # 因为end是0时0分,将它续一天┑(￣Д ￣)┍
    # if create_at_end:
    create_at_end += timedelta(days=1)
    conditions['create_at_end'] = create_at_end

    where_clauses.append(
        """(mch_inlet_info.create_at BETWEEN %(create_at_start)s::TIMESTAMP AND %(create_at_end)s::TIMESTAMP)""")
    conditions['create_at_start'] = create_at_start
    conditions['create_at_end'] = create_at_end

    if conditions.get('dt_id', None) is not None:
        where_clauses.append("""mch_inlet_info.dt_id=%(dt_id)s""")

    if conditions.get('dt_name', ''):
        where_clauses.append("""dt_user.dt_name ~ E%(dt_name)s""")
        conditions['dt_name'] = escape(conditions['dt_name'])

    if conditions.get('cs_name', ''):
        where_clauses.append("""dt_user.dt_name ~ E%(cs_name)s""")
        conditions['cs_name'] = escape(conditions['cs_name'])

    if conditions.get('activated_status', None) is not None:
        where_clauses.append("""mch_inlet_info.activated_status=%(activated_status)s""")

    if conditions.get('bk_id', None) is not None:
        where_clauses.append("""mch_inlet_info.bk_id=%(bk_id)s""")

    if conditions.get('mch_name', None):
        where_clauses.append("""mch_inlet_info.mch_name ~ E%(mch_name)s""")
        conditions['mch_name'] = escape(conditions['mch_name'])

    if conditions.get('mch_id', None):
        where_clauses.append("""mch_inlet_info.mch_id::VARCHAR ~ E%(mch_id)s""")
        conditions['mch_id'] = escape(conditions['mch_id'])

    if conditions.get('short_name', None):
        where_clauses.append("""mch_inlet_info.mch_shortname ~ E%(short_name)s""")
        conditions['short_name'] = escape(conditions['short_name'])

    cs_id = conditions.get('cs_id', None)

    if is_cs:
        if cs_id:
            where_clauses.append("""mch_inlet_info.cs_id=%(cs_id)s""")
        else:
            where_clauses.append("""mch_inlet_info.cs_id NOTNULL""")
    else:
        where_clauses.append("""mch_inlet_info.cs_id ISNULL""")

    if conditions.get('dt_sub_id', None) is not None:
        where_clauses.append("""mch_inlet_info.dt_sub_id=%(dt_sub_id)s""")
    conditions['offset'] = offset
    where_str = " AND ".join(where_clauses)

    query = query.format(select_colums, tables, where_str)
    ret = db.selectSQL(query, conditions, fetchone=False, use_dict=False)

    return ret


def escape(value):
    """
    转义字符串以在sql语句正则查询中用
    """
    if value:
        # 如果是数字，转化成字符串
        if not isinstance(value, basestring):
            value = str(value)
        # re.escape 在这里满足不了需求.
        # 1. 需要应对unicode和ascii字符。
        # 2. 需要双重转义, postgresql 正则需要\\[特殊字符] 这样的格式。
        return re.sub(r"[(){}\[\].*?|^$\\+-]", r"\\\\\g<0>", value)
    else:
        # 查询字符串是None， 或是空'', 我们认为是一样的
        return ''


def get_chain_info(db, cs_id):
    sql = """select dt_inlet_info.dt_short_name from dt_inlet_info where dt_id=%s"""
    chain_info = db.selectSQL(sql, (cs_id,))
    if chain_info:
        return chain_info[0]
