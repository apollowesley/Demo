# -*- coding:utf-8 -*-
import os
import tornado.web
import redis
from uline_api.handlers.urls import urls
from uline_api.handlers import baseHandlers as base
from uline_api.util import db
from uline_api.setting import REDIS_DB, REDIS_HOST, REDIS_PORT, env
from uline_api.util import session


class Application(tornado.web.Application):
    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        settings = dict(
            debug=True if env in ['LOCAL', 'INSIDE', 'DEV'] else False,
            autoreload=True if env in ['LOCAL', 'INSIDE', 'DEV'] else False,
            default_handler_class=base.DefaultRESTfulHandler,
            template_path=os.path.join(self.base_dir, "templates"),
            static_path=os.path.join(self.base_dir, "static"),
            cookie_secret='7D7DBF7B94F3248011E4C016CCC666B9935E074C97874C352D00FB84F96BA065',
            session_secret="F6220339F9A9DB76A96620BDAD6A1FD08F79ABAE68AB545AD712FB44FB780CF3",
            session_timeout=60 * 60,
            xsrf_cookies=False,
            store_options={
                'redis_host': REDIS_HOST,
                'redis_port': REDIS_PORT,
                'redis_pass': None
            },
        )
        tornado.web.Application.__init__(self, handlers=urls, **settings)
        self.client = redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        self.session_manager = session.SessionManager(
            settings["session_secret"],
            settings["store_options"],
            settings["session_timeout"]
        )
        db.initdb()
