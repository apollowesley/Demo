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
import types
from collections import defaultdict
from xml.etree import cElementTree as ET
import requests
from hashlib import md5
from functools import partial
from uline.settings import WX_PUB_KEY, WX_PRIVATE_KEY
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class MerchantInletToWx(object):

    def __init__(self, appid, mch_id, wxpay_key):
        self.appid = appid
        self.mch_id = mch_id
        self.wxpay_key = wxpay_key
        self.session = requests.Session()

    def __smart_str(self, s, encoding='utf-8', strings_only=False, errors='strict'):
        """
        Returns a bytestring version of 's', encoded as specified in 'encoding'.

        If strings_only is True, don't convert (some) non-string-like objects.
        """
        if strings_only and isinstance(s, (types.NoneType, int)):
            return s
        if not isinstance(s, basestring):
            try:
                return str(s)
            except UnicodeEncodeError:
                if isinstance(s, Exception):
                    # An Exception subclass containing non-ASCII data that doesn't
                    # know how to print itself properly. We shouldn't raise a
                    # further exception.
                    return ' '.join([self.__smart_str(arg, encoding, strings_only,
                                                      errors) for arg in s])
                return unicode(s).encode(encoding, errors)
        elif isinstance(s, unicode):
            return s.encode(encoding, errors)
        elif s and encoding != 'utf-8':
            return s.decode('utf-8', errors).encode(encoding, errors)
        else:
            return s

    def __etree_to_dict(self, t):
        d = {t.tag: {} if t.attrib else None}
        children = list(t)
        if children:
            dd = defaultdict(list)
            for dc in map(self.__etree_to_dict, children):
                for k, v in dc.iteritems():
                    dd[k].append(v)
            d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.iteritems()}}
        if t.attrib:
            d[t.tag].update(('@' + k, v) for k, v in t.attrib.iteritems())
        if t.text:
            text = t.text.strip()
            if children or t.attrib:
                if text:
                    d[t.tag]['#text'] = text
            else:
                d[t.tag] = text
        return d

    def __dict_to_xml(self, dict_data):
        if isinstance(dict_data, dict):
            xml = '<xml>'
            for k, v in dict_data.items():
                if isinstance(v, (int, float)):
                    xml = '%s<%s>%s</%s>' % (xml, k, v, k)
                else:
                    xml = '%s<%s><![CDATA[%s]]></%s>' % (xml, k, v, k)
            xml = '%s%s' % (xml, '</xml>')
            return self.__smart_str(xml)
        return None

    def __xml_to_dict(self, xml_text):
        e = ET.XML(self.__smart_str(xml_text))
        return self.__etree_to_dict(e)

    def __params_to_sign(self, params, wxpay_key):
        _temp = sorted(params.items())
        _temp.append(('key', wxpay_key))
        _temp = '&'.join(u'{}={}'.format(key, value) for key, value in _temp)
        sign = md5(_temp.encode('utf-8')).hexdigest().upper()
        return sign

    def __wx_post(self, url, data):
        ret = ''
        try:
            ret = self.session.post(url=url, data=data, cert=(WX_PUB_KEY, WX_PRIVATE_KEY))
            ret.encoding = 'UTF-8'
        except Exception as err:
            print err
        return ret

    def _handle(self, appid, mch_id, wxpay_key, merchant_name=None, merchant_shortname=None, service_phone=None,
                contact=None, contact_phone=None, contact_email=None, business=None, merchant_remark=None):
        _url = "https://api.mch.weixin.qq.com/secapi/mch/submchmanage?action=add"
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
        sign = self.__params_to_sign(params=params, wxpay_key=wxpay_key)
        params['sign'] = sign

        xml = self.__dict_to_xml(params)
        ret = self.__wx_post(url=_url, data=xml)

        if not ret:
            return dict(result_code='FAIL')

        ret = self.__xml_to_dict(ret.text)['root']
        return ret

    def handle(self):
        return partial(self._handle, appid=self.appid, mch_id=self.mch_id, wxpay_key=self.wxpay_key)

# if __name__ == '__main__':
#     mch_inlet = MerchantInletToWxHandler('wxdace645e0bc2c424', '1900008951', '3AC991426F056322E053645AA8C0CC12')
#     ret = mch_inlet.handle()(merchant_name=u'测试商户名1', merchant_shortname=u'测试', service_phone=u'15813321648',contact=u'测试',
# contact_phone=u'15813321648', contact_email=u'kw10kk_xzg@163.com',
# business=u'123', merchant_remark=u'123')
