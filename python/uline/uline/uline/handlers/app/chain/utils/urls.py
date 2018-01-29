#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url

from .downloadEvents import DownloadEventsHandler
from .downloadExportFile import DownloadExportFileHandler
from .deleteExportFile import DeleteExportFileHandler

# chain
urls = [
    url(r'download', DownloadEventsHandler),
    url(r'download/export', DownloadExportFileHandler),
    url(r'download/delete', DeleteExportFileHandler),
]
