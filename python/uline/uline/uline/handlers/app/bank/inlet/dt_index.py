# -*- coding: utf-8 -*-
import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import BkAdminHandler
from .form import DistributorSearch
from datetime import timedelta
from uline.settings import QR_SCAN_URL
from uline.settings import FEATURE_SWITCH
from uline.public.permit import check_permission
from uline.model.uline.user import Employee
from uline.model.uline.info import UserProfile
from uline.model.uline.base import uline_session


class DistributorInletIndexHandler(BkAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        self.form = DistributorSearch(self)
        # 查询参数不合法
        if not self.form.validate() and self.form.activated_status.data != None:
            self.redirect('/bank/inlet/dt')
            return
        pageindex = int(self.get_argument("p", 1))
        self.data, self.total_number = self.db_execute(
            self.form, (pageindex - 1) * 10)
        self.open_review = FEATURE_SWITCH['REVIEW']

    def get(self):
        open_review = FEATURE_SWITCH['REVIEW']
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('bank/inlet/distributor.html', navigate_html=navigate_html, data=self.data, form=self.form,
                    total_num=self.total_number, QR_SCAN_URL=QR_SCAN_URL, open_review=open_review,
                    expand_type=0)

    def post(self):
        open_review = FEATURE_SWITCH.get['REVIEW']
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('bank/inlet/distributor.html', navigate_html=navigate_html, data=self.data, form=self.form,
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
        bk_id = form.bk_id.data or None
        bk_name = form.bk_name.data or None
        expand_type = form.expand_type.data or None

        # 因为end是0时0分,将它续一天┑(￣Д ￣)┍
        if create_at_end:
            create_at_end += timedelta(days=1)

        query = """SELECT dt.dt_id,
                           dt.dt_name,
                           dt.activated_status,
                           dt.auth_status,
                           bk_user.bk_type,
                           z.auth_user,
                           COUNT(*) OVER () AS total
                        FROM dt_inlet_info as dt,
                        (select auth_user ,dt_id from auth_dt_info as a1 where not exists(select 1 from auth_dt_info as a2
                        where a2.dt_id= a1.dt_id and a2.create_at > a1.create_at)) as z,bk_user
                        WHERE (dt.dt_id = z.dt_id)
                         AND (bk_user.bk_id=dt.bk_id)
                          AND(dt.activated_status=%(activated_status)s OR %(activated_status)s IS NULL )
                          AND (dt.auth_status=%(auth_status)s OR %(auth_status)s IS NULL )
                          AND (dt.dt_name ~ E%(dt_name)s OR %(dt_name)s = '')
                          AND (dt.dt_id::VARCHAR ~ E%(dt_id)s OR %(dt_id)s = '')
                          AND (dt.parent_id is null)
                          AND (dt.create_at BETWEEN %(create_at_start)s::TIMESTAMP AND %(create_at_end)s::TIMESTAMP OR %(create_at_start)s IS NULL OR %(create_at_end)s IS NULL )

                        AND (dt.bk_id IN (SELECT bk_id FROM bk_user WHERE (bk_type = %(expand_type)s OR %(expand_type)s IS NULL)
                                                    AND  (bk_id::VARCHAR ~ E%(bk_id)s OR %(bk_id)s IS NULL) AND (bk_name ~ E%(bk_name)s OR %(bk_name)s IS NULL) ))

                        ORDER BY dt.create_at desc
                        OFFSET %(offset)s ROWS FETCH NEXT 10 ROWS ONLY"""

        ret = self.db.selectSQL(query, {
            'activated_status': activated_status,
            'auth_status': auth_status,
            'dt_name': self.db.escape(dt_name),
            'dt_id': self.db.escape(dt_id),
            'create_at_start': create_at_start,
            'create_at_end': create_at_end,

            'expand_type': expand_type,
            'bk_id': self.db.escape(bk_id),
            'bk_name': self.db.escape(bk_name),

            'offset': offset}, fetchone=False)  # 每页显示10条数据
        if ret:
            ret_list = []
            for i in ret:
                i = list(i)
                bk_id = self.auth_userid(i[-2])
                # current_user = self.session.get('bk_id')
                current_user = self.session.get('employee_id')
                # i[-2] = 0 if bk_id == current_user else 1
                i[-2] = 0 if current_user in bk_id else 1
                ret_list.append(tuple(i))
            return ret_list, ret_list[0][-1]  # 数据,总数
        return ret, 0

    def auth_userid(self, email):
        # selSql = """select bk_id from bk_user where email=%s"""
        # db_ret = self.db.selectSQL(selSql, (email,))
        # if db_ret:
        #     return db_ret[0]

        sys_type_id = self.session["sys_type_id"]
        last_employee = uline_session.query(Employee).join(UserProfile, UserProfile.id == Employee.user_id). \
            filter(UserProfile.email == email, Employee.sys_type_id == sys_type_id).all()
        if last_employee:
            ids = [employee.id for employee in last_employee]
            return ids
        else:
            return []
