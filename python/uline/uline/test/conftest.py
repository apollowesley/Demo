#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '11/1/16'

import codecs
import pytest
from os import path
from sqlalchemy import create_engine
from uline.setting import test_sqlalchemy_uline_db, test_sqlalchemy_uline_trade_db
from uline.model.uline.base import Base as Model, uline_Session, uline_session as _uline_session
from uline.model.uline_trade.base import Base as trade_Model, trade_Session, trade_session as _trade_session
from uline.setting import env
from .generate_test_db_data import main
from uline.model.uline.clear import MchClearInfo, DtClearInfo, PClearInfo
from uline.model.uline.error import ReconRefundErrorInfo, ReconTxErrorInfo
from uline.model.uline.balance import MchDailyBalanceInfo, DtDailyBalanceInfo, PDailyBalanceInfo
from uline.model.uline_trade.order import Order, OrderRefund


@pytest.fixture(autouse=True)
def uline_session(request):
    # 重建数据库
    uline_engine = create_engine(test_sqlalchemy_uline_db, connect_args={'connect_timeout': 2})
    uline_connection = uline_engine.connect()
    uline_transaction = uline_connection.begin()
    uline_Session.configure(bind=uline_engine)
    Model.metadata.bind = uline_engine
    # 仅仅删除订单相关的表
    MchClearInfo.__table__.drop(uline_engine, checkfirst=True)
    DtClearInfo.__table__.drop(uline_engine, checkfirst=True)
    PClearInfo.__table__.drop(uline_engine, checkfirst=True)
    MchDailyBalanceInfo.__table__.drop(uline_engine, checkfirst=True)
    DtDailyBalanceInfo.__table__.drop(uline_engine, checkfirst=True)
    PDailyBalanceInfo.__table__.drop(uline_engine, checkfirst=True)
    ReconRefundErrorInfo.__table__.drop(uline_engine, checkfirst=True)
    ReconTxErrorInfo.__table__.drop(uline_engine, checkfirst=True)

    Model.metadata.create_all(checkfirst=True)

    def tearDown():
        _uline_session.close()
        uline_transaction.rollback()
        uline_connection.close()

    request.addfinalizer(tearDown)


@pytest.fixture(autouse=True)
def trade_session(request):
    # 重建数据库
    trade_engine = create_engine(test_sqlalchemy_uline_trade_db, connect_args={'connect_timeout': 2})
    trade_connection = trade_engine.connect()
    trade_transaction = trade_connection.begin()
    trade_Session.configure(bind=trade_engine)
    trade_Model.metadata.bind = trade_engine

    Order.__table__.drop(trade_engine, checkfirst=True)
    OrderRefund.__table__.drop(trade_engine, checkfirst=True)

    trade_Model.metadata.create_all(checkfirst=True)

    def tearDown():
        _trade_session.close()
        trade_transaction.rollback()
        trade_connection.close()

    request.addfinalizer(tearDown)


def ingore_test(func):
    # 有一些测试只在银行测试环境进行
    if env == 'DEV':
        return func
    else:
        return


@pytest.fixture(autouse=True)
def gereate_user(uline_session, request):
    # 基础数据 仅当不存在的时候生成
    # 生成一个银行账号,2个渠道商,每个渠道商2个商户
    main()
