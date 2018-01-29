#!/usr/bin/env python
# -*- coding: utf-8 -*-

# version: v0.0.1
# author: leiyutian
# contact: leiyutian@ulaiber.com
# filename: mch_wx_config.py
# datetime: 2017/6/19 14:58
# description: 请求微信配置

import datetime

from tornado import gen
from tornado.web import authenticated

from uline.handlers.baseHandlers import OfclAdminHandler
from uline.public import common, wx_config_util
from uline.utils.wxpay.wx_util import get_wx_configs
from .form import GetChainWxConfig
from uline.public.permit import check_permission


class ChainWxConfigHandler(OfclAdminHandler):
    @authenticated
    @check_permission
    def prepare(self):
        form = GetChainWxConfig(self)
        self.form = form
        if not form.validate():
            f_rsp = common.f_rsp(code=406, msg='fail')
            self.finish(f_rsp)
        self.chain_id = form.mch_id.data
        self.need_refresh = int(form.refresh.data) == 2
        self.now_time = datetime.datetime.now()

    @gen.coroutine
    def get(self):
        s_rsp = common.f_rsp(code=200, msg='success')
        wx_sub_mch_id, wx_app_sub_mch_id = self.get_wx_sub_ids()
        with self.db.get_db(use_dict=True) as cursor:
            wx_configs = list()
            if wx_sub_mch_id:
                if self.need_refresh:
                    yield wx_config_util.refresh_wx_config(cursor, self.chain_id, 'chain', wx_sub_mch_id, 2, self.now_time)
                wx_reg_config = wx_config_util.get_wx_configs(cursor, self.chain_id, 'chain', 2)
                wx_configs.append(wx_reg_config)

            if wx_app_sub_mch_id:
                if self.need_refresh:
                    yield wx_config_util.refresh_wx_config(cursor, self.chain_id, 'chain',
                                                           wx_app_sub_mch_id, 6, self.now_time)
                wx_app_config = wx_config_util.get_wx_configs(cursor, self.chain_id, 'chain', 6)
                wx_configs.append(wx_app_config)

            s_rsp['wx_configs'] = wx_configs

        self.write(s_rsp)

    def get_wx_sub_ids(self):
        wx_sub_mch_id = None
        wx_app_sub_mch_id = None
        sql = """select wx_sub_mch_id,wx_app_sub_mch_id
                 from dt_user INNER JOIN dt_inlet_info on dt_inlet_info.dt_id=dt_user.dt_id
                 WHERE dt_user.dt_id=%s and dt_inlet_info.parent_id NOTNULL;"""
        wx_sub_ids = self.db.selectSQL(sql, (self.chain_id, ))
        if wx_sub_ids:
            wx_sub_mch_id, wx_app_sub_mch_id = wx_sub_ids
        return wx_sub_mch_id, wx_app_sub_mch_id
