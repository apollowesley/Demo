# -*- coding:utf-8 -*-

import sys
import traceback

import tornado.ioloop
import tornado.httpserver

from tornado.options import (
    options,
    define,
)

from uline_risk.application import Application
from uline_risk.settings import (
    SERVER,
    SERVER_PORT,
    ENV,
)


define("port", default=SERVER_PORT, help="run on the given port", type=int)


ENVS = ['DEV', 'LOCAL', 'CMBC_PROD', 'SPD_PROD', 'SPDLOCAL']


app = Application()


def main():
    if ENV not in ENVS:
        raise Exception('必须设置ENV环境变量')

    options.parse_command_line()
    server_port = options.port
    app.listen(server_port)
    print('risk server is running at http://{}:{}/'.format(SERVER, SERVER_PORT))
    print('Quit the server with Control-C')
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        traceback.print_exc(e)
        print("     >>>>> App terminating.....\n")
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n")
        print("KI")
        print("     >>>>> App terminating.....\n")
        sys.exit(0)
