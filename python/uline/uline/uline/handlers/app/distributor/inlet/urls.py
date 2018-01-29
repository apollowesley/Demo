#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url

from .mch_index import MerchantInletIndexHandler
from .mch_add import AddMerchantInletHandler
from .dt_index import DistributorInletIndexHandler
from .mch_export import ExportMerchantHandler
from .cs_export import ExportCsHandler
from .bank_info import GetBankInfoHandler
from .mch_info import GetMerchantInfoHandler
from .mch_modify import ModifyMerchantInletHandler
from .mch_batch_info import MerchantBatchInletInfoHandler
from .callback import SetCallbackUrlHandler
from .mch_excel_import import ImportMerchantExcelHandler
from .mch_img_import import ImportMerchantImageHandler

from .mch_batch_operate import MerchantBatchInletOperateHandler

from .mch_wx_config import GetMerchantWxConfigHandler

from .chain_general_add import AddChainGeneralHandler
from .chain_general_index import ChainInletIndexHandler
from .chain_info import GetChainGeneralHandler
from .chain_modify import ModifyChainGeneralHandler
from .chain_export import ExportChainHandler
from .chain_wx_config import ChainWxConfigHandler

from .chain_branch_add import AddChainBranchHandler
from .cs_modify import ModifyCSInletHandler
from .cs_index import CSInletIndexHandler

from .get_chains import ChainSearchHandler
from .resend_active_email import ResendMchActiveEmailHandler
from .resend_chain_active_email import ResendChainActiveEmailHandler

from .cs_batch_info import CSBatchInletInfoHandler
from .cs_excel_import import ImportCSExcelHandler
from .cs_img_import import ImportCSImageHandler
from .cs_batch_operate import CSBatchInletOperateHandler
# 前缀/dist/inlet

urls = [
    # 商户
    url(r'/mch', MerchantInletIndexHandler),
    url(r'/mch/add', AddMerchantInletHandler),
    url(r'/mch/callbackurl', SetCallbackUrlHandler),
    url(r'/mch/export', ExportMerchantHandler),
    url(r'/mch/bank', GetBankInfoHandler),
    url(r'/mch/wx_config', GetMerchantWxConfigHandler),
    url(r'/mch/detail', GetMerchantInfoHandler),
    url(r'/mch/modify', ModifyMerchantInletHandler),
    url(r'/mch/batch/excel', ImportMerchantExcelHandler),
    url(r'/mch/batch/image', ImportMerchantImageHandler),
    url(r'/mch/batch/info', MerchantBatchInletInfoHandler),
    url(r'/mch/resend_active_email', ResendMchActiveEmailHandler),

    url(r'/mch/batch/operate', MerchantBatchInletOperateHandler),

    # 连锁商户
    url(r'/chain', ChainInletIndexHandler),
    url(r'/chain/add', AddChainGeneralHandler),
    url(r'/chain/modify', ModifyChainGeneralHandler),
    url(r'/chain/detail', GetChainGeneralHandler),
    url(r'/chain/export', ExportChainHandler),
    url(r'/chain/wx_config', ChainWxConfigHandler),
    url(r'/chain/resend_active_email', ResendChainActiveEmailHandler),

    # 连锁门店
    url(r'/cs', CSInletIndexHandler),
    url(r'/cs/add', AddChainBranchHandler),
    url(r'/cs/detail', GetMerchantInfoHandler),
    url(r'/cs/chains', ChainSearchHandler),
    url(r'/cs/modify', ModifyCSInletHandler),
    url(r'/cs/batch/excel', ImportCSExcelHandler),
    url(r'/cs/batch/image', ImportCSImageHandler),
    url(r'/cs/batch/info', CSBatchInletInfoHandler),
    url(r'/cs/batch/operate', CSBatchInletOperateHandler),
    url(r'/cs/export', ExportCsHandler),

    # 渠道商
    url(r'/dt', DistributorInletIndexHandler),
]
