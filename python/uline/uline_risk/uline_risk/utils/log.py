# -*- coding:utf-8 -*-
import os
import logging.config
import logging
import cloghandler   # noqa

config_dir = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))))
LOGGING_CONF_FILE = config_dir + "/etc/logging.conf"
LOGGING_BASE_FILE = config_dir + "/etc/base_logging.conf"


class Logging:
    initialnized = False
    no_conf_loaded = True

    @staticmethod
    def InitLogConf():
        Logging.loadConfig(LOGGING_BASE_FILE)
        Logging.loadConfig(LOGGING_CONF_FILE)
        Logging.initialnized = True

    @staticmethod
    def loadConfig(config_filename):
        logging.config.fileConfig(config_filename, disable_existing_loggers=Logging.no_conf_loaded)
        if Logging.no_conf_loaded:
            Logging.no_conf_loaded = False

    @staticmethod
    def GetLogger(name=""):
        if not Logging.initialnized:
            print('initlogConf')
            Logging.InitLogConf()
        logger = logging.getLogger(name)
        return logger


detail = Logging.GetLogger('detail')
request = Logging.GetLogger('request')
exception = Logging.GetLogger('exception')
longrecord = Logging.GetLogger('longrecord')
