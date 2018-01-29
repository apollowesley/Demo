#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @author: leiyutian
# @createTime: 2017-06-02, 18:33:10 GMT+0800
# @description: 渠道商管理中连锁商户显示


import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import DtAdminHandler
from .form import ChainSearch
from datetime import timedelta
from uline.settings import QR_SCAN_URL
from uline.settings import FEATURE_SWITCH
from uline.public.distributor_util import query_dt_inlet_info
from uline.public import auth_util, constants
from uline.public.permit import check_permission


class ChainInletIndexHandler(DtAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        self.form = ChainSearch(self)
        # setattr(self.form,'dt_id', self.current_user)
        # 查询参数不合法
        if not self.form.validate():
            self.redirect('/bank/inlet/dt')
            return
        pageindex = int(self.get_argument("p", 1))
        self.data, self.total_number = self.db_execute(self.form, (pageindex - 1) * 10)

    def generate_unchanged_render_params(self):
        return {
            'navigate_html': self.get_navigate_html(self.total_number),
            'data': self.data,
            'form': self.form,
            'total_num': self.total_number,
            'QR_SCAN_URL': QR_SCAN_URL,
            'open_review': FEATURE_SWITCH['REVIEW'],
            'OPEN_D0': True,
            'print_status': auth_util.print_auth_status_simple
        }

    def get(self):
        self.render('distributor/inlet/chain.html')

    def post(self):
        self.render('distributor/inlet/chain.html')

    def db_execute(self, form, offset):
        # 返回列表,过滤、分页
        create_at_start = form.create_at_start.data or None
        create_at_end = form.create_at_end.data or None
        activated_status = form.activated_status.data or None
        dt_name = form.dt_name.data or None
        auth_status = form.auth_status.data or None
        dt_id = form.dt_id.data or None

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
            'dt_name': dt_name,
            'auth_status': auth_status,
            'dt_id': dt_id,
            'offset': offset,
            'is_chain': True,
            'parent_id': self.current_user,
        }

        ret = query_dt_inlet_info(self.db, conditions, offset)

        if ret:
            return ret, ret[0][-1]  # 数据,总数
        return ret, 0

    def auth_userid(self, auth_user):
        selSql = """select bk_id from bk_user where email=%s"""
        db_ret = self.db.selectSQL(selSql, (auth_user,))
        if db_ret:
            return db_ret[0]
