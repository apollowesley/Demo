#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url

from .merchantInletIndex import MerchantInletIndexHandler
from .distributorInletIndex import DistributorInletIndexHandler
from .getMerchantInfo import GetMerchantInfoHandler
from .addDistributor import AddDistributorInletHandler
from .getBankInfo import GetBankInfoHandler
from .getDistributorInfo import GetDistributorInfoHandler
from .modifyDistributor import ModifyDistributorInletHandler

from .exportMerchant import ExportMerchantHandler
from .exportCs import ExportCsHandler
from .exportDistributor import ExportDistributorHandler
from .exportChain import ExportChainHandler
from .resend_active_email import ResendMchActiveEmailHandler
from .chain_index import ChainInletIndexHandler
from .cs_index import CSInletIndexHandler

from .chain_wx_config import ChainWxConfigHandler
from .mch_wx_config import GetMerchantWxConfigHandler
from .resend_chain_active_email import ResendChainActiveEmailHandler

from .inter_bank_index import InterBankInletIndexHandler
from .inter_bank_modify import ModifyInterBnakInletHandler
from .inter_bank_add import AddInterBankInletHandler

# 前缀/official/inlet
urls = [
    url(r'/mch', MerchantInletIndexHandler),
    url(r'/mch/detail', GetMerchantInfoHandler),
    url(r'/mch/export', ExportMerchantHandler),
    url(r'/mch/resend_active_email', ResendMchActiveEmailHandler),
    url(r'/mch/wx_config', GetMerchantWxConfigHandler),
    url(r'/dt', DistributorInletIndexHandler),
    url(r'/dt/add', AddDistributorInletHandler),
    url(r'/dt/bank', GetBankInfoHandler),
    url(r'/dt/detail', GetDistributorInfoHandler),
    url(r'/dt/modify', ModifyDistributorInletHandler),
    url(r'/dt/export', ExportDistributorHandler),

    # 连锁商户
    url(r'/chain', ChainInletIndexHandler),
    url(r'/chain/detail', GetDistributorInfoHandler),
    url(r'/chain/export', ExportChainHandler),
    url(r'/chain/wx_config', ChainWxConfigHandler),
    url(r'/chain/resend_active_email', ResendChainActiveEmailHandler),

    url(r'/cs', CSInletIndexHandler),
    url(r'/cs/detail', GetMerchantInfoHandler),
    url(r'/cs/export', ExportCsHandler),

    # 同业银行
    url(r'/inter_bank', InterBankInletIndexHandler),
    url(r'/inter_bank/add', AddInterBankInletHandler),
    url(r'/inter_bank/modify', ModifyInterBnakInletHandler),

]
