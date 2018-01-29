# -*- coding:utf-8 -*-
from __future__ import division
import urlparse

from uline.handlers.baseHandlers import BaseHandler
from uline.public.baseDB import DbClient
from uline.public.baseTradeDB import TradeDbClient
from uline.public import log


class ApiHandler(BaseHandler):
    def __init__(self, *args, **kwargs):
        super(ApiHandler, self).__init__(*args, **kwargs)

        """
        获取当前角色名称：
        dt: 渠道商
        mch: 商户
        bk: 银行
        ub: 官方
        inter_bank: 同业银行
        :return:
        """
        self.users = ['dt', 'mch', 'bk', 'ub', 'inter_bk', 'chain']

        # 登录地址
        self.login_urls = {
            'mch': '/merchant/login',
            'dt': '/dist/login',
            'bk': '/bank/login',
            'ub': '/official/login',
            'chain': '/chain/login',
            'inter_bk': '/inter_bank/login'
        }

        self.current_user_name = ''
        for user in self.users:
            if self.session.get(user + '_id'):
                self.current_user_name = user
                break
        if not self.current_user_name:
            # 如果找不到对应的角色类型，获取当前的角色类型
            ref_url = self.request.headers.get('Referer', '')
            log.exception.info(
                'no user name, ref_url:{}, request_uri:{}, session info:{}'.format(ref_url, self.request.uri,
                                                                                   self.session))

    def get_login_url(self):
        login_url = self.login_urls.get(self.current_user_name)
        if not login_url:
            try:
                # header中的Referer是当前页面的来源页面的地址，从这里可以获得访问来源"
                self.back_uri = urlparse.urlparse(self.request.headers.get('Referer', '')).path[1:].split('/')[0]
                login_url = "/{}/login".format(self.back_uri)
            except Exception as e:
                login_url = "http://uline.cc"
        return login_url

    def get_current_user(self):
        return self.session.get(self.current_user_name + '_id')

    def get_current_subuser(self):
        return self.session.get(self.current_user_name + '_sub_id')

    # def get_dt_user_name(self, dt_id):
    # return self.db.selectSQL("select dt_name from dt_user where dt_id=%s",
    # (dt_id,))

    def initialize(self):
        self.db = DbClient()
        self.tdb = TradeDbClient()
        self.rdb = self.application.client
