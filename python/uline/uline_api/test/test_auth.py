#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '11/30/16'
import pytest
import tornado
from base64 import b64encode
from datetime import datetime
from hashlib import md5
from . import conf


class TestBasicAuth():

    @tornado.gen.coroutine
    def basic_auth(self, http_client, sign, code, auth_message=None):
        response = yield http_client.fetch(
            conf.base_url + '/v1/mchinlet/authtest', headers={'Authorization': sign})

        # 所有basic auth 的请求返回值都应该是200
        assert response.code == 200

        # 判断body 里面的code是否正确
        assert tornado.escape.json_decode(response.body).get('code') == code

        # 检查错误提示是否符合预期
        if auth_message:
            assert tornado.escape.json_decode(response.body).get("content").get("Authorization")[0] == auth_message

    @pytest.mark.gen_test
    def test_basic_auth_success(self, http_client):
        """检查basic auth 成功授权"""
        sign = 'Basic ' + b64encode(conf.dt_id + ':' + conf.api_key)
        code = 200
        yield self.basic_auth(http_client, sign, code)

    @pytest.mark.gen_test
    def test_invalid_base_64(self, http_client):
        """检查认证字符串是非法base64字符串的时候, 返回值是否符合预期"""
        sign = 'Basic ' + conf.dt_id + ':' + conf.api_key
        code = 401
        yield self.basic_auth(http_client, sign, code, auth_message=u"Authorization认证失败，非有效的base64字符串")

    @pytest.mark.gen_test
    def test_must_include_colon(self, http_client):
        """检查认证字符串格式是否正确， 必须保护冒号, 返回值是否符合预期"""
        sign = 'Basic ' + b64encode(conf.dt_id + " "+ conf.api_key)
        code = 401
        yield self.basic_auth(http_client, sign, code, auth_message=u'Header中Authorization字段格式错误，必须为"渠道商号:渠道商密钥"格式')

    @pytest.mark.gen_test
    def test_dt_id_is_empty(self, http_client):
        """检查basic auth 渠道号为空, 返回值是否符合预期"""
        sign = 'Basic ' + b64encode(':' + conf.api_key)
        code = 401
        yield self.basic_auth(http_client, sign, code, auth_message=u"Authorization认证失败，渠道商号不能为空")

    @pytest.mark.gen_test
    def test_dt_api_key_is_empty(self, http_client):
        """检查basic auth 渠道上密钥为空, 返回值是否符合预期"""
        sign = 'Basic ' + b64encode(conf.dt_id + ':')
        code = 401
        yield self.basic_auth(http_client, sign, code, auth_message=u"Authorization认证失败，渠道商密钥不能为空")

    @pytest.mark.gen_test
    def test_dt_id_invalid(self, http_client):
        """检查basic auth 渠道商号非法, 返回值是否符合预期"""
        sign = 'Basic ' + b64encode('invalid' + ':' + conf.api_key)
        code = 401
        yield self.basic_auth(http_client, sign, code, auth_message=u"Authorization认证失败，渠道号非法，必须只包含数字")

    @pytest.mark.gen_test
    def test_dt_id_is_not_exist(self, http_client):
        """检查basic auth 渠道商号不存在, 返回值是否符合预期"""
        sign = 'Basic ' + b64encode(conf.dt_id_not_exit + ':' + conf.api_key)
        code = 401
        yield self.basic_auth(http_client, sign, code, auth_message=u"Authorization认证失败，渠道商不存在")

    @pytest.mark.gen_test
    def test_wrong_dt_api_key(self, http_client):
        """检查basic auth 渠道商密钥错误, 返回值是否符合预期"""
        sign = 'Basic ' + b64encode(conf.dt_id + ':' + conf.api_key + 'wrong')
        code = 401
        yield self.basic_auth(http_client, sign, code, auth_message=u"Authorization认证失败，渠道商密钥错误")


class TestHMACAuth(object):
    @staticmethod
    def get_auth_args():
        date = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        method = 'POST'
        path = '/v1/mchinlet/authtest'
        length = '1'
        return date, method, path, length

    @tornado.gen.coroutine
    def hmac_auth(self, http_client, dt_id, sign, date, code, body='_', auth_message=None):
        """进行hmac验证"""
        response = yield self.hmac_auth_request(http_client, dt_id, sign, date, body)
        assert tornado.escape.json_decode(response.body).get('code') == code

        # 检查错误提示是否符合预期
        if auth_message:
            assert tornado.escape.json_decode(response.body).get("content").get("Authorization")[0] == auth_message

    @tornado.gen.coroutine
    def hmac_auth_request(self, http_client, dt_id, sign, date, body='-'):
        """发送hmac验证请求"""
        headers={
            'Authorization': 'Uline ' + dt_id + ':' + sign,
        }
        if date:
            headers['Date'] = date
        response = yield http_client.fetch(
            conf.base_url + '/v1/mchinlet/authtest',
            headers=headers,
            method="POST", body=body
        )
        raise tornado.gen.Return(response)

    @pytest.mark.gen_test
    def test_auth_success(self, http_client):
        """认证成功"""
        date, method, path, length = self.get_auth_args()
        sign_body = '&'.join([method, path, date, length, conf.api_key])
        sign = md5(sign_body).hexdigest()
        yield self.hmac_auth(http_client, conf.dt_id, sign, date, code=200)

    @pytest.mark.gen_test
    def test_auth_format_invalid(self, http_client):
        """检查认证字符串格式不合法， 不包含冒号, 错误提示符合预期"""
        date, method, path, length = self.get_auth_args()
        sign_body = '&'.join([method, path, date, length, conf.api_key])
        sign = md5(sign_body).hexdigest()
        headers={
            'Authorization': 'Uline ' + conf.dt_id + ' ' + sign,
        }
        if date:
            headers['Date'] = date

        response = yield http_client.fetch(
            conf.base_url + '/v1/mchinlet/authtest',
            headers=headers,
            method="POST", body='-'
        )
        assert tornado.escape.json_decode(response.body).get('code') == 401

        auth_message = u'Header中Authorization字段格式错误，必须为："Authorization: Uline <id>:<signature>"'
        assert tornado.escape.json_decode(response.body).get("content").get("Authorization")[0] == auth_message

    @pytest.mark.gen_test
    def test_http_header_date_no_valid(self, http_client):
        """检查http请求头DATE字段格式不对, 错误提示符合预期"""
        date, method, path, length = self.get_auth_args()
        date = 'Wed, 05 Jul 2017 10:27-19 GMT'
        sign_body = '&'.join([method, path, date, length, conf.api_key])
        sign = md5(sign_body).hexdigest()
        auth_message = u'HTTP请求头中Date字段不合法, 必须为类似这样的格式:"Wed, 05 Jul 2017 10:27:19 GMT"'
        yield self.hmac_auth(http_client, conf.dt_id, sign, date, code=401, auth_message=auth_message)

    @pytest.mark.gen_test
    def test_http_header_date_not_exist(self, http_client):
        """检查http请求头DATE字段不存在, 错误提示符合预期"""
        date, method, path, length = self.get_auth_args()
        date = ''
        sign_body = '&'.join([method, path, date, length, conf.api_key])
        sign = md5(sign_body).hexdigest()
        auth_message = u'HTTP请求头中没有Date字段'
        yield self.hmac_auth(http_client, conf.dt_id, sign, date, code=401, auth_message=auth_message)

    @pytest.mark.gen_test
    def test_http_header_date_too_early(self, http_client):
        """检查http请求头DATE字段过期, 错误提示符合预期"""
        date, method, path, length = self.get_auth_args()
        sign_body = '&'.join([method, path, date, length, conf.api_key])
        date = 'Wed, 05 Jul 2017 10:27:19 GMT'
        sign = md5(sign_body).hexdigest()
        auth_message = u'HTTP请求头中Date距离现在已经超过一分钟'
        yield self.hmac_auth(http_client, conf.dt_id, sign, date, code=401, auth_message=auth_message)

    @pytest.mark.gen_test
    def test_dt_id_is_not_exist(self, http_client):
        """检查渠道号不存在，错误提示符合预期"""
        date, method, path, length = self.get_auth_args()
        sign_body = '&'.join([method, path, date, length, conf.api_key])
        sign = md5(sign_body).hexdigest()
        auth_message = u'Authorization认证失败,提供的渠道号不存在'
        yield self.hmac_auth(http_client, conf.dt_id_not_exit, sign, date, code=401, auth_message=auth_message)

    @pytest.mark.gen_test
    def test_dt_id_has_no_api_key(self, http_client):
        """检查该渠道商没有配置api_key，错误提示符合预期"""
        date, method, path, length = self.get_auth_args()
        sign_body = '&'.join([method, path, date, length, conf.api_key])
        sign = md5(sign_body).hexdigest()
        auth_message = u'Authorization认证失败,提供的渠道号没有开通api权限，请联系客服处理'
        yield self.hmac_auth(http_client, conf.dt_id_has_no_api_key, sign, date, code=401, auth_message=auth_message)

    @pytest.mark.gen_test
    def test_dt_id_auth_error(self, http_client):
        """检查该渠道商签名校验错误"""
        date, method, path, length = self.get_auth_args()
        path = 'error_path'
        sign_body = '&'.join([method, path, date, length, conf.api_key])
        sign = md5(sign_body).hexdigest()
        response = yield self.hmac_auth_request(http_client, conf.dt_id, sign, date)

        assert tornado.escape.json_decode(response.body).get('code') == 401
        # 检查错误提示是否符合预期
        auth_message = tornado.escape.json_decode(response.body).get("content").get("Authorization")[0]
        assert auth_message.startswith(u'Authorization认证失败, 签名不匹配， 服务器端进行签名的字符串为')
