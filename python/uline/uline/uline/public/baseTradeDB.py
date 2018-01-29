# -*- coding:utf-8 -*-
from uline.public import log
from uline.settings import pg_trade_host, pg_trade_db, pg_trade_port, pg_trade_user, pg_trade_passwd
from psycopg2.pool import SimpleConnectionPool
from psycopg2 import DatabaseError
from contextlib import contextmanager
from tornado.web import HTTPError

from psycopg2.extras import DictCursor


def Singleton(cls):
    instances = {}

    def getinstance(*args, **kwargs):
        key = (cls, args, frozenset(kwargs.items()))
        if key not in instances:
            instances[key] = cls(*args, **kwargs)
        return instances[key]

    return getinstance


@Singleton
class TradeDbClient(object):

    def __init__(self, db_host=pg_trade_host, db_usr=pg_trade_user, db_pw=pg_trade_passwd, db_port=pg_trade_port, cb_db=pg_trade_db, **kwargs):
        self.pool = SimpleConnectionPool(1, 10, host=db_host,
                                         user=db_usr, password=db_pw, dbname=cb_db, port=db_port)

    @contextmanager
    def get_db(self, use_dict=False):
        connect = self.pool.getconn()
        connect.set_client_encoding('UTF8')
        try:
            if use_dict:
                yield connect.cursor(cursor_factory=DictCursor)
            else:
                yield connect.cursor()
        finally:
            self.pool.putconn(connect)

    def selectSQL(self, sql, args=None, fetchone=True, use_dict=False):
        db_result = ''
        with self.get_db(use_dict=use_dict) as cur:
            try:
                if args:
                    cur.execute(sql, args)
                else:
                    cur.execute(sql)
            except DatabaseError as err:
                log.exception.info(err)
                cur.connection.commit()
            except Exception as err:
                import traceback
                traceback.print_exc(err)
                log.exception.info(err)
                raise HTTPError(500)
            else:
                db_result = cur.fetchone() if fetchone else cur.fetchall()
        return db_result

    def executeSQL(self, sql, args=None, use_dict=False):
        db_result = 0
        with self.get_db(use_dict=use_dict) as cur:
            try:
                if args:
                    db_result = cur.execute(sql, args) if isinstance(
                        args, tuple) else cur.executemany(sql, args)
                else:
                    db_result = cur.execute(sql)
            except Exception as err:
                import traceback
                traceback.print_exc(err)
                cur.connection.rollback()
                log.exception.info(err)
                raise HTTPError(500)
            else:
                cur.connection.commit()
        return db_result
