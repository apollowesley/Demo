# -*- coding: utf-8 -*-
import json
import base64
import hashlib
from tornado import gen
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
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
def mch_inlet_to_alipay_data(mch_id, mch_name, mch_shortname, service_phone, category_id):
    biz_content = {
        "external_id": mch_id,
        "name": mch_name,
        "alias_name": mch_shortname,
        "service_phone": service_phone,
        "category_id": category_id,
        "source": ALI_PID,

    }

    common_params = {
        "app_id": ALI_APPID,
        "method": "alipay.boss.prod.submerchant.create",
        "charset": "utf-8",
        "sign_type": "RSA",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "1.0",
        "biz_content": json.dumps(biz_content)
    }
    rsa_sign = AliRSAEncryptionClass(common_params)
    sign = rsa_sign.sign()
    common_params['sign'] = sign
    raise gen.Return(common_params)


class AliMd5EncryptionClass(object):
    """
    处理md5加密，校验
    """

    def __init__(self, merchant_key="", *args, **kargs):
        try:
            self.sign = kargs.pop("sign")
        except KeyError:
            pass
        self.dict_params = kargs
        self.sorted_params = self.sort_params()
        self.calculate_sign = hashlib.md5(self.sorted_params + "&key=" + merchant_key).hexdigest().upper()

    def sort_params(self):
        sorted_keys = sorted(self.dict_params)
        sorted_params = []
        for key in sorted_keys:
            if self.dict_params[key] != "":
                sorted_params.append("{}={}".format(key, self.dict_params[key]))
        return "&".join(sorted_params)

    def verify(self):
        return self.calculate_sign == self.sign

#
# print ALI_PUB_KEY
# biz_content = {
#     "external_id": "100000000975",
#     "name": "客都美食",
#     "alias_name": "客都美食",
#     "service_phone": "15220136618",
#     "category_id": "2015050700000061",
#     "source": ALI_PID,
#
# }
#
# common_params = {
#     "app_id": ALI_APPID,
#     "method": "alipay.boss.prod.submerchant.create",
#     "charset": "utf-8",
#     "sign_type": "RSA",
#     "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#     "version": "1.0",
#     "biz_content": json.dumps(biz_content)
# }
# rsa_sign = AliRSAEncryptionClass(common_params)
#
# sign = rsa_sign.sign()
# common_params['sign']= sign
# print common_params
# resp = requests.post("https://openapi.alipay.com/gateway.do", data=common_params)
# ret = json.loads(resp.content.decode('gbk'))
# print ret
# print ret.get('alipay_boss_prod_submerchant_create_response')
