#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url

from .cs_index import CsInletIndexHandler
from .cs_add import AddCsInletHandler
from .chain_index import ChainAdminHandler
# from .mch_export import ExportMerchantHandler
from .bank_info import GetBankInfoHandler
from .cs_info import GetCsInfoHandler
from .cs_modify import ModifyCsInletHandler
from .cs_batch_info import CSBatchInletInfoHandler
from .cs_excel_import import ImportCSExcelHandler
from .cs_img_import import ImportCSImageHandler
from .cs_batch_operate import CSBatchInletOperateHandler
from .chain_index import ChainInletIndexHandler
from .cs_export import ExportCsHandler
from .resend_active_email import ResendMchActiveEmail

# 前缀/chain/inlet

urls = [
    url(r'/cs', CsInletIndexHandler),
    url(r'/cs/add', AddCsInletHandler),
    url(r'/cs/bank', GetBankInfoHandler),
    url(r'/cs/detail', GetCsInfoHandler),
    url(r'/cs/modify', ModifyCsInletHandler),
    url(r'/cs/batch/excel', ImportCSExcelHandler),
    url(r'/cs/batch/image', ImportCSImageHandler),
    url(r'/cs/batch/info', CSBatchInletInfoHandler),
    url(r'/cs/batch/operate', CSBatchInletOperateHandler),
    url(r'/cs/export', ExportCsHandler),
    url(r'/chain', ChainInletIndexHandler),
    url(r'/cs/resend_active_email', ResendMchActiveEmail),

]
