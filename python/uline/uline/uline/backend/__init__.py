# -*- coding: utf-8 -*-
from __future__ import absolute_import
from uline.backend.celery import app

from celery import platforms
from uline.backend.baseDB import DbClient
platforms.C_FORCE_ROOT = True

pg_user = app.conf.CELERY_RESULT_USER
pg_passwd = app.conf.CELERY_RESULT_PASSWD
pg_host = app.conf.CELERY_RESULT_HOST
pg_db = app.conf.CELERY_RESULT_DB
pg_port = app.conf.CELERY_RESULT_PORT

pg_trade_user = app.conf.CELERY_RESULT_TUSER
pg_trade_passwd = app.conf.CELERY_RESULT_TPASSWD
pg_trade_host = app.conf.CELERY_RESULT_THOST
pg_trade_db = app.conf.CELERY_RESULT_TDB
pg_trade_port = app.conf.CELERY_RESULT_TPORT

db = DbClient(pg_host, pg_user, pg_passwd, pg_port, pg_db)
tdb = DbClient(pg_trade_host, pg_trade_user, pg_trade_passwd, pg_trade_port, pg_trade_db)
