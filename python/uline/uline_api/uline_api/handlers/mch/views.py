#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '12/14/16'

from tornado.gen import coroutine
from uline_api.handlers.baseHandlers import RESTfulHandler, RESTfulHTTPError
from .form import GetMCHPayKey, MerchantForm
import binascii
import StringIO
from base64 import b64encode
import random
import string
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from uline_api.model.uline.user import DtUser, MchUser
from uline_api.model.uline.info import MchBalance, MchPayment, MchInletInfo
from uline_api.model.uline.d0 import MchAsset

# 需要过滤掉的商户表字段
MCH_ATTRS_EXCLUDED = ('id', 'mch_id', 'create_at', 'update_at',  # 多个表包含的信息
                      'mch_pay_key', 'api_key', 'password', 'email', 'mch_name', 'wx_sub_mch_id', 'auth_at',
                      'license_start_date')  # MchUser表

MCH_INLET_INCLUDED = ('province', 'city', 'mch_shortname',
                      'mch_name', 'address', 'auth_status')


def padding(text):
    output = StringIO.StringIO()
    val = 16 - (len(text) % 16)
    for _ in xrange(val):
        output.write('{:x}'.format(val))
    return text + binascii.unhexlify(output.getvalue())


class MerchantBaseHandler(RESTfulHandler):
    def prepare(self):
        if self.request.method == 'GET':
            super(MerchantBaseHandler, self).prepare()
            self.form = MerchantForm(self)
            setattr(self.form, 'dt_id', self.dt_id)


class MerchantHandler(MerchantBaseHandler):
    """
    处理商户请求，当前只支持GET请求
    """

    @coroutine
    def get(self):
        """
        通过商户ID(mch_id),获取该商户的详细信息
        :return: 该商户的详细信息
        """
        if not self.form.validate():
            raise RESTfulHTTPError(400, content=self.form.errors)

        mch_id = self.form.mch_id.data
        mch_info = {}

        mch_user = MchUser.get_by(mch_id=mch_id).first()
        mch_balance = MchBalance.get_by(mch_id=mch_id).first()
        # 一个商户对应多种支付方式
        mch_payments = MchPayment.get_by(mch_id=mch_id).all()

        mch_inlet = MchInletInfo.get_by(mch_id=mch_id).first()

        mch_info['mch_id'] = mch_id
        mch_info['mch_user'] = mch_user.to_dict(MCH_ATTRS_EXCLUDED)
        mch_info['mch_balance'] = mch_balance.to_dict(
            MCH_ATTRS_EXCLUDED) if mch_balance else {}
        mch_info['mch_payments'] = [mch_payment.to_dict(MCH_ATTRS_EXCLUDED)
                                    for mch_payment in mch_payments]
        mch_info['mch_inlet'] = mch_inlet.to_dict(
            MCH_INLET_INCLUDED, excluded=False) if mch_inlet else {}

        self.finish(mch_info)


class GetMchPayKey(MerchantBaseHandler):
    """获取商户支付密钥"""

    @coroutine
    def get(self):
        if not self.form.validate():
            raise RESTfulHTTPError(400, content=self.form.errors)

        mch_user = MchUser.get_by(mch_id=self.form.mch_id.data).first()
        if mch_user.status != 2:
            raise RESTfulHTTPError(400, content={'mch_id': ['用户未激活']})

        backend = default_backend()

        iv = ''.join(random.choice(string.ascii_letters) for i in range(16))

        dt_api_key = DtUser.get_by(dt_id=self.dt_id).first().api_key

        cipher = Cipher(algorithms.AES(str(dt_api_key)),
                        modes.CBC(iv), backend=backend)
        encryptor = cipher.encryptor()

        ct = encryptor.update(padding(str(mch_user.mch_pay_key))) + encryptor.finalize()

        self.finish({'mch_pay_key': iv + b64encode(ct)})


class GetMchWithdrawBalance(MerchantBaseHandler):
    """获取商户可提现金额"""

    @coroutine
    def get(self):
        if not self.form.validate():
            raise RESTfulHTTPError(400, content=self.form.errors)
        mch_asset = MchAsset.get_by(mch_id=self.form.mch_id.data).first()
        result = {
            'wx_balance': getattr(mch_asset, 'wx_total', 0),
            'ali_balance': getattr(mch_asset, 'ali_total', 0),
        }
        self.finish(result)
