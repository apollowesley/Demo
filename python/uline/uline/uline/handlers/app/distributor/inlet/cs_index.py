# -*- coding: utf-8 -*-
import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import DtAdminHandler
from .form import CSSearch
from datetime import timedelta, date
from uline.settings import QR_SCAN_URL, FEATURE_SWITCH
from uline.public.merchant_util import query_mch_inlet_infos, get_chain_info
from uline.public import auth_util, constants
from uline.public.permit import check_permission


class CSInletIndexHandler(DtAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        self.open_d0 = FEATURE_SWITCH.get('OPEN_D0')
        self.form = CSSearch(self)
        self.form.dt_id = self.current_user
        # 查询参数不合法
        if not self.form.validate() and self.form.activated_status.data is not None:
            self.redirect(self.request.uri)
            return
        pageindex = int(self.get_argument("p", 1))
        self.is_normal = 'mch' in self.request.uri
        self.data, self.total_number = self.db_execute(self.form, (pageindex - 1) * 10)

    def get(self):
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('distributor/inlet/cs.html', navigate_html=navigate_html)

    def post(self):
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('distributor/inlet/cs.html', navigate_html=navigate_html)

    def db_execute(self, form, offset):
        create_at_start = form.create_at_start.data or None
        create_at_end = form.create_at_end.data or None
        activated_status = form.activated_status.data or None
        auth_status = form.auth_status.data or None

        mch_id = form.mch_id.data or None
        short_name = form.short_name.data or None

        cs_id = form.cs_id.data or None
        cs_name = form.cs_name.data or None

        if auth_status == constants.AUTH_STATUS_SUBMIT:
            auth_status = (constants.AUTH_STATUS_SUBMIT, constants.AUTH_STATUS_PREVIEWD, constants.AUTH_STATUS_INLETING,
                           constants.AUTH_STATUS_INTERNET_FAIL)
        elif auth_status == constants.AUTH_STATUS_ACCEPT:
            auth_status = (auth_status, )
        elif auth_status == constants.AUTH_STATUS_DENY:
            auth_status = (constants.AUTH_STATUS_FIRST_DENY, constants.AUTH_STATUS_DENY)

        conditions = {
            'create_at_start': create_at_start,
            'create_at_end': create_at_end,
            'activated_status': activated_status,
            'auth_status': auth_status,
            'mch_id': mch_id,
            'short_name': short_name,
            'offset': offset,
            'is_cs': True,
            'cs_id': cs_id,
            'cs_name': cs_name,
            'dt_id': self.current_user
        }

        ret = query_mch_inlet_infos(self.db, conditions, offset)
        if ret:
            ret_list = list()
            chain_map = {}
            for each_cs_info in ret:
                each_cs_info = list(each_cs_info)
                cs_id = each_cs_info[-2]
                chain_shortname = chain_map.get(cs_id, None)
                if chain_shortname is None:
                    chain_shortname = get_chain_info(self.db, each_cs_info[-2])
                    if not chain_shortname:
                        chain_shortname = ''
                    chain_map[cs_id] = chain_shortname
                each_cs_info.insert(-2, chain_shortname)
                ret_list.append(each_cs_info)
            return ret_list, ret_list[0][-1]  # 数据,总数
            # return ret, ret[0][-1]  # 数据,总数
        return ret, 0

    def generate_unchanged_render_params(self):
        return {
            'data': self.data,
            'form': self.form,
            'total_num': self.total_number,
            'QR_SCAN_URL': QR_SCAN_URL,
            'OPEN_D0': self.open_d0,
            'is_normal': self.is_normal,
            'print_status': auth_util.print_auth_status_simple
        }
        pass
