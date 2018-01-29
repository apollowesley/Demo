#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @author: leiyutian
# @createTime: 2017-06-05, 10:10:09 GMT+0800
# @description: 官方后台连锁商户进件信息列表

import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import BkAdminHandler
from .form import ChainSearch
from datetime import timedelta
from uline.settings import QR_SCAN_URL
from uline.settings import FEATURE_SWITCH
from uline.public.distributor_util import query_dt_inlet_info
from uline.public import auth_util, constants
from uline.public.permit import check_permission
from uline.model.uline.user import Employee
from uline.model.uline.info import UserProfile
from sqlalchemy import desc
from uline.model.uline.other import AuthDtInfo
from uline.model.uline.base import uline_session


class ChainInletIndexHandler(BkAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        self.open_review = FEATURE_SWITCH['REVIEW']
        self.form = ChainSearch(self)
        # 查询参数不合法
        if not self.form.validate() and self.form.activated_status.data != None:
            self.redirect('/bank/inlet/chain')
            return
        pageindex = int(self.get_argument("p", 1))
        self.data, self.total_number = self.db_execute(self.form, (pageindex - 1) * 10)

    def generate_unchanged_render_params(self):
        return {
            'print_status': auth_util.print_auth_status
        }

    def get(self):
        open_review = FEATURE_SWITCH['REVIEW']
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('bank/inlet/chain.html', navigate_html=navigate_html, data=self.data, form=self.form,
                    total_num=self.total_number, QR_SCAN_URL=QR_SCAN_URL, open_review=open_review,
                    expand_type=0)

    def post(self):
        open_review = FEATURE_SWITCH.get['REVIEW']
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('bank/inlet/chain.html', navigate_html=navigate_html, data=self.data, form=self.form,
                    total_num=self.total_number, QR_SCAN_URL=QR_SCAN_URL, open_review=open_review,
                    expand_type=0)

    def db_execute(self, form, offset):
        # 返回列表,过滤、分页
        create_at_start = form.create_at_start.data or None
        create_at_end = form.create_at_end.data or None
        activated_status = form.activated_status.data or None
        dt_name = form.dt_name.data or None
        auth_status = form.auth_status.data or None
        dt_id = form.dt_id.data or None
        parent_id = form.parent_id.data or None
        parent_name = form.parent_name.data or None
        expand_type = form.expand_type.data or None
        bk_id = form.bk_id.data or None
        bk_name = form.bk_name.data or None

        # if auth_status == 0:
        #     auth_status = tuple(list([int(key) for key in constants.AUTH_STATUS]))
        # if not auth_status:
        #     auth_status = None
        if not self.open_review and auth_status == 3:
            auth_status = (constants.AUTH_STATUS_DENY, constants.AUTH_STATUS_FIRST_DENY)
        elif not self.open_review and auth_status == 1:
            auth_status = (constants.AUTH_STATUS_SUBMIT, constants.AUTH_STATUS_PREVIEWD)
        else:
            auth_status = (auth_status,)

        conditions = {
            'create_at_start': create_at_start,
            'create_at_end': create_at_end,
            'activated_status': activated_status,
            'dt_name': self.db.escape(dt_name),
            'auth_status': auth_status,
            'dt_id': self.db.escape(dt_id),
            'offset': offset,
            'is_chain': True,
            'parent_id': self.db.escape(parent_id),
            'parent_name': self.db.escape(parent_name),

            'expand_type': expand_type,
            'bk_id': self.db.escape(bk_id),
            'bk_name': self.db.escape(bk_name),
        }

        query = """SELECT dt.dt_id,
                dt.dt_name,
                bk_user.bk_type,
                dt.dt_short_name,
                dt_user.dt_name,
                dt.activated_status,
                dt.auth_status,
                COUNT(*) OVER () AS total
               FROM dt_inlet_info as dt
               INNER JOIN dt_user ON dt.parent_id=dt_user.dt_id
               INNER JOIN bk_user ON dt.bk_id = bk_user.bk_id
               WHERE (dt_user.dt_name::VARCHAR ~ E%(parent_name)s OR %(parent_name)s = '')
               AND (dt.activated_status=%(activated_status)s OR %(activated_status)s IS NULL )
               AND (dt.auth_status in %(auth_status)s OR %(auth_status)s IS NULL )
               AND (dt.dt_name ~ E%(dt_name)s OR %(dt_name)s = '')
                 AND (dt.dt_id::VARCHAR ~ E%(dt_id)s OR %(dt_id)s = '')
               AND (dt.create_at BETWEEN %(create_at_start)s::TIMESTAMP AND %(create_at_end)s::TIMESTAMP
                            OR %(create_at_start)s IS NULL OR %(create_at_end)s IS NULL )
               AND dt.parent_id IS NOT NULL

                AND (dt.bk_id IN (SELECT bk_id FROM bk_user WHERE (bk_type = %(expand_type)s OR %(expand_type)s IS NULL)
                                                    AND  (bk_id::VARCHAR ~ E%(bk_id)s OR %(bk_id)s IS NULL) AND (bk_name ~ E%(bk_name)s OR %(bk_name)s IS NULL) ))

               ORDER BY dt.create_at desc
               OFFSET %(offset)s ROWS FETCH NEXT 10 ROWS ONLY

               """

        ret = self.db.selectSQL(query, conditions, fetchone=False)
        if ret:
            ret_list = []
            risk_sql = """select count(*) from merchant_risk
                                       where sys_id=%s and sys_type_id=%s and has_risk>0 and status=1"""
            for dt_inlet_info in ret:
                dt_inlet_info = list(dt_inlet_info)
                dt_id = dt_inlet_info[0]
                # auth_info = self.auth_userid(dt_id)
                auth_info = self.auth_userid(dt_id)
                # auth_user = ""
                # bk_id = []
                # if auth_info:
                # bk_id = auth_info[0]
                # bk_id = auth_info
                # auth_user = auth_info[1]

                current_user = self.session["employee_id"]
                # current_user = self.session.get('bk_id')
                # auth_user = 0 if bk_id == current_user else 1
                auth_user = 0 if current_user in auth_info else 1
                dt_inlet_info.insert(-1, auth_user)

                has_risk = self.db.selectSQL(risk_sql, (dt_id, 'chain'))[0]
                dt_inlet_info.insert(-1, has_risk)

                ret_list.append(tuple(dt_inlet_info))
            return ret_list, ret_list[0][-1]  # 数据,总数
        return ret, 0

    def auth_userid(self, dt_id):
        auth_dt_info = uline_session.query(AuthDtInfo).filter(
            AuthDtInfo.dt_id == dt_id).order_by(desc(AuthDtInfo.create_at)).first()
        if auth_dt_info:
            email = auth_dt_info.auth_user
            sys_type_id = self.session["sys_type_id"]
            last_employee = uline_session.query(Employee).\
                join(UserProfile, UserProfile.id == Employee.user_id).\
                filter(UserProfile.email == email, Employee.sys_type_id == sys_type_id).all()
            if last_employee:
                ids = [employee.id for employee in last_employee]
                return ids
            else:
                return []
        else:
            return []

        #
        # selSql = """select bk_user.bk_id,auth_user ,dt_id
        #             from auth_dt_info as a1 INNER JOIN  bk_user on bk_user.email=a1.auth_user
        #             where dt_id=%s and not exists(select 1 from auth_dt_info as a2
        #                 where a2.dt_id= a1.dt_id and a2.create_at > a1.create_at);"""
        # db_ret = self.db.selectSQL(selSql, (dt_id,))
        # if db_ret:
        #     return db_ret
