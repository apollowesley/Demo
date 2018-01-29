#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback

from datetime import datetime
from tornado.web import RequestHandler
from tornado import gen

from uline.utils.alipay.new_merchantInletToAlipay import AliEncryptionClass
from uline.utils.alipay import query_alipay_mapi
from uline.public import log
from uline.backend.risk.send_trade_risk_info import send_trade_risk_email
from uline import settings
from uline.utils.risk_api import risk_api_util


class AlipayTransactionRiskNotify(RequestHandler):
    def prepare(self):
        log.exception.info("alipay risk notify uri: {}".format(self.request.uri))
        log.exception.info("alipay risk notify body: {}".format(self.request.body))
        self.risk_info = {key: self.request.arguments[key][0] for key in self.request.arguments}
        sign = self.risk_info.get('sign', [''])
        self.charset = self.risk_info.get('charset', ['UTF-8'])

        sign_info = {key: self.risk_info[key] for key in self.risk_info if
                     self.risk_info[key] and key not in ['sign', 'sign_type']}
        sorted_keys = sorted(sign_info)
        self.sign_info = '&'.join(["{}={}".format(key, sign_info[key]) for key in sorted_keys if sign_info[key]])

        need_validate = True
        if need_validate:
            valid_sign_result = AliEncryptionClass.verify(self.sign_info, sign,
                                                          query_alipay_mapi.ALI_CONFIGS.get('risk').get('pub_key_file'),
                                                          hash_type=self.risk_info.get('sign_type', 'RSA'))
            if not valid_sign_result:
                self.write('sign failed')
                self.finish()
        self.current_time = datetime.now()

    @gen.coroutine
    def post(self):
        response = yield risk_api_util.query_risk_api("alipay_trade_risk_notify", params=self.request.body)
        is_success, errormsg = risk_api_util.check_response(response)
        risk_id = 0
        if is_success:
            log.exception.info("添加风险交易成功")
            risk_id = response.get("risk_id", 0)
            self.write("success")
        else:
            log.exception.info("添加交易风险失败,{}".format(response))
            self.write("fail")

        if risk_id:
            gen.Task(send_trade_risk_email.apply_async, args=[risk_id])
        self.finish()

    def write_error(self, status_code, **kwargs):
        if "exc_info" in kwargs:
            for line in traceback.format_exception(*kwargs["exc_info"]):
                log.exception.info(line)
        self.write('fail')

    def post_url(self):
        return settings.RISK_API_URL + self.request.uri

    def get(self):
        log.exception.info("alipay risk notify uri post: {}".format(self.request.uri))
        log.exception.info("alipay risk notify body post: {}".format(self.request.body))

    def check_xsrf_cookie(self):
        pass
