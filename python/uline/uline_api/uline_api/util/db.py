#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/12/16'

from contextlib import contextmanager
from uline_api.util.log import error_log
from sqlalchemy import create_engine

from uline_api.setting import sqlalchemy_uline_db, sqlalchemy_uline_trade_db
from uline_api.model.uline.base import Model as uline_Model, uline_Session
from uline_api.model.uline_trade.base import (
    Model as trade_Model,
    trade_Session
)


def initdb():
    uline_engine = create_engine(
        sqlalchemy_uline_db,
        pool_recycle=3600,
        pool_size=10
    )
    uline_Session.configure(bind=uline_engine)
    uline_Model.metadata.bind = uline_engine

    trade_engine = create_engine(
        sqlalchemy_uline_trade_db,
        pool_recycle=3600,
        pool_size=10
    )
    trade_Session.configure(bind=trade_engine)
    trade_Model.metadata.bind = trade_engine


@contextmanager
def uline_session_scope():
    session = uline_Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        error_log.exception(u'uline数据库执行异常', exc_info=True)
        raise
    finally:
        session.close()


@contextmanager
def trade_session_scope():
    session = trade_Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        error_log.exception(u'uline_trade数据库执行异常', exc_info=True)
        raise
    finally:
        session.close()
