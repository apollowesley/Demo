#!/usr/bin/env python
# -*- coding: utf-8 -*-

# version: v0.0.1
# author: leiyutian
# contact: leiyutian@ulaiber.com
# filename: wx_pay_config.py
# datetime: 2017/6/28 15:12
# description: 新增微信配置

import datetime

from tornado import gen

from uline_api.handlers.baseHandlers import RESTfulHandler, RESTfulHTTPError
from uline_api.handlers.mch_inlet.modify_form import SetMchWxPayConfigForm, GetMchWxPayConfigForm, \
    UpdateMchWxPayConfigForm
from uline_api.model.uline.info import MchInletInfo, PayConfigInfo, DtInletInfo, MchPayment
from uline_api.model.uline.user import MchUser, DtUser
from uline_api.util.db import uline_session_scope
from uline_api.util.wxpay.wx_util import set_channel_config, get_wx_configs

CHANNEL_MAP = {
    'reg_online': 6,
    'reg_offline': 2,
    'dine': 10,
}


class SetMchWxPayConfigHandler(RESTfulHandler, SetMchWxPayConfigForm):
    def prepare(self):
        self.update_at = datetime.datetime.now()
        super(SetMchWxPayConfigHandler, self).prepare()
        self.form = SetMchWxPayConfigForm(self)
        setattr(self.form, 'dt_id', self.dt_id)
        self.create_at = datetime.datetime.now()

    @gen.coroutine
    def post(self):
        if not self.form.validate():
            raise RESTfulHTTPError(400, content=self.form.errors)

        mch_id = self.get_argument('mch_id', None)
        if not mch_id:
            raise RESTfulHTTPError(400, content={'mch_id': [u'指定商户未找到']})
        self.mch_id = mch_id
        with uline_session_scope() as session:
            error_msg, wx_sub_mch_id, wx_app_sub_mch_id = get_role_user(session, self.mch_type, self.mch_id, self.dt_id)

        self.config_channel = CHANNEL_MAP.get(self.config_channel, '')
        if not self.config_channel:
            error_msg = {'config_channel': [u'配置所选通道错误']}

        if error_msg:
            raise RESTfulHTTPError(400, content=error_msg)

        query_wx_sub_id = wx_sub_mch_id
        if self.config_channel == 6:
            query_wx_sub_id = wx_app_sub_mch_id
        if not query_wx_sub_id:
            raise RESTfulHTTPError(400, content={'config_channel': ['商户没有对应通道的微信商户号']})
        result_code, msg = yield set_channel_config(query_wx_sub_id, self.config_channel, self.config_key,
                                                    self.config_value)
        if not result_code:
            raise RESTfulHTTPError(400, content={'config': [msg]})
        with uline_session_scope() as session:
            pay_configs = session.query(PayConfigInfo).filter(PayConfigInfo.role_id == self.mch_id,
                                                              PayConfigInfo.role_type == 'mch',
                                                              PayConfigInfo.channel == self.config_channel,
                                                              PayConfigInfo.config_name == self.config_key).all()
            config_values = set([each_config.config_value for each_config in pay_configs])
            if self.config_value not in config_values:
                pay_config = PayConfigInfo()
                pay_config.role_id = self.mch_id
                pay_config.role_type = self.mch_type
                pay_config.config_name = self.config_key
                pay_config.config_value = self.config_value
                pay_config.channel = self.config_channel
                pay_config.create_time = self.create_at
                pay_config.update_time = self.create_at
                session.add(pay_config)
        self.finish({'result': 'SUCCESS'})


class GetMchWxPayConfigHandler(RESTfulHandler, GetMchWxPayConfigForm):
    def prepare(self):
        self.update_at = datetime.datetime.now()
        super(GetMchWxPayConfigHandler, self).prepare()
        self.form = GetMchWxPayConfigForm(self)
        self.create_at = datetime.datetime.now()

    @gen.coroutine
    def get(self):
        if not self.form.validate():
            raise RESTfulHTTPError(400, content=self.form.errors)
        mch_id = self.get_argument('mch_id', None)
        if not mch_id:
            raise RESTfulHTTPError(400, content={'mch_id': [u'指定商户未找到']})
        self.mch_id = mch_id
        with uline_session_scope() as session:
            error_msg, wx_sub_mch_id, wx_app_sub_mch_id = get_role_user(session, self.mch_type, self.mch_id, self.dt_id)

        self.channel = CHANNEL_MAP.get(self.config_channel, '')
        if not self.channel:
            error_msg = {'config_channel': [u'查询所选通道错误']}

        if error_msg:
            raise RESTfulHTTPError(400, content=error_msg)

        wx_configs = {
            'config_channel': self.config_channel,
            'jsapi_path_list': [],
            'appid_config_list': [],
            'default_subscribe': '',
            'err_msg': '',
        }

        key_map = {
            'subscribe_appid': 'default_subscribe',
            'sub_appid': 'appid_config_list',
            'jsapi_path': 'jsapi_path_list'
        }
        with uline_session_scope() as session:
            db_configs = session.query(PayConfigInfo).filter(PayConfigInfo.role_id == self.mch_id,
                                                             PayConfigInfo.role_type == self.mch_type,
                                                             PayConfigInfo.channel == self.channel).all()
            for each_config in db_configs:
                config_name = each_config.config_name
                config_value = each_config.config_value
                if config_name in ('sub_appid', 'jsapi_path'):
                    wx_configs[key_map[config_name]].append(config_value)
                elif config_name == 'subscribe_appid':
                    wx_configs['default_subscribe'] = config_name
        self.finish(wx_configs)


class UpdateMchWxPayConfigHandler(RESTfulHandler, UpdateMchWxPayConfigForm):
    def prepare(self):
        self.update_at = datetime.datetime.now()
        super(UpdateMchWxPayConfigHandler, self).prepare()
        self.form = UpdateMchWxPayConfigForm(self)
        self.create_at = datetime.datetime.now()

    @gen.coroutine
    def post(self):
        if not self.form.validate():
            raise RESTfulHTTPError(400, content=self.form.errors)
        mch_id = self.get_argument('mch_id', None)
        if not mch_id:
            raise RESTfulHTTPError(400, content={'mch_id': [u'指定商户未找到']})
        self.mch_id = mch_id
        with uline_session_scope() as session:
            error_msg, wx_sub_mch_id, wx_app_sub_mch_id = get_role_user(session, self.mch_type, self.mch_id, self.dt_id)

        if error_msg:
            raise RESTfulHTTPError(400, content=error_msg)

        config_list = []

        with uline_session_scope() as session:
            session.query(PayConfigInfo).filter(PayConfigInfo.role_id == self.mch_id,
                                                PayConfigInfo.role_type == self.mch_type).delete()

            if wx_sub_mch_id:
                channel = 2
                dine_payments = session.query(MchPayment).filter(MchPayment.payment_type.in_([11, 12, 13]),
                                                                 MchPayment.mch_id == self.mch_id).all()
                if dine_payments:
                    channel = 10
                wx_configs = yield self.update_channel_pay_config(session, channel, wx_sub_mch_id)
                config_list.append(wx_configs)

            if wx_app_sub_mch_id:
                wx_configs = yield self.update_channel_pay_config(session, 6, wx_app_sub_mch_id)
                config_list.append(wx_configs)

        self.finish({'config_list': config_list})

    @gen.coroutine
    def update_channel_pay_config(self, session, channel, query_sub_mch_id):
        wx_configs = yield get_wx_configs(query_sub_mch_id, channel)
        if wx_configs['err_msg']:
            raise RESTfulHTTPError(400, content={'configs': wx_configs['err_msg']})
        appids = wx_configs['appid_config_list']
        self.save_config_list(session, channel, 'sub_appid', appids)

        jsapi_list = wx_configs['jsapi_path_list']
        self.save_config_list(session, channel, 'jsapi_path', jsapi_list)

        default_sub = [wx_configs['default_subscribe']]
        self.save_config_list(session, channel, 'subscribe_appid', default_sub)
        raise gen.Return(wx_configs)

    def save_config_list(self, session, channel, config_name, default_sub):
        for each_config in default_sub:
            if each_config:
                self.save_config(session, channel, config_name, each_config)

    def save_config(self, session, channel, config_name, each_config):
        pay_info = {
            'role_id': self.mch_id,
            'role_type': self.mch_type,
            'config_name': config_name,
            'config_value': each_config,
            'channel': channel,
            'create_time': self.create_at,
            'update_time': self.create_at,
        }
        config_info = PayConfigInfo(**pay_info)
        session.add(config_info)


def get_role_user(session, mch_type, mch_id, dt_id):
    error_msg = ''
    inlet_info = None
    wx_sub_mch_id = None
    wx_app_sub_mch_id = None
    role_user = None
    if mch_type == 'mch':
        inlet_info = session.query(MchInletInfo).filter(MchInletInfo.mch_id == mch_id,
                                                        MchInletInfo.dt_id == dt_id,
                                                        MchInletInfo.cs_id.is_(None)).first()
        role_user = session.query(MchUser).filter(MchUser.mch_id == mch_id).first()
    elif mch_type == 'chain':
        inlet_info = session.query(DtInletInfo).filter(DtInletInfo.dt_id == mch_id,
                                                       DtInletInfo.parent_id == dt_id,
                                                       DtInletInfo.parent_id.isnot(None)).first()
        role_user = session.query(DtUser).filter(DtUser.dt_id == mch_id).first()
    if role_user:
        wx_sub_mch_id = role_user.wx_sub_mch_id
        wx_app_sub_mch_id = role_user.wx_app_sub_mch_id
    if not (inlet_info and role_user):
        error_msg = {'mch_id': [u'指定商户未找到']}
    return error_msg, wx_sub_mch_id, wx_app_sub_mch_id
