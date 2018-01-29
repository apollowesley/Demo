# -*- coding: utf-8 -*-

from uline_api.util.urls import include

urls = [
    #     url(r"/", HomeHandler),
    #     url(r"/docs", DocsHandler),
    #     url(r"/docs/version/(.*)", web.StaticFileHandler,
    #         {"path": settings.DOCS_ROOT}),
    #     url(r"/static/(.*)", web.StaticFileHandler,
    #         {"path": settings.STATIC_ROOT})
]

# 商户进件
urls += include(r"/v1/mchinlet", "uline_api.handlers.mch_inlet.urls")
urls += include(r"/v1/mch", "uline_api.handlers.mch.urls")
