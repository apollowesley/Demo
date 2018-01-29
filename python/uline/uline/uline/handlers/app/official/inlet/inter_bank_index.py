# -*- coding: utf-8 -*-
import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import OfclAdminHandler
from .form import InterBankSearch
from datetime import timedelta
from uline.public.permit import check_permission


class InterBankInletIndexHandler(OfclAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        self.form = InterBankSearch(self)
        # 查询参数不合法
        if not self.form.validate():
            self.redirect('/official/inlet/inter_bank')
            return

        pageindex = int(self.get_argument("p", 1))
        self.data, self.total_number = self.db_execute((pageindex - 1) * 10)

    def get(self):
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('official/inlet/interBank.html', navigate_html=navigate_html, data=self.data, form=self.form,
                    total_num=self.total_number)

    def post(self):
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('official/inlet/interBank.html', navigate_html=navigate_html, data=self.data, form=self.form,
                    total_num=self.total_number)

    def db_execute(self, offset):
        """
        """
        # 返回列表,过滤、分页
        create_at_start = self.form.create_at_start.data or None
        create_at_end = self.form.create_at_end.data or None
        bk_name = self.form.bk_name.data or None
        bk_id = self.form.bk_id.data or None

        # 因为end是0时0分,将它续一天┑(￣Д ￣)┍
        if create_at_end:
            create_at_end += timedelta(days=1)

        query = """SELECT bk_id,
                   bk_name,
                   email,
                   COUNT(*) OVER () AS total
                FROM bk_user
                WHERE (bk_name ~ E%(bk_name)s OR %(bk_name)s = '')
                   AND (bk_type=2)
                  AND (bk_id::VARCHAR ~ E%(bk_id)s OR %(bk_id)s = '')
                  AND (create_at BETWEEN %(create_at_start)s::TIMESTAMP AND %(create_at_end)s::TIMESTAMP OR %(create_at_start)s IS NULL OR %(create_at_end)s IS NULL )
                ORDER BY create_at desc
                OFFSET %(offset)s ROWS FETCH NEXT 10 ROWS ONLY"""

        ret = self.db.selectSQL(query, {
            'bk_name': self.db.escape(bk_name),
            'bk_id': self.db.escape(bk_id),
            'create_at_start': create_at_start,
            'create_at_end': create_at_end,

            'offset': offset}, fetchone=False)  # 每页显示10条数据
        if ret:
            return ret, ret[0][-1]  # 数据,总数
        return ret, 0
