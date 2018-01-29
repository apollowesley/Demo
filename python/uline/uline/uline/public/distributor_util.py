#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @author: leiyutian
# @createTime: time
# @description: 渠道商相关公有方法

from datetime import date, timedelta
from .merchant_util import escape


def query_dt_inlet_info(db, conditions, offset, query_role=1, use_dict=False):
    """查询渠道进件信息
      Arguments:
        conditions {dict} -- 查询条件
        offset {int} -- 偏移量

      Keyword Arguments:
        query_role {int} -- 使用该方法的角色 (default: {1})
      """
    # 返回列表,过滤、分页
    where_clauses = []

    is_chain = conditions.get('is_chain', False)

    parent_name = conditions.get('parent_name', '')

    choose_columns = ""
    tables = ""
    if is_chain:
        choose_columns = """dt_inlet_info.dt_id, dt_inlet_info.dt_name,bk_user.bk_type, dt_inlet_info.dt_short_name,
                            dt_user.dt_name, dt_inlet_info.activated_status,dt_inlet_info.auth_status,
                            COUNT(*) OVER () AS total"""
        tables = "dt_inlet_info INNER JOIN dt_user ON dt_inlet_info.parent_id=dt_user.dt_id INNER JOIN bk_user ON bk_user.bk_id=dt_inlet_info.bk_id"
        if parent_name:
            where_clauses.append("dt_user.dt_name::VARCHAR ~ E%(parent_name)s")
    else:
        choose_columns = """dt_inlet_info.dt_id, dt_inlet_info.dt_name, dt_inlet_info.activated_status,
                      dt_inlet_info.auth_status, COUNT(*) OVER () AS total"""

    query = """SELECT {}
               FROM {}
               WHERE {}
               ORDER BY dt_inlet_info.create_at desc
               OFFSET %(offset)s ROWS FETCH NEXT 10 ROWS ONLY"""

    if conditions.get('activated_status', None):
        where_clauses.append(
            """dt_inlet_info.activated_status=%(activated_status)s""")

    auth_status = conditions.get('auth_status', None)
    if auth_status:
        where_clauses.append("""dt_inlet_info.auth_status in %(auth_status)s""")

    if conditions.get('dt_name', None):
        where_clauses.append("""dt_inlet_info.dt_name ~ E%(dt_name)s""")
        conditions['dt_name'] = escape(conditions['dt_name'])

    if conditions.get('dt_id', None):
        where_clauses.append("""dt_inlet_info.dt_id::VARCHAR ~ E%(dt_id)s""")
        conditions['dt_id'] = escape(conditions['dt_id'])

    if conditions.get('bk_id', None):
        where_clauses.append("""dt_inlet_info.bk_id::VARCHAR ~ E%(bk_id)s""")
        conditions['bk_id'] = escape(conditions['bk_id'])

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
        """(dt_inlet_info.create_at BETWEEN %(create_at_start)s::TIMESTAMP AND %(create_at_end)s::TIMESTAMP)""")
    conditions['create_at_start'] = create_at_start
    conditions['create_at_end'] = create_at_end

    if conditions.get('is_chain', False):
        parent_id = conditions.get('parent_id', '')
        if parent_id:
            where_clauses.append("""dt_inlet_info.parent_id=%(parent_id)s""")
        else:
            where_clauses.append("""parent_id NOTNULL""")
    else:
        where_clauses.append("""parent_id ISNULL""")

    where_str = " AND ".join(where_clauses)
    query = query.format(choose_columns, tables, where_str)

    conditions['offset'] = offset

    ret = db.selectSQL(query, conditions, fetchone=False, use_dict=use_dict)  # 每页显示10条数据
    return ret


def get_all_dt_info(cur, dt_id):
    pass
