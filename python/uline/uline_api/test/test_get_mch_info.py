#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urlparse import urlparse, urljoin
from urllib import urlencode
from hashlib import md5
from datetime import datetime

import pytest
import tornado
from tornado.httputil import  url_concat

from . import conf

class TestGetMchInfo(object):

    @tornado.gen.coroutine
    def hmac_auth_request(self, http_client, method, url, body=None):
        """发送获取mch信息请求"""
        date = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        path = urlparse(url).path
        if body:
            length = str(len(body))
        else:
            length = '0'
        sign_body = '&'.join([method, path, date, length, conf.api_key])
        sign = md5(sign_body).hexdigest()
        headers={
            'Authorization': 'Uline ' + conf.dt_id + ':' + sign,
        }
        if date:
            headers['Date'] = date
        response = yield http_client.fetch(
            url,
            headers=headers,
            method=method, body=body
        )
        raise tornado.gen.Return(response)

    @tornado.gen.coroutine
    def get_mch_info(self, http_client, method, params={}):
        """发送获取mch信息请求"""
        url= urljoin(conf.base_url, "/v1/mch")
        body = None
        if method == 'GET':
            url = url_concat(url, params)
        else:
            body = urlencode(params)
        response = yield self.hmac_auth_request(http_client, method, url, body)
        raise tornado.gen.Return(response)

    @pytest.mark.gen_test
    def test_get_mch_info_success(self, http_client):
        params = {'mch_id': conf.mch_id}
        response = yield self.get_mch_info(http_client, 'GET', params)

        # 检查http code
        assert response.code == 200
        # 检查body里面的code是否为200
        assert tornado.escape.json_decode(response.body).get('code') == 200

    @pytest.mark.gen_test
    def test_post_mch_info_not_allowed(self, http_client):
        """检查POST方法获取商户信息不支持"""
        params = {'mch_id': conf.mch_id}
        response = yield self.get_mch_info(http_client, 'POST', params)

        # 检查http code
        assert response.code == 200
        assert tornado.escape.json_decode(response.body).get('code') == 405
        assert tornado.escape.json_decode(response.body).get('error').get('type') == u'未许可的方法'

    @pytest.mark.gen_test
    def test_get_mch_info_empty_mch_id(self, http_client):
        params = {}
        response = yield self.get_mch_info(http_client, 'GET', params)

        assert response.code == 200
        assert tornado.escape.json_decode(response.body).get('code') == 400
        assert tornado.escape.json_decode(response.body).get('error').get('type') == u'参数错误'
        assert tornado.escape.json_decode(response.body).get('content').get('mch_id')[0] == u'必须传入商户号mch_id'

    @pytest.mark.gen_test
    def test_get_mch_info_mch_id_invalid_format(self, http_client):
        params = {'mch_id': 'xxxxx'}
        response = yield self.get_mch_info(http_client, 'GET', params)

        assert response.code == 200
        assert tornado.escape.json_decode(response.body).get('code') == 400
        assert tornado.escape.json_decode(response.body).get('error').get('type') == u'参数错误'
        assert tornado.escape.json_decode(response.body).get('content').get('mch_id')[0] == u'mch_id必须是数字'

    @pytest.mark.gen_test
    def test_get_mch_info_mch_id_not_exist(self, http_client):
        params = {'mch_id': '123413241'}
        response = yield self.get_mch_info(http_client, 'GET', params)

        assert response.code == 200
        assert tornado.escape.json_decode(response.body).get('code') == 400
        assert tornado.escape.json_decode(response.body).get('error').get('type') == u'参数错误'
        assert tornado.escape.json_decode(response.body).get('content').get('mch_id')[0] == u'mch_id不存在'
