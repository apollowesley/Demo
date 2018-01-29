#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import datetime
from uline.public.constants import AVAILABLE_PAYMENTS_FORMAT, translate_payment_type, new_payment_relations, \
    old_payment_relations
# from uline.public.db import initdb, uline_session_scope
from uline.model.uline.base import uline_session
from uline.model.uline.info import MchPayment, DtPayment, MchInletInfo, D0WithdrawFee
from uline.model.uline.user import MchUser
from uline.model.uline.other import ChangeRecord
from tornado import ioloop
import argparse


from uline.model.uline.base import Model as uline_Model, uline_Session
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from uline.backend.__init__ import *

# sqlalchemy_uline_db = 'postgresql+psycopg2://ulinesa:Xm.u7!nebio2@192.168.20.100:5432/spd_uline'
sqlalchemy_uline_db = 'postgresql+psycopg2://ulinesa:Xm.u7!nebio2@127.0.0.1:16691/spd_uline'
# sqlalchemy_uline_db = 'postgresql+psycopg2://uline:uline2015@127.0.0.1:7890/uline'


def initdb():
    uline_engine = create_engine(sqlalchemy_uline_db, echo=False)
    uline_Session.configure(bind=uline_engine)
    uline_Model.metadata.bind = uline_engine


def get_chain_id():
    """从命令行获取渠道商id"""
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('dt_id', metavar='DT_ID', type=str,
                        help='input dt_id')
    args = parser.parse_args()
    return args.dt_id


def get_mch_ids(cursor, chain_id):
    query = """SELECT mch_id FROM mch_inlet_info WHERE cs_id=%s"""
    cursor.execute(query, (chain_id,))
    mch_ids = cursor.fetchall()
    return [str(mch_id[0]) for mch_id in mch_ids]


def get_paymnets(cursor, chain_id):
    pass


@contextmanager
def uline_session_scope():
    session = uline_Session()
    try:
        yield session
        print 'session commit'
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def add_mch_payment_type(cur, mch_id, all_paymnet_type):
    for payment_type in all_paymnet_type:
        query = """SELECT 1 FROM mch_payment WHERE mch_id=%s and payment_type=%s"""
        cur.execute(query, (mch_id, payment_type))
        ret = cur.fetchone()
        if ret:
            continue
        else:
            tmp_str = translate_payment_type.get(payment_type)
            uline_payment_id, uline_settle_id, trade_type,\
                thirdparty_mch_id, uline_payment_code = tmp_str.split('|')
            dt_id = '10000096983'
            thirdparty_mch_id = '69215744'
            query = """INSERT INTO mch_payment(mch_id, settle_rate, uline_payment_id, uline_payment_code,
                                              uline_settle_id, trade_type,
                                              payment_type, payment_rate, activated_status,
                                              create_at, update_at, dt_id, thirdparty_mch_id)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
            cur.execute(query, (mch_id, 30, uline_payment_id, uline_payment_code,
                                uline_settle_id, trade_type,
                                payment_type, 30, 2, datetime.datetime.now(), datetime.datetime.now(),
                                dt_id, thirdparty_mch_id))


def main():
    dt_id = get_chain_id()
    with db.get_db() as cur:
        mch_ids = get_mch_ids(cur, dt_id)
        print mch_ids

        # all_paymnet_type = get_paymnets(cur, dt_id)

    # mch_ids = ['100053015582']
    all_paymnet_type = [2, 3]
    print mch_ids
    print all_paymnet_type
    for mch_id in mch_ids:
        with db.get_db() as cur:
            add_mch_payment_type(cur, mch_id, all_paymnet_type)


if __name__ == "__main__":
    initdb()
    ioloop.IOLoop.instance().run_sync(main)
