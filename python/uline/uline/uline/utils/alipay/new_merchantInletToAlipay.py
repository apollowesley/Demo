# -*- coding: utf-8 -*-
import json
import base64
import hashlib
from tornado import gen
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA, SHA256
from Crypto.PublicKey import RSA
from datetime import datetime
from urllib import quote_plus, urlencode
from uline.settings import ALI_APPID, ALI_PID, ALI_PRIVATE_KEY, ALI_PUB_KEY, ALI_SERVER_ADDRESS


class AliRSAEncryptionClass(object):
    with open(ALI_PRIVATE_KEY) as f:
        private_key = RSA.importKey(f.read())

    with open(ALI_PUB_KEY) as f:
        public_key = RSA.importKey(f.read())

    """
    处理rsa加密，校验
    """

    def __init__(self, params):
        self.server_address = ALI_SERVER_ADDRESS
        self.dict_params = params
        self.dict_params['biz_content'] = self.dict_params.pop('biz_content')
        self.dict_params["app_id"] = ALI_APPID
        self.dict_params["format"] = "JSON"
        self.dict_params["charset"] = "UTF-8"

        self.dict_params["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.dict_params["version"] = "1.0"
        self.dict_params["sign_type"] = "RSA"
        self.sorted_params = self.sort_params()

        self.sign_str = quote_plus(self.sign())
        self.final_url = self.server_address + "?" + urlencode(self.dict_params) + "&sign=" + self.sign_str

    def sort_params(self):
        sorted_keys = sorted(self.dict_params)
        sorted_params = []
        for key in sorted_keys:
            if self.dict_params[key] != "":
                sorted_params.append("{}={}".format(key, self.dict_params[key]))
        return "&".join(sorted_params)

    def sign(self):
        h = SHA.new(self.sorted_params.encode('UTF-8'))
        return base64.b64encode(PKCS1_v1_5.new(self.private_key).sign(h))

    @staticmethod
    def verify(data, sign):
        h = SHA.new(data)
        try:
            verifier = PKCS1_v1_5.new(AliRSAEncryptionClass.public_key)
            signature = verifier.verify(h, base64.decodestring(sign))
        except:
            signature = 0
        return signature


@gen.coroutine
def mch_inlet_to_alipay_data(biz_content, method):
    raise gen.Return(mch_inlet_to_alipay_data_block(biz_content, method))


def mch_inlet_to_alipay_data_block(biz_content, method):
    common_params = {
        "app_id": ALI_APPID,
        "method": method,
        "charset": "utf-8",
        "sign_type": "RSA",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "1.0",
        "biz_content": json.dumps(biz_content)
    }
    rsa_sign = AliRSAEncryptionClass(common_params)
    sign = rsa_sign.sign()
    common_params['sign'] = sign
    return urlencode(common_params)


class AliEncryptionClass(object):
    """
    处理rsa加密，校验
    """

    def __init__(self, params, config_info=None, crypto_type='RSA', charset='UTF-8'):
        self.charset = charset
        self.public_key = None
        self.private_key = None

        private_key_file = config_info.get('private_key_file')
        if private_key_file:
            with open(private_key_file) as f:
                self.private_key = RSA.importKey(f.read())

        public_key_file = config_info.get('pub_key_file')
        if public_key_file:
            with open(public_key_file) as f:
                self.public_key = RSA.importKey(f.read())

        self.hash_class = self.get_crypto_type_class(crypto_type)

        if not params:
            params = {}

        self.dict_params = params
        self.dict_params["app_id"] = config_info.get('app_id', '')
        self.dict_params["sign_type"] = crypto_type
        self.sorted_params = self.sort_params()

    def sort_params(self):
        sorted_keys = sorted(self.dict_params)
        sorted_params = []
        for key in sorted_keys:
            if self.dict_params[key] != "":
                sorted_params.append("{}={}".format(key, self.dict_params[key]))
        return "&".join(sorted_params)

    def sign(self):
        h = self.hash_class.new(self.sorted_params.encode(self.charset))
        return base64.b64encode(PKCS1_v1_5.new(self.private_key).sign(h))

    @staticmethod
    def verify(data, sign, public_key_file, hash_type='RSA'):
        if not public_key_file:
            return 0
        public_key = ''
        with open(public_key_file) as f:
            public_key = RSA.importKey(f.read())

        hash_class = AliEncryptionClass.get_crypto_type_class(hash_type)
        h = hash_class.new(data)
        try:
            verifier = PKCS1_v1_5.new(public_key)
            signature = verifier.verify(h, base64.decodestring(sign))
        except:
            signature = 0
        return signature

    @staticmethod
    def get_crypto_type_class(crypto_type):
        if crypto_type == 'RSA':
            return SHA
        elif crypto_type == 'RSA2':
            return SHA256
        else:
            return None

def query_mapi_info(method, biz_content, config_info, crypto_type='RSA', charset='UTF-8'):
    common_params = {
        "method": method,
        "format": "JSON",
        "charset": charset,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "1.0",
        "biz_content": json.dumps(biz_content),
    }

    signutil = AliEncryptionClass(common_params, config_info, crypto_type)
    sign = signutil.sign()
    common_params['sign'] = sign
    return urlencode(common_params), sign
