#!/bin/env python
# -*- encoding=utf8 -*-

import tornado.testing
import tornado.web
import tornado.ioloop as ioloop
from tornado.testing import AsyncHTTPTestCase
import unittest
import mock

from tornado.util import ObjectDict, unicode_type, timedelta_to_seconds


class MockQuestHanlder(tornado.web.RequestHandler):

    def __init__(self):
        self.request = tornado.httputil.HTTPServerRequest(uri='', host='uline.com')
        headers = tornado.httputil.HTTPHeaders()
        headers['User-Agent'] = 'mozilla/5.0 (windows nt 6.1; wow64) applewebkit/537.36 (khtml, like gecko) chrome/54.0.2840.99 safari/537.36'
        self.request.headers = headers


    def base_url(self):
        return '127.0.0.1:8893/'


class BaseRequestHandlerTestCase(MockQuestHanlder):

    def __init__(self, cookie_secret='0123456789', key_version=None):
        # don't call super.__init__
        self._cookies = {}
        if key_version is None:
            self.application = ObjectDict(settings=dict(cookie_secret=cookie_secret))
        else:
            self.application = ObjectDict(settings=dict(cookie_secret=cookie_secret,
                                                        key_version=key_version))
        super(BaseRequestHandlerTestCase, self).__init__()
        self.set_request_info()

    def set_request_info(self):
        self.request = tornado.httputil.HTTPServerRequest(uri='', host='uline.com')
        headers = tornado.httputil.HTTPHeaders()
        headers['User-Agent'] = 'mozilla/5.0 (windows nt 6.1; wow64) applewebkit/537.36 (khtml, like gecko) chrome/54.0.2840.99 safari/537.36'
        self.request.headers = headers
        self.set_cookie("auth", "209&20b275822b5bfd1ac8de1693ec60c567")

    def get_cookie(self, name):
        return self._cookies.get(name)

    def set_cookie(self, name, value, expires_days=None):
        self._cookies[name] = value


if __name__ == '__main__':
    unittest.main()
