# -*- coding:utf-8 -*-
import tornado.web

from raven.contrib.tornado import AsyncSentryClient

from uline_risk.settings import (
    SENTRY_DSN,
    ENV,
    DEBUG,
)

from uline_risk.handlers.urls import urls
from uline_risk.utils import db


class Risk404Handler(tornado.web.RequestHandler):
    # Override prepare() instead of get() to cover all possible HTTP methods.
    def prepare(self):
        self.set_status(404)
        msg = "url is not valid:{}".format(self.request.uri)
        self.write({"code": 404, "error_msg": msg})
        self.finish()


class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            xsrf_cookies=False,
            debug=DEBUG,
        )
        tornado.web.Application.__init__(self, handlers=urls, default_handler_class=Risk404Handler, **settings)
        db.initdb()
        self.sentry_client = AsyncSentryClient(SENTRY_DSN, environment=ENV)
