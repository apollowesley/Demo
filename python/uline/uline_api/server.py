# -*- coding:utf-8 -*-
import sys
import tornado.ioloop
import tornado.web
import tornado.httpserver
from uline_api.application import Application
from uline_api.setting import SERVER_PORT, SERVER_ADDRESS
from uline_api.util import config_check
from tornado.options import define, options
import traceback


define("port", default=SERVER_PORT, help="run on the given port", type=int)
options.parse_command_line()
server_port = options.port


def main():
    config_check.check()
    application = Application()
    application.listen(port=server_port, address=SERVER_ADDRESS)
    print('Production server is running at http://{}:{}/'.format(
        SERVER_ADDRESS, SERVER_PORT))
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
