# -*- coding: utf-8 -*-

import os


bind = '0.0.0.0:80'
workers = os.cpu_count()
worker_class = 'tornado'
