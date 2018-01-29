# -*- coding:utf-8 -*-
import re
import traceback
from uline.public import log
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
from tornado.web import HTTPError


def Singleton(cls):
    instances = {}

    def getinstance(*args, **kwargs):
        key = (cls, args, frozenset(kwargs.items()))
        if key not in instances:
            instances[key] = cls(*args, **kwargs)
        return instances[key]

    return getinstance


@Singleton
class DbClient(object):

    def __init__(self, db_host=None, db_usr=None, db_pw=None, db_port=None, cb_db=None, **kwargs):
        self.pool = ThreadedConnectionPool(1, 16, host=db_host, user=db_usr,
                                           password=db_pw, dbname=cb_db, port=db_port)

    @contextmanager
    def get_db(self):
        connect = self.pool.getconn()
        connect.set_client_encoding('UTF8')
        try:
            yield connect.cursor()
            connect.commit()
        except Exception as err:
            traceback.print_exc(err)
            log.exception.info(err)
            connect.rollback()
            raise HTTPError(500)
        finally:
            self.pool.putconn(connect)

    def selectSQL(self, sql, args=None, fetchone=True):
        db_result = ''
        with self.get_db() as cur:
            if args:
                cur.execute(sql, args)
            else:
                cur.execute(sql)
            db_result = cur.fetchone() if fetchone else cur.fetchall()
            cur.close()
            cur.connection.commit()
        return db_result

    def executeSQL(self, sql, args=None):
        db_result = 0
        with self.get_db() as cur:
            if args:
                db_result = cur.execute(sql, args) if isinstance(
                    args, tuple) else cur.executemany(sql, args)
            else:
                db_result = cur.execute(sql)
        return db_result

    def escape(self, value):
        """
        转义字符串以在sql语句正则查询中用
        """
        if value:
            # 如果是数字，转化成字符串
            if not isinstance(value, basestring):
                value = str(value)
            # re.escape 在这里满足不了需求.
            # 1. 需要应对unicode和ascii字符。
            # 2. 需要双重转义, postgresql 正则需要\\[特殊字符] 这样的格式。
            return re.sub(r"[(){}\[\].*?|^$\\+-]", r"\\\\\g<0>", value)
        else:
            # 查询字符串是None， 或是空'', 我们认为是一样的
            return ''
