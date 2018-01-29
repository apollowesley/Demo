# -*- coding:utf-8 -*-
import sys
import tornado.ioloop
import tornado.web
import tornado.httpserver
from uline.application import Application
from uline.settings import (pg_host, server_port, env, pg_db, pg_trade_db, pg_trade_host, redis_host, redis_db,
                            WX_MCH_ID, server)
from uline.utils import config_check
import traceback
from tornado.options import define, options
from uline.public import log
from uline.public.db import initdb

define("port", default=server_port, help="run on the given port", type=int)
options.parse_command_line()
server_port = options.port


def record_block(_, frame):
    a = traceback.format_stack(frame)
    log.longrecord.warning('block time over 3 seconds ')
    log.longrecord.warning(''.join(a))


def main():

    initdb()
    # config_check.check()
    application = Application()
    application.listen(port=server_port)
    print("=========== start ===========")
    print("env == " + env)
    print("postgresql_uline == " + pg_host)
    print("postgresql_uline_db == " + pg_db)
    print("postgresql_uline_trade == " + pg_trade_host)
    print("postgresql_uline_trade_db == " + pg_trade_db)
    print("redis == " + redis_host)
    print("redis_db == " + str(redis_db))
    print("server port == " + str(server_port))
    print("wx_mch_id == " + str(WX_MCH_ID))
    print 'Production server is running at http://%s:%s/' % (server, server_port)
    print 'Quit the server with Control-C'
    tornado.ioloop.IOLoop.instance().set_blocking_signal_threshold(3, record_block)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        traceback.print_exc(e)
        print("     >>>>> App terminating.....\n")
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n")
        print("KI")
        print("     >>>>> App terminating.....\n")
        sys.exit(0)
