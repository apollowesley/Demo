# -*- coding:utf-8 -*-
import os
import tornado.web
import redis

from raven.contrib.tornado import AsyncSentryClient

from uline.handlers.urls import urls
from uline.settings import (
    redis_db,
    redis_host,
    redis_port,
    server_debug,
    env,
    SENTRY_DSN,
)

from uline.utils import session
from uline.handlers import baseHandlers as base


class Application(tornado.web.Application):

    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        settings = dict(
            debug=server_debug,
            default_handler_class=base.ErrorLinkHandler,
            template_path=os.path.join(self.base_dir, "templates"),
            static_path=os.path.join(self.base_dir, "static"),
            cookie_secret='1ks1tuCW3x0lU14H3m0CV39Q288rVkc9113ieivhYi610E0i4fRhB6u5VhiZRu72',
            session_secret="3cdcb1f00803b6e78ab50b466a40b9977db396840c28307f428b25e2277f1bcc",
            session_timeout=60 * 60,
            # xsrf_cookies=True if env == 'prod' else False,
            # xsrf_cookies=True,
            store_options={
                'redis_host': redis_host,
                'redis_port': redis_port,
                'redis_pass': None
            },
        )
        tornado.web.Application.__init__(self, handlers=urls, **settings)
        self.client = redis.Redis(
            host=redis_host, port=redis_port, db=redis_db)
        self.session_manager = session.SessionManager(
            settings["session_secret"],
            settings["store_options"], settings["session_timeout"])
        self.sentry_client = AsyncSentryClient(dsn=SENTRY_DSN, environment=env)
