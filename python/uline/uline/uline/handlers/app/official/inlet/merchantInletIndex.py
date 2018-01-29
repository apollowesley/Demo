# -*- coding: utf-8 -*-
import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import OfclAdminHandler
from .form import MerchantSearch
from datetime import timedelta
from uline.public.common import get_week_range
from uline.settings import QR_SCAN_URL
from uline.settings import FEATURE_SWITCH
from uline.public import constants, auth_util
from uline.public.constants import BANK_TYPE
from uline.public.permit import check_permission


class MerchantInletIndexHandler(OfclAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        self.form = MerchantSearch(self)
        # 查询参数不合法
        if not self.form.validate() and self.form.activated_status.data != None:
            self.redirect('/official/inlet/mch')
            return
        self.pageindex = int(self.get_argument("p", 1))
        self.open_review = FEATURE_SWITCH['REVIEW']

    def get(self):
        # get 请求时如果没有create_at_start和create_at_end，则默认查询最近7天
        if not self.form.create_at_start.data and not self.form.create_at_end.data and self.pageindex == 1:
            create_at_start, create_at_end = get_week_range()
            self.form.create_at_start.data = create_at_start
            self.form.create_at_end.data = create_at_end
        self.data, self.total_number = self.db_execute(
            self.form, (self.pageindex - 1) * 10)
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('official/inlet/merchant.html', navigate_html=navigate_html, data=self.data, form=self.form,
                    total_num=self.total_number, QR_SCAN_URL=QR_SCAN_URL, open_review=self.open_review)

    def print_status(self, status):
        status_str = constants.AUTH_STATUS.get(str(status), '')
        if not self.open_review:
            if status == 4:
                status_str = u'审核中'
            elif status in [constants.AUTH_STATUS_DENY, constants.AUTH_STATUS_FIRST_DENY]:
                status_str = u'审核驳回'
        return status_str

    def generate_unchanged_render_params(self):
        return {
            'print_status': auth_util.print_auth_status
        }

    def post(self):
        self.data, self.total_number = self.db_execute(
            self.form, (self.pageindex - 1) * 10)
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('official/inlet/merchant.html', navigate_html=navigate_html, data=self.data, form=self.form,
                    total_num=self.total_number, QR_SCAN_URL=QR_SCAN_URL, open_review=self.open_review)

    def db_execute(self, form, offset):
        # 返回列表,过滤、分页
        create_at_start = form.create_at_start.data or None
        create_at_end = form.create_at_end.data or None
        activated_status = form.activated_status.data or None
        mch_name = form.mch_name.data or None
        auth_status = form.auth_status.data or None
        dt_name = form.dt_name.data or None
        dt_id = form.dt_id.data or None
        mch_id = form.mch_id.data or None
        bk_name = form.bk_name.data or None
        bk_id = form.bk_id.data or None
        expand_type = form.expand_type.data or None

        if not self.open_review and auth_status == 3:
            auth_status = (constants.AUTH_STATUS_DENY, constants.AUTH_STATUS_FIRST_DENY)

        elif not self.open_review and auth_status == 1:
            auth_status = (constants.AUTH_STATUS_SUBMIT, constants.AUTH_STATUS_PREVIEWD)
        else:
            auth_status = (auth_status,)
        # 因为end是0时0分,将它续一天┑(￣Д ￣)┍
        if create_at_end:
            create_at_end += timedelta(days=1)

        query = """select mch.mch_id,mch.mch_name,mch.mch_shortname,mch.activated_status,mch.auth_status,dt.dt_name, COUNT(*) OVER () AS total
        from mch_inlet_info as mch
          inner join dt_user as dt on mch.dt_id=dt.dt_id
          inner join bk_user as bu on bu.bk_id = mch.bk_id
        where (mch.activated_status=%(activated_status)s or %(activated_status)s is null)
        and (mch.auth_status in %(auth_status)s or %(auth_status)s is null)
        and (mch.mch_name ~ E%(mch_name)s or %(mch_name)s = '')
        and (dt.dt_name ~ E%(dt_name)s or %(dt_name)s = '')
        and (dt.dt_id::VARCHAR ~ E%(dt_id)s or %(dt_id)s = '')
        and (bu.bk_name ~ E%(bk_name)s or %(bk_name)s = '')
        and (bu.bk_id::VARCHAR  ~ E%(bk_id)s or %(bk_id)s = '')
        and (mch.cs_id is null)
        and (mch.mch_id::VARCHAR ~ E%(mch_id)s or %(mch_id)s = '')
        and (mch.create_at between %(create_at_start)s::timestamp
          and %(create_at_end)s::timestamp or %(create_at_start)s is null or %(create_at_end)s is null)
        and (mch.cs_id ISNULL)
        {and_sql}
        order by mch.create_at desc
        offset %(offset)s rows fetch next 10 rows only;
        """

        and_sql = " and bu.bk_type = {0} ".format(expand_type)

        if expand_type in (BANK_TYPE.get("main"), BANK_TYPE.get("inter")):
            # 主银行和同业银行
            query = query.format(and_sql=and_sql)
        else:
            query = query.format(and_sql="")

        ret = self.db.selectSQL(query, {
            'activated_status': activated_status,
            'auth_status': auth_status,
            'mch_name': self.db.escape(mch_name),
            'mch_id': self.db.escape(mch_id),
            'dt_name': self.db.escape(dt_name),
            'dt_id': self.db.escape(dt_id),
            'bk_name': self.db.escape(bk_name),
            'bk_id': self.db.escape(bk_id),
            'create_at_start': create_at_start,
            'create_at_end': create_at_end,
            'offset': offset}, fetchone=False)  # 每页显示10条数据
        if ret:
            ret_list = []
            sql = """select comment from auth_mch_info where mch_id=%s ORDER BY id desc LIMIT 1"""
            risk_sql = """select count(*) from merchant_risk
                                       where sys_id=%s and sys_type_id=%s and has_risk>0 and status=1"""
            for i in ret:
                i = list(i)
                comment = self.db.selectSQL(sql, (i[0],))[0]
                i.insert(-1, comment)

                mch_id = i[0]
                has_risk = self.db.selectSQL(risk_sql, (mch_id, 'mch'))[0]
                i.insert(-1, has_risk)

                ret_list.append(tuple(i))
            return ret_list, ret_list[0][-1]  # 数据,总数
        return ret, 0
