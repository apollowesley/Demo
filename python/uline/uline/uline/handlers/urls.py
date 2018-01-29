# -*- coding: utf-8 -*-

from uline.utils.urls import include

urls = [
    #     url(r"/", HomeHandler),
    #     url(r"/docs", DocsHandler),
    #     url(r"/docs/version/(.*)", web.StaticFileHandler,
    #         {"path": settings.DOCS_ROOT}),
    #     (r"/static/(.*)", StaticHandler),
]

# distributor 账户登录,登出
# 渠道商
# 账户管理
urls += include(r"/dist/", "uline.handlers.app.distributor.account.urls")
# 进件管理
urls += include(r"/dist/inlet/", "uline.handlers.app.distributor.inlet.urls")
# 结算管理
urls += include(r'/dist/balance/',
                'uline.handlers.app.distributor.balance.urls')
# 交易管理
urls += include(r'/dist/transaction/',
                'uline.handlers.app.distributor.transaction.urls')
# 数据统计
urls += include(r"/dist/stats/",
                "uline.handlers.app.distributor.statistics.urls")

# 渠道商子账户
urls += include(r"/dist/sub_user/",
                "uline.handlers.app.distributor.sub_user.urls")
# 渠道商子账户
urls += include(r"/dist/settings/",
                "uline.handlers.app.distributor.system_settings.urls")


# 其他功能
urls += include(r"/dist/utils/", "uline.handlers.app.distributor.utils.urls")

# 资金账户
urls += include(r"/dist/capital/",
                "uline.handlers.app.distributor.capital.urls")

# 银行
# 账户管理
urls += include(r"/bank/", "uline.handlers.app.bank.account.urls")
# 结算管理
urls += include(r"/bank/balance/", "uline.handlers.app.bank.balance.urls")
# 进件管理
urls += include(r"/bank/inlet/", "uline.handlers.app.bank.inlet.urls")
# 交易管理
urls += include(r"/bank/transaction/", "uline.handlers.app.bank.transaction.urls")
# 对账管理
urls += include(r"/bank/recon/", "uline.handlers.app.bank.reconciliation.urls")
# 数据统计
urls += include(r"/bank/stats/", "uline.handlers.app.bank.statistics.urls")
# 其他功能
urls += include(r"/bank/utils/", "uline.handlers.app.bank.utils.urls")
# 资金账户
urls += include(r"/bank/capital/", "uline.handlers.app.bank.capital.urls")
# 优惠活动
urls += include(r"/bank/subsidize/", "uline.handlers.app.bank.subsidize.urls")
# 风控
urls += include(r"/bank/risk/", "uline.handlers.app.bank.risk.urls")

# 同业银行
# 进件管理
urls += include(r"/inter_bank/inlet/", "uline.handlers.app.inter_bank.inlet.urls")
# 账户管理
urls += include(r"/inter_bank/", "uline.handlers.app.inter_bank.account.urls")
# 结算管理
urls += include(r"/inter_bank/balance/", "uline.handlers.app.inter_bank.balance.urls")
# 交易管理
urls += include(r"/inter_bank/transaction/", "uline.handlers.app.inter_bank.transaction.urls")
# 其他功能
urls += include(r"/inter_bank/utils/", "uline.handlers.app.inter_bank.utils.urls")

# 数据统计
urls += include(r"/inter_bank/stats/", "uline.handlers.app.inter_bank.statistics.urls")

# 风控
urls += include(r"/inter_bank/risk/", "uline.handlers.app.inter_bank.risk.urls")

# 官方
# 账户管理
urls += include(r'/official/', 'uline.handlers.app.official.account.urls')
# 结算管理
urls += include(r'/official/balance/',
                'uline.handlers.app.official.balance.urls')
# 进件管理
urls += include(r'/official/inlet/', 'uline.handlers.app.official.inlet.urls')
# 交易管理
urls += include(r'/official/transaction/',
                'uline.handlers.app.official.transaction.urls')
# 对账管理
urls += include(r'/official/recon/',
                'uline.handlers.app.official.reconciliation.urls')
# 数据统计
urls += include(r"/official/stats/",
                "uline.handlers.app.official.statistics.urls")

# 其他功能
urls += include(r"/official/utils/", "uline.handlers.app.official.utils.urls")

# 资金账户
urls += include(r"/official/capital/",
                "uline.handlers.app.official.capital.urls")

# 运营管理
urls += include(r"/official/operations/",
                "uline.handlers.app.official.operations.urls")

# 优惠信息
urls += include(r"/official/subsidize/", "uline.handlers.app.official.subsidize.urls")

urls += include(r"/official/risk/", "uline.handlers.app.official.risk.urls")

# 商户
# 账户管理
urls += include(r"/merchant/", "uline.handlers.app.merchant.account.urls")
# 进件管理
urls += include(r"/merchant/inlet/", "uline.handlers.app.merchant.inlet.urls")
# 结算管理
urls += include(r'/merchant/balance/',
                'uline.handlers.app.merchant.balance.urls')
# 交易管理
urls += include(r'/merchant/transaction/',
                'uline.handlers.app.merchant.transaction.urls')
# 其他功能
urls += include(r"/merchant/utils/", "uline.handlers.app.merchant.utils.urls")
# 系统设置
urls += include(r"/merchant/settings/",
                "uline.handlers.app.merchant.system_settings.urls")
# 数据统计
urls += include(r"/merchant/stats/",
                "uline.handlers.app.merchant.statistics.urls")
# 资金账户
urls += include(r"/merchant/capital/",
                "uline.handlers.app.merchant.capital.urls")

# 连锁商户
# 账户管理
urls += include(r"/chain/", "uline.handlers.app.chain.account.urls")
# 进件管理
urls += include(r"/chain/inlet/", "uline.handlers.app.chain.inlet.urls")
# 结算管理
urls += include(r'/chain/balance/',
                'uline.handlers.app.chain.balance.urls')
# 交易管理
urls += include(r'/chain/transaction/',
                'uline.handlers.app.chain.transaction.urls')

# 数据统计
urls += include(r"/chain/stats/",
                "uline.handlers.app.chain.statistics.urls")

# 系统设置
urls += include(r"/chain/settings/",
                "uline.handlers.app.chain.system_settings.urls")

# 其他功能
urls += include(r"/chain/utils/", "uline.handlers.app.chain.utils.urls")

# 通用功能
urls += include(r"/common/", "uline.handlers.app.common.urls")
urls += include(r"/account/", "uline.handlers.app.account.urls")
urls += include(r"/common/settings/", "uline.handlers.app.common.system_settings.urls")
urls += include(r"/common/permit/", "uline.handlers.app.common.permit.controller.urls")

# D0提现手续费
urls += include(r"/api/fee/", "uline.handlers.api.fee.urls")

# 风险回调信息
urls += include(r"/risk/", "uline.handlers.api.risk.urls")
urls += include(r"//risk/", "uline.handlers.api.risk.urls")
