# -*- coding: utf-8 -*-
import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import OfclAdminHandler
from .form import CSSearch
from datetime import timedelta
from uline.settings import QR_SCAN_URL
from uline.settings import FEATURE_SWITCH

from uline.public.merchant_util import query_mch_inlet_infos, get_chain_info
from uline.public import auth_util, constants
from uline.public.constants import BANK_TYPE
from uline.public.permit import check_permission


class CSInletIndexHandler(OfclAdminHandler):
    """连锁门店列表

    Extends:
        OfclAdminHandler
    """

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        self.open_review = FEATURE_SWITCH['REVIEW']
        self.form = CSSearch(self)
        # 查询参数不合法
        if not self.form.validate() and self.form.activated_status.data != None:
            self.redirect('/official/inlet/cs')
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
        self.render('official/inlet/cs.html', navigate_html=navigate_html, data=self.data, form=self.form,
                    total_num=self.total_number, QR_SCAN_URL=QR_SCAN_URL, open_review=open_review)

    def post(self):
        open_review = FEATURE_SWITCH['REVIEW']
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('official/inlet/cs.html', navigate_html=navigate_html, data=self.data, form=self.form,
                    total_num=self.total_number, QR_SCAN_URL=QR_SCAN_URL, open_review=open_review)

    # def db_execute(self, form, offset):
    #
    #     # 返回列表,过滤、分页
    #     create_at_start = form.create_at_start.data or None
    #     create_at_end = form.create_at_end.data or None
    #     activated_status = form.activated_status.data or None
    #     auth_status = form.auth_status.data or None
    #
    #     mch_id = form.mch_id.data or None
    #     short_name = form.short_name.data or None
    #
    #     cs_id = form.cs_id.data or None
    #     cs_name = form.cs_name.data or None
    #
    #     query_auth_status = None
    #     if not self.open_review and auth_status == 3:
    #         query_auth_status = (constants.AUTH_STATUS_DENY, constants.AUTH_STATUS_FIRST_DENY)
    #     elif not self.open_review and auth_status == 1:
    #         query_auth_status = (constants.AUTH_STATUS_SUBMIT, constants.AUTH_STATUS_PREVIEWD)
    #     elif auth_status:
    #         query_auth_status = (auth_status,)
    #
    #     conditions = {
    #         'create_at_start': create_at_start,
    #         'create_at_end': create_at_end,
    #         'activated_status': activated_status,
    #         'auth_status': query_auth_status,
    #         'mch_id': mch_id,
    #         'short_name': short_name,
    #         'offset': offset,
    #         'is_cs': True,
    #         'cs_id': cs_id,
    #         'cs_name': cs_name,
    #     }
    #
    #     # 因为end是0时0分,将它续一天┑(￣Д ￣)┍
    #     if create_at_end:
    #         create_at_end += timedelta(days=1)
    #
    #     ret = query_mch_inlet_infos(self.db, conditions, offset, query_role=2)
    #     if ret:
    #         ret_list = list()
    #         chain_map = {}
    #         for each_cs_info in ret:
    #             each_cs_info = list(each_cs_info)
    #             cs_id = each_cs_info[-2]
    #             chain_shortname = chain_map.get(cs_id, None)
    #             if chain_shortname is None:
    #                 chain_shortname = get_chain_info(self.db, each_cs_info[-2])
    #                 if not chain_shortname:
    #                     chain_shortname = ''
    #                 chain_map[cs_id] = chain_shortname
    #             each_cs_info.insert(-2, chain_shortname)
    #             ret_list.append(each_cs_info)
    #         return ret_list, ret_list[0][-1]  # 数据,总数
    #     return ret, 0

    def db_execute(self, form, offset):
        create_at_start = form.create_at_start.data or None
        create_at_end = form.create_at_end.data or None
        activated_status = form.activated_status.data or None
        auth_status = form.auth_status.data or None

        mch_id = form.mch_id.data or None
        short_name = form.short_name.data or None

        cs_id = form.cs_id.data or None
        cs_name = form.cs_name.data or None

        bk_name = form.bk_name.data or None
        bk_id = form.bk_id.data or None
        expand_type = form.expand_type.data or None

        # 因为end是0时0分,将它续一天┑(￣Д ￣)┍
        if create_at_end:
            create_at_end += timedelta(days=1)

        query = """SELECT mch_inlet_info.mch_id,
                           dt_inlet_info.dt_name,
                           mch_inlet_info.mch_shortname,
                           mch_inlet_info.activated_status,
                           mch_inlet_info.auth_status,
                           bu.bk_type,
                           dt_inlet_info.dt_short_name,
                           mch_inlet_info.cs_id,
                           COUNT(*) OVER () AS total
                        FROM mch_inlet_info
                        inner join bk_user as bu on bu.bk_id = mch_inlet_info.bk_id
                        inner join dt_inlet_info on dt_inlet_info.dt_id = mch_inlet_info.cs_id
                        WHERE (mch_inlet_info.activated_status=%(activated_status)s OR %(activated_status)s IS NULL )
                          AND (mch_inlet_info.auth_status=%(auth_status)s OR %(auth_status)s IS NULL )
                          AND (mch_inlet_info.mch_shortname ~ E%(short_name)s OR %(short_name)s = '')
                          AND (mch_inlet_info.cs_id is not null)
                          AND (mch_inlet_info.mch_id::VARCHAR ~ E%(mch_id)s OR %(mch_id)s = '')
                          AND (bu.bk_name ~ E%(bk_name)s or %(bk_name)s = '')
                          AND (bu.bk_id::VARCHAR  ~ E%(bk_id)s or %(bk_id)s = '')
                          AND (mch_inlet_info.cs_id::VARCHAR  ~ E%(cs_id)s OR %(cs_id)s = '')
                          AND (dt_inlet_info.dt_name ~ E%(cs_name)s or %(cs_name)s = '')
                          {and_sql}
                          AND (mch_inlet_info.create_at BETWEEN %(create_at_start)s::TIMESTAMP AND %(create_at_end)s::TIMESTAMP OR %(create_at_start)s IS NULL OR %(create_at_end)s IS NULL )
                        ORDER BY mch_inlet_info.create_at desc
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
            'short_name': self.db.escape(short_name),
            'auth_status': auth_status,
            'mch_id': self.db.escape(mch_id),
            'bk_name': self.db.escape(bk_name),
            'bk_id': self.db.escape(bk_id),
            'cs_id': self.db.escape(cs_id),
            'cs_name': self.db.escape(cs_name),
            'offset': offset
        }, fetchone=False)  # 每页显示10条数据
        if ret:
            ret_list = []
            risk_sql = """select count(*) from merchant_risk
                                                               where sys_id=%s and sys_type_id=%s and has_risk>0 and status=1"""
            for mch_inlet_info in ret:
                mch_inlet_info = list(mch_inlet_info)
                mch_id = mch_inlet_info[0]
                has_risk = self.db.selectSQL(risk_sql, (mch_id, 'cs'))[0]
                mch_inlet_info.insert(-1, has_risk)

                ret_list.append(tuple(mch_inlet_info))
            return ret_list, ret_list[0][-1]  # 数据,总数
        return ret, 0
