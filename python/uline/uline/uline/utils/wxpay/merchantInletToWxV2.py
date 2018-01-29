# -*- coding: utf-8 -*-
'''
BEGIN
添加商户进件到微信
    必选参数:
        appid mch_id sign merchant_name merchant_shortname service_phone contact contact_phone
    可选参数:
        contact_email business merchant_remark
    成功:
    失败:
END
'''
from hashlib import md5
from functools import partial
from .util import dict_to_xml
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class MerchantInletToWx(object):
    def __init__(self, appid, mch_id, wxpay_key):
        self.appid = appid
        self.mch_id = mch_id
        self.wxpay_key = wxpay_key

    def __params_to_sign(self, params, wxpay_key):
        _temp = sorted(params.items())
        _temp.append(('key', wxpay_key))
        _temp = '&'.join(u'{}={}'.format(key, value) for key, value in _temp)
        sign = md5(_temp.encode('utf-8')).hexdigest().upper()
        return sign

    def _handle(self, appid, mch_id, wxpay_key, merchant_name=None, merchant_shortname=None, service_phone=None,
                contact=None, contact_phone=None, contact_email=None, business=None, merchant_remark=None, **kwargs):
        params = {
            "appid": appid,
            "mch_id": mch_id,
            "merchant_name": merchant_name,
            "merchant_shortname": merchant_shortname,
            "service_phone": service_phone,
            "contact": contact,
            "contact_phone": contact_phone,
            "contact_email": contact_email,
            "business": business,
            "merchant_remark": merchant_remark,
        }
        # 微信进件新接口需要渠道商渠道号
        if 'channel_id' in kwargs:
            params['channel_id'] = kwargs['channel_id']

        sign = self.__params_to_sign(params=params, wxpay_key=wxpay_key)
        params['sign'] = sign
        xml = dict_to_xml(params)
        return xml

    def handle(self):
        return partial(self._handle, appid=self.appid, mch_id=self.mch_id, wxpay_key=self.wxpay_key)


class UpdateMerchantInletToWx(MerchantInletToWx):
    def _handle(self, appid, mch_id, wxpay_key, merchant_shortname=None, service_phone=None,
                contact=None, sub_mch_id=None):
        params = {
            "appid": appid,
            "mch_id": mch_id,
            "merchant_shortname": merchant_shortname,
            "service_phone": service_phone,
            "contact": contact,
            "sub_mch_id": sub_mch_id
        }
        sign = self.__params_to_sign(params=params, wxpay_key=wxpay_key)
        params['sign'] = sign
        xml = dict_to_xml(params)
        return xml

    def __params_to_sign(self, params, wxpay_key):
        _temp = sorted(params.items())
        _temp.append(('key', wxpay_key))
        _temp = '&'.join(u'{}={}'.format(key, value) for key, value in _temp)
        sign = md5(_temp.encode('utf-8')).hexdigest().upper()
        return sign


class GetMetchantInfoFromWx(MerchantInletToWx):

    def _handle(self, appid, mch_id, wxpay_key, merchant_name=None, sub_mch_id=None):
        params = {
            'appid': appid,
            'mch_id': mch_id,
            'sub_mch_id': sub_mch_id,
            'merchant_name': merchant_name,
            'page_index': '1',
            'page_size': '50'

        }
        sign = wx_sign(params=params, wxpay_key=wxpay_key)
        params['sign'] = sign
        xml = dict_to_xml(params)
        return xml


def wx_sign(params, wxpay_key):
    _temp = sorted(params.items())
    _temp.append(('key', wxpay_key))
    _temp = '&'.join(u'{}={}'.format(key, value) for key, value in _temp)
    sign = md5(_temp.encode('utf-8')).hexdigest().upper()
    return sign

    #     mch_inlet = MerchantInletToWx('wxdace645e0bc2c424', '1900008951', '3AC991426F056322E053645AA8C0CC12')
    # if __name__ == '__main__':
    #     ret = mch_inlet.handle()(merchant_name=u'测试商户名1', merchant_shortname=u'测试', service_phone=u'15813321648',contact=u'测试',
    #                              contact_phone=u'15813321648', contact_email=u'kw10kk_xzg@163.com', business=u'123', merchant_remark=u'123')
    #     resp = requests.post("https://api.mch.weixin.qq.com/secapi/mch/submchmanage?action=add", data=ret, cert=(WX_PUB_KEY, WX_PRIVATE_KEY))
    #     result = xml_to_dict(resp.text)['root']
    #     print result
