#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @author: leiyutian
# @createTime: 2017-06-05, 10:10:09 GMT+0800
# @description: 官方后台连锁商户进件信息列表

import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import OfclAdminHandler
from .form import ChainSearch
from datetime import timedelta
from uline.settings import QR_SCAN_URL
from uline.settings import FEATURE_SWITCH
from uline.public import auth_util
from uline.public.constants import BANK_TYPE
from uline.public.permit import check_permission


class ChainInletIndexHandler(OfclAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        self.form = ChainSearch(self)
        # 查询参数不合法
        if not self.form.validate() and self.form.activated_status.data is not None:
            self.render('official/inlet/chain')
            return
        self.open_review = FEATURE_SWITCH['REVIEW']
        pageindex = int(self.get_argument("p", 1))
        self.data, self.total_number = self.db_execute(self.form, (pageindex - 1) * 10)

    def generate_unchanged_render_params(self):
        return {
            'print_status': auth_util.print_auth_status
        }

    def get(self):
        open_review = FEATURE_SWITCH['REVIEW']
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('official/inlet/chain.html', navigate_html=navigate_html, data=self.data, form=self.form,
                    total_num=self.total_number, QR_SCAN_URL=QR_SCAN_URL, open_review=open_review)

    def post(self):
        open_review = FEATURE_SWITCH['REVIEW']
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('official/inlet/chain.html', navigate_html=navigate_html, data=self.data, form=self.form,
                    total_num=self.total_number, QR_SCAN_URL=QR_SCAN_URL, open_review=open_review)

    def db_execute(self, form, offset):
        create_at_start = form.create_at_start.data or None
        create_at_end = form.create_at_end.data or None
        activated_status = form.activated_status.data or None
        dt_name = form.dt_name.data or None
        auth_status = form.auth_status.data or None
        parent_id = form.parent_id.data or None
        parent_name = form.parent_name.data or None

        dt_id = form.dt_id.data or None
        bk_name = form.bk_name.data or None
        bk_id = form.bk_id.data or None
        expand_type = form.expand_type.data or None

        # 因为end是0时0分,将它续一天┑(￣Д ￣)┍
        if create_at_end:
            create_at_end += timedelta(days=1)

        query = """SELECT dt_inlet_info.dt_id,
                       dt_inlet_info.dt_name,
                       bu.bk_type,
                       dt_inlet_info.dt_short_name,
                       dt_user.dt_name,
                       dt_inlet_info.activated_status,
                       dt_inlet_info.auth_status,
                       COUNT(*) OVER () AS total
                    FROM dt_inlet_info
                    inner join bk_user as bu on bu.bk_id = dt_inlet_info.bk_id
                    inner join dt_user on dt_user.dt_id = dt_inlet_info.parent_id
                    WHERE (dt_inlet_info.activated_status=%(activated_status)s OR %(activated_status)s IS NULL )
                      AND (dt_inlet_info.auth_status=%(auth_status)s OR %(auth_status)s IS NULL )
                      AND (dt_inlet_info.dt_name ~ E%(dt_name)s OR %(dt_name)s = '')
                       AND (dt_inlet_info.parent_id is not null)
                      AND (dt_inlet_info.dt_id::VARCHAR ~ E%(dt_id)s OR %(dt_id)s = '')
                      AND (bu.bk_name ~ E%(bk_name)s or %(bk_name)s = '')
                      AND (bu.bk_id::VARCHAR  ~ E%(bk_id)s or %(bk_id)s = '')
                      AND (dt_inlet_info.parent_id::VARCHAR  ~ E%(parent_id)s OR %(parent_id)s = '')
                      AND (dt_user.dt_name ~ E%(parent_name)s or %(parent_name)s = '')
                      {and_sql}
                      AND ( dt_inlet_info.create_at BETWEEN %(create_at_start)s::TIMESTAMP
                                                    AND %(create_at_end)s::TIMESTAMP
                            OR %(create_at_start)s IS NULL OR %(create_at_end)s IS NULL
                          )
                    ORDER BY dt_inlet_info.create_at desc
                    OFFSET %(offset)s ROWS FETCH NEXT 10 ROWS ONLY"""

        and_sql = " and bu.bk_type = {0} ".format(expand_type)

        if expand_type in (BANK_TYPE.get("main"), BANK_TYPE.get("inter")):
            # 主银行和同业银行
            query = query.format(and_sql=and_sql)
        else:
            query = query.format(and_sql="")

        ret = self.db.selectSQL(query, {
            'create_at_start': create_at_start,
            'create_at_end': create_at_end,
            'activated_status': activated_status,
            'dt_name': self.db.escape(dt_name),
            'auth_status': auth_status,
            'dt_id': self.db.escape(dt_id),
            'bk_name': self.db.escape(bk_name),
            'bk_id': self.db.escape(bk_id),
            'parent_id': self.db.escape(parent_id),
            'parent_name': self.db.escape(parent_name),
            'offset': offset
        }, fetchone=False)  # 每页显示10条数据
        if ret:
            ret_list = []
            risk_sql = """select count(*) from merchant_risk
                       where sys_id=%s and sys_type_id=%s and has_risk>0 and status=1"""
            for dt_inlet_info in ret:
                dt_inlet_info = list(dt_inlet_info)
                dt_id = dt_inlet_info[0]
                has_risk = self.db.selectSQL(risk_sql, (dt_id, 'chain'))[0]
                dt_inlet_info.insert(-1, has_risk)
                ret_list.append(tuple(dt_inlet_info))
            return ret_list, ret_list[0][-1]  # 数据,总数
        return ret, 0  # 数据,总数
        # return ret, 0
