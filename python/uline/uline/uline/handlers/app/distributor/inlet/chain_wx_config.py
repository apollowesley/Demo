#!/usr/bin/env python
# -*- coding: utf-8 -*-

# version: v0.0.1
# author: leiyutian
# contact: leiyutian@ulaiber.com
# filename: mch_wx_config.py
# datetime: 2017/6/19 14:58
# description: 请求微信配置

import json
import datetime

from tornado import gen
from tornado.web import authenticated

from uline.handlers.baseHandlers import DtAdminHandler
from uline.public import common, wx_config_util
from uline.utils.wxpay.wx_util import get_wx_configs, set_channel_config
from .form import GetChainWxConfig, SetChainWxConfig
from uline.public.permit import check_permission


class ChainWxConfigHandler(DtAdminHandler):
    @authenticated
    @check_permission
    def prepare(self):
        form = GetChainWxConfig(self)
        if self.request.method == 'POST':
            form = SetChainWxConfig(self)
        self.form = form
        self.dt_id = self.current_user
        setattr(form, 'dt_id', self.current_user)
        if not form.validate():
            f_rsp = common.f_rsp(code=406, msg='fail')
            self.finish(f_rsp)
        self.chain_id = form.mch_id.data
        self.now_time = datetime.datetime.now()

    @gen.coroutine
    def get(self):
        self.need_refresh = int(self.form.refresh.data) == 2
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

    @gen.coroutine
    def post(self):
        wx_sub_mch_id, wx_app_sub_mch_id = self.get_wx_sub_ids()
        config_type = self.form.config_type.data
        config_value = self.form.config_value.data
        config_key = self.form.config_key.data
        now_time = datetime.datetime.now()

        s_rsp = common.f_rsp(code=200, msg='设置成功')

        query_wx_sub_id = wx_sub_mch_id
        channel = 2
        if config_type == 6:
            query_wx_sub_id = wx_app_sub_mch_id
            channel = 6
        msg = ''
        if query_wx_sub_id:
            config_values = list()
            if config_key == 'jsapi_path':
                config_value = json.loads(config_value)
                config_values.extend(config_value)
            else:
                config_values.append(config_value)
            with self.db.get_db() as cursor:
                for each_config in config_values:
                    msg = yield set_channel_config(query_wx_sub_id, channel, config_key, each_config)
                    if msg:
                        break
                    config_info = {
                        'role_id': self.chain_id,
                        'role_type': 'chain',
                        'config_name': config_key,
                        'config_value': each_config,
                        'channel': channel,
                        'create_time': now_time,
                        'update_time': now_time
                    }
                    wx_config_util.save_config(cursor, config_info)
        else:
            msg = '该商户没有该费率渠道'
        if msg:
            s_rsp['code'] = 406
            s_rsp['msg'] = msg
        self.write(s_rsp)

    def get_wx_sub_ids(self):
        wx_sub_mch_id = None
        wx_app_sub_mch_id = None
        sql = """select wx_sub_mch_id,wx_app_sub_mch_id
                 from dt_user INNER JOIN dt_inlet_info on dt_inlet_info.dt_id=dt_user.dt_id
                 WHERE dt_user.dt_id=%s and dt_inlet_info.parent_id=%s;"""
        wx_sub_ids = self.db.selectSQL(sql, (self.chain_id, self.dt_id))
        if wx_sub_ids:
            wx_sub_mch_id, wx_app_sub_mch_id = wx_sub_ids
        return wx_sub_mch_id, wx_app_sub_mch_id
