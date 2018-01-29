#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/26/16'

import os
import logging.config
import logging
from logging import handlers

config_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
LOGGING_CONF_FILE = config_dir + "/logging.conf"

logging.basicConfig(level=logging.CRITICAL)
logging.config.fileConfig(LOGGING_CONF_FILE)


def setup_logger(logger_name, log_file, level=logging.INFO):
    log = logging.getLogger(logger_name)
    log_dir = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))) + '/log/'
    log_path = log_dir + log_file + '.log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    if not os.path.isfile(log_path):
        open(log_path, 'a').close()

    formatter = logging.Formatter(
        '%(asctime)s %(pathname)s %(lineno)d %(levelname)-8s %(message)s')
    fileHandler = handlers.RotatingFileHandler(
        log_path, maxBytes=1024 * 1024 * 100, backupCount=5)
    fileHandler.setFormatter(formatter)

    if logger_name != 'error':
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)
        log.addHandler(streamHandler)
        log.propagate = False

    log.setLevel(level)
    log.addHandler(fileHandler)


setup_logger('error', 'error', logging.ERROR)
setup_logger('access', 'info')
setup_logger('info', 'info')

error_log = logging.getLogger('error')
access_log = logging.getLogger('access')
info_log = logging.getLogger('info')
