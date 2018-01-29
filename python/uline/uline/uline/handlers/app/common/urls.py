#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url
from .qr_view import QrDownload
from .browser import BrowserHandler
from .update_ali_level import UpdateAliLevel
from .get_mch_profile import Getmchprofiles
from . downloads_merchant_bill import DownloadsMerchantBill
from .permit.controller.role_controller import RoleController
from .permit.controller.permit_controller import PermitController
from .permit.controller.have_permit_controller import HavePermitController

# 前缀common
urls = [
    url(r'/qrdownload', QrDownload),
    url(r'/browser', BrowserHandler),
    url(r'/update', UpdateAliLevel),
    url(r'/query_mch', Getmchprofiles),
    url(r'/downloads_bill', DownloadsMerchantBill),
    url(r'/role', RoleController),
    url(r'/role/permit', PermitController),
    url(r'/have_permission', HavePermitController)
]
