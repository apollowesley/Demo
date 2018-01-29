# -*- coding: utf-8 -*-
import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import ChainAdminHandler
from .form import MerchantSearch
from datetime import timedelta, date
from uline.public.common import get_week_range
from uline.settings import QR_SCAN_URL, FEATURE_SWITCH
from uline.public.merchant_util import get_chain_info
from uline.utils.chain import chain_utils
from uline.public import auth_util, constants
from uline.public.permit import check_permission


class CsInletIndexHandler(ChainAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        self.open_review = FEATURE_SWITCH['REVIEW']
        self.open_d0 = FEATURE_SWITCH.get('OPEN_D0')
        self.form = MerchantSearch(self)
        self.form.dt_id = chain_utils.get_dt_id_for_chain_id(self.current_user)
        # 查询参数不合法
        if not self.form.validate() and self.form.activated_status.data is not None:
            self.redirect(self.request.uri)
            return
        self.pageindex = int(self.get_argument("p", 1))

    def get(self):
        # get 请求时如果没有create_at_start和create_at_end，则默认查询最近7天
        if not self.form.create_at_start.data and not self.form.create_at_end.data and self.pageindex == 1:
            create_at_start, create_at_end = get_week_range()
            self.form.create_at_start.data = create_at_start
            self.form.create_at_end.data = create_at_end
        self.data, self.total_number = self.db_execute(
            self.form, (self.pageindex - 1) * 10)
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('chain/inlet/cs.html', navigate_html=navigate_html)

    def post(self):
        self.data, self.total_number = self.db_execute(
            self.form, (self.pageindex - 1) * 10)
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('chain/inlet/cs.html', navigate_html=navigate_html)

    def db_execute(self, form, offset):
        # 返回列表,过滤、分页
        create_at_start = form.create_at_start.data or None
        create_at_end = form.create_at_end.data or None
        activated_status = form.activated_status.data or None
        mch_name = form.mch_name.data or None
        auth_status = form.auth_status.data or None
        mch_id = form.mch_id.data or None
        dt_sub_id = form.dt_sub_id.data or None

        query_auth_status = None
        if not self.open_review and auth_status == 3:
            query_auth_status = [constants.AUTH_STATUS_DENY, constants.AUTH_STATUS_FIRST_DENY]
        elif not self.open_review and auth_status == 1:
            query_auth_status = [constants.AUTH_STATUS_SUBMIT, constants.AUTH_STATUS_PREVIEWD]
        elif auth_status:
            query_auth_status = [auth_status, ]

            # 因为end是0时0分,将它续一天┑(￣Д ￣)┍
        if create_at_end:
            create_at_end += timedelta(days=1)

        query = """SELECT mch_id,
                   mch_name,
                   mch_shortname,
                   activated_status,
                   auth_status,
                   COUNT(*) OVER () AS total
                FROM mch_inlet_info
                WHERE cs_id=%(cs_id)s
                  AND (activated_status=%(activated_status)s OR %(activated_status)s IS NULL )
                  AND (auth_status=ANY(%(auth_status)s) OR %(auth_status)s IS NULL )
                  AND (mch_name ~ E%(mch_name)s OR %(mch_name)s = '')
                  AND (mch_id::VARCHAR ~ E%(mch_id)s OR %(mch_id)s = '')
                  and (mch_inlet_info.cs_id is not null)
                  AND (create_at BETWEEN %(create_at_start)s::TIMESTAMP
                  AND %(create_at_end)s::TIMESTAMP OR %(create_at_start)s IS NULL OR %(create_at_end)s IS NULL )
                  AND (dt_sub_id=%(dt_sub_id)s OR %(dt_sub_id)s IS NULL )
                ORDER BY create_at desc
                OFFSET %(offset)s ROWS FETCH NEXT 10 ROWS ONLY;"""

        ret = self.db.selectSQL(query, {
            'cs_id': self.current_user,
            'activated_status': activated_status,
            'auth_status': query_auth_status,
            'mch_name': self.db.escape(mch_name),
            'mch_id': self.db.escape(mch_id),
            'create_at_start': create_at_start,
            'create_at_end': create_at_end,
            'dt_sub_id': dt_sub_id,

            'offset': offset}, fetchone=False)  # 每页显示10条数据

        if ret:
            return ret, ret[0][-1]  # 数据,总数
        return ret, 0

    def generate_unchanged_render_params(self):
        return {
            'data': self.data,
            'form': self.form,
            'total_num': self.total_number,
            'QR_SCAN_URL': QR_SCAN_URL,
            'OPEN_D0': self.open_d0,
            'print_status': auth_util.print_auth_status_simple
        }
