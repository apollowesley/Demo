#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @author: leiyutian
# @createTime: 2017-06-06, 18:10:18 GMT+0800
# @description: 获取当前渠道商下的相关连锁商户

from tornado.web import authenticated
from uline.public import common

from uline.handlers.baseHandlers import DtAdminHandler
from uline.public.permit import check_permission

INDEX_PAGE_SIZE = 10


class ChainSearchHandler(DtAdminHandler):
    """处理查询子账户的请求"""

    @authenticated
    @check_permission
    def get(self):
        """
        根据名字获取子账户列表
        """
        dt_id = self.current_user
        name = self.get_argument('q', None)
        print name
        print dt_id
        # all_argument = self.get_argument('all', None)

        query = """SELECT dt_inlet_info.dt_id, dt_inlet_info.dt_name
                    FROM auth_dt_info inner join  dt_inlet_info on auth_dt_info.dt_id=dt_inlet_info.dt_id
                    where dt_inlet_info.parent_id=%(dt_id)s
                    and (dt_inlet_info.dt_name ~ E%(dt_name)s or %(dt_name)s ISNULL)
                    and auth_dt_info.auth_status=2
                    group by dt_inlet_info.dt_id
                    LIMIT %(limit)s;"""

        # if not all_argument:
        # query = query.filter(DtSubUser.status == 1)
        # sub_users = query.limit(INDEX_PAGE_SIZE).all()

        query_params = {
            'dt_id': dt_id,
            'dt_name': name,
            'limit': INDEX_PAGE_SIZE
        }
        result = self.db.selectSQL(query, query_params, fetchone=False)
        data = list()
        for each_inlet in result:
            data.append({'id': each_inlet[0], 'dt_name': each_inlet[1]})
        response = common.scc_rsp(code=200, msg='success')
        response['data'] = data
        response['total_count'] = len(data)
        self.write(response)
