# -*- coding:utf-8 -*-
import os
import logging.config
import logging
import cloghandler

config_dir = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))))
LOGGING_CONF_FILE = config_dir + "/etc/logging.conf"


class Logging:
    log_instance = None

    @staticmethod
    def InitLogConf():
        Logging.log_instance = logging.config.fileConfig(LOGGING_CONF_FILE)

    @staticmethod
    def GetLogger(name=""):
        if Logging.log_instance is None:
            print 'initlogConf'
            Logging.InitLogConf()
        Logging.log_instance = logging.getLogger(name)
        return Logging.log_instance


detail = Logging.GetLogger('detail')
request = Logging.GetLogger('request')
exception = Logging.GetLogger('exception')
longrecord = Logging.GetLogger('longrecord')
uline_celery = Logging.GetLogger('uline_celery')
uline_script = Logging.GetLogger('uline_script')
uline_dailycut = Logging.GetLogger('uline_dailycut')
