# -*- coding: utf-8 -*-
import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import OfclAdminHandler
from .form import DistributorSearch
from datetime import timedelta
from uline.settings import FEATURE_SWITCH
from uline.public.constants import BANK_TYPE
from uline.public.permit import check_permission


class DistributorInletIndexHandler(OfclAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        self.form = DistributorSearch(self)
        # 查询参数不合法
        if not self.form.validate() and self.form.activated_status.data != None:
            self.redirect('/official/inlet/dt')
            return
        pageindex = int(self.get_argument("p", 1))
        self.data, self.total_number = self.db_execute(
            self.form, (pageindex - 1) * 10)

    def get(self):
        open_review = FEATURE_SWITCH['REVIEW']
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('official/inlet/distributor.html', navigate_html=navigate_html, data=self.data, form=self.form,
                    total_num=self.total_number, open_review=open_review)

    def post(self):
        open_review = FEATURE_SWITCH['REVIEW']
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('official/inlet/distributor.html', navigate_html=navigate_html, data=self.data, form=self.form,
                    total_num=self.total_number, open_review=open_review)

    def db_execute(self, form, offset):
        """
        """
        # 返回列表,过滤、分页
        create_at_start = form.create_at_start.data or None
        create_at_end = form.create_at_end.data or None
        activated_status = form.activated_status.data or None
        dt_name = form.dt_name.data or None
        auth_status = form.auth_status.data or None
        dt_id = form.dt_id.data or None
        bk_name = form.bk_name.data or None
        bk_id = form.bk_id.data or None
        expand_type = form.expand_type.data or None

        # 因为end是0时0分,将它续一天┑(￣Д ￣)┍
        if create_at_end:
            create_at_end += timedelta(days=1)

        query = """SELECT dt_id,
                   dt_name,
                   activated_status,
                   auth_status,
                   COUNT(*) OVER () AS total
                FROM dt_inlet_info
                inner join bk_user as bu on bu.bk_id = dt_inlet_info.bk_id
                WHERE (activated_status=%(activated_status)s OR %(activated_status)s IS NULL )
                  AND (auth_status=%(auth_status)s OR %(auth_status)s IS NULL )
                  AND (dt_name ~ E%(dt_name)s OR %(dt_name)s = '')
                   AND (dt_inlet_info.parent_id is null)
                  AND (dt_id::VARCHAR ~ E%(dt_id)s OR %(dt_id)s = '')
                  AND (bu.bk_name ~ E%(bk_name)s or %(bk_name)s = '')
                  AND (bu.bk_id::VARCHAR  ~ E%(bk_id)s or %(bk_id)s = '')
                  {and_sql}
                  AND (dt_inlet_info.create_at BETWEEN %(create_at_start)s::TIMESTAMP AND %(create_at_end)s::TIMESTAMP OR %(create_at_start)s IS NULL OR %(create_at_end)s IS NULL )
                ORDER BY dt_inlet_info.create_at desc
                OFFSET %(offset)s ROWS FETCH NEXT 10 ROWS ONLY"""

        and_sql = " and bu.bk_type = {0} ".format(expand_type)

        if expand_type in (BANK_TYPE.get("main"), BANK_TYPE.get("inter")):
            # 主银行和同业银行
            query = query.format(and_sql=and_sql)
        else:
            query = query.format(and_sql="")

        ret = self.db.selectSQL(query, {
            'activated_status': activated_status,
            'auth_status': auth_status,
            'dt_name': self.db.escape(dt_name),
            'dt_id': self.db.escape(dt_id),
            'bk_name': self.db.escape(bk_name),
            'bk_id': self.db.escape(bk_id),
            'create_at_start': create_at_start,
            'create_at_end': create_at_end,

            'offset': offset}, fetchone=False)  # 每页显示10条数据
        if ret:
            return ret, ret[0][-1]  # 数据,总数
        return ret, 0
