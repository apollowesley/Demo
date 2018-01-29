#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url

from .mch_index import MerchantInletIndexHandler
from .dt_index import DistributorInletIndexHandler
from .mch_info import GetMerchantInfoHandler
from .mch_auth import AuthMerchantInletStatusHandler
from .mch_deny import DenyMerchantInletStatusHandler
from .mch_active import ActivatedMerchantInletStatusHandler
from .mch_close import CloseMerchantPaymentHandler
from .mch_batch_close import CloseBatchMerchantPaymentHandler
from .mch_wx_config import GetMerchantWxConfigHandler
from .mch_close_balance import CloseBalanceHandle

from .dt_info import GetDistributorInfoHandler
from .dt_auth import AuthDistributorInletStatusHandler
from .dt_deny import DenyDistributorInletStatusHandler
from .dt_active import ActivatedDistributorInletStatusHandler
from .mch_batch_active import ActivatedBatchMerchantInletStatusHandler
from .dt_batch_active import ActivatedBatchDistributorInletStatusHandler
from .dt_close import CloseDistributorPaymentHandler
from .dt_batch_close import CloseBatchDistributorPaymentHandler

from .mch_export import ExportMerchantHandler
from .dt_export import ExportDistributorHandler
from .chain_export import ExportChainHandler

from .chain_index import ChainInletIndexHandler
from .chain_info import GetChainInfoHandler
from .chain_active import ActivatedChainInletStatusHandler
from .chain_batch_active import ActivatedBatchChainInletStatusHandler
from .chain_close import CloseChainPaymentHandler
from .chain_batch_close import CloseBatchChainPaymentHandler
from .chain_auth import AuthChainInletStatusHandler
from .chain_wx_config import ChainWxConfigHandler

from .cs_index import CSInletIndexHandler
from .cs_export import ExportCsHandler
from .cs_active import ActivatedCsInletStatusHandler
from .cs_info import GetCSInfoHandler
from .cs_batch_active import ActivatedBatchCsInletStatusHandler

from .inter_bank_index import InterBankInletIndexHandler


# 前缀/bank/inlet

urls = [
    url(r'/mch', MerchantInletIndexHandler),
    url(r'/mch/detail', GetMerchantInfoHandler),
    url(r'/mch/close', CloseMerchantPaymentHandler),
    url(r'/mch/batchClose', CloseBatchMerchantPaymentHandler),
    url(r'/mch/auth', AuthMerchantInletStatusHandler),
    url(r'/mch/deny', DenyMerchantInletStatusHandler),
    url(r'/mch/activated', ActivatedMerchantInletStatusHandler),
    url(r'/mch/batchActivated', ActivatedBatchMerchantInletStatusHandler),
    url(r'/mch/export', ExportMerchantHandler),
    url(r'/mch/wx_config', GetMerchantWxConfigHandler),
    url(r'/mch/changebalance', CloseBalanceHandle),  # 冻结或者解冻

    url(r'/dt', DistributorInletIndexHandler),
    url(r'/dt/detail', GetDistributorInfoHandler),
    url(r'/dt/close', CloseDistributorPaymentHandler),
    url(r'/dt/batchClose', CloseBatchDistributorPaymentHandler),
    url(r'/dt/auth', AuthDistributorInletStatusHandler),
    url(r'/dt/deny', DenyDistributorInletStatusHandler),
    url(r'/dt/activated', ActivatedDistributorInletStatusHandler),
    url(r'/dt/batchActivated', ActivatedBatchDistributorInletStatusHandler),
    url(r'/dt/export', ExportDistributorHandler),

    # 连锁商户
    url(r'/chain', ChainInletIndexHandler),
    url(r'/chain/detail', GetChainInfoHandler),
    url(r'/chain/export', ExportChainHandler),
    url(r'/chain/activated', ActivatedChainInletStatusHandler),
    url(r'/chain/batchActivated', ActivatedBatchChainInletStatusHandler),
    url(r'/chain/close', CloseChainPaymentHandler),
    url(r'/chain/batchClose', CloseBatchChainPaymentHandler),
    url(r'/chain/auth', AuthChainInletStatusHandler),
    url(r'/chain/wx_config', ChainWxConfigHandler),

    url(r'/cs', CSInletIndexHandler),
    url(r'/cs/detail', GetCSInfoHandler),
    url(r'/cs/export', ExportCsHandler),
    url(r'/cs/activated', ActivatedCsInletStatusHandler),
    url(r'/cs/batchActivated', ActivatedBatchCsInletStatusHandler),

    url(r'/inter_bank', InterBankInletIndexHandler),

]

