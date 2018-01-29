#!/usr/bin/env python
#-*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/12/16'

# 微信支付接口


import types
from collections import defaultdict
from xml.etree import cElementTree as ET
from hashlib import md5

DELIVER_NOTIFY_URL = "https://api.weixin.qq.com/pay/delivernotify"


always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
               'abcdefghijklmnopqrstuvwxyz'
               '0123456789' '_.-')
_safemaps = {}


def my_quote(s, safe='/'):
    """quote('abc def') -> 'abc%20def'

    Each part of a URL, e.g. the path info, the query, etc., has a
    different set of reserved characters that must be quoted.

    RFC 2396 Uniform Resource Identifiers (URI): Generic Syntax lists
    the following reserved characters.

    reserved    = ";" | "/" | "?" | ":" | "@" | "&" | "=" | "+" |
                  "$" | ","

    Each of these characters is reserved in some component of a URL,
    but not necessarily in all of them.

    By default, the quote function is intended for quoting the path
    section of a URL.  Thus, it will not encode '/'.  This character
    is reserved, but in typical usage the quote function is being
    called on a path where the existing slash characters are used as
    reserved characters.
    """
    cachekey = (safe, always_safe)
    try:
        safe_map = _safemaps[cachekey]
    except KeyError:
        safe += always_safe
        safe_map = {}
        for i in range(256):
            c = chr(i)
            safe_map[c] = (c in safe) and c or ('%%%02x' % i)
        _safemaps[cachekey] = safe_map
    res = map(safe_map.__getitem__, s)
    return ''.join(res)


def my_quote_plus(s, safe=''):
    """Quote the query fragment of a URL; replacing ' ' with '+'"""
    if ' ' in s:
        s = my_quote(s, safe + ' ')
        return s.replace(' ', '+')
    return my_quote(s, safe)


def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
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
                return ' '.join([smart_str(arg, encoding, strings_only,
                                           errors) for arg in s])
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s


def dict_to_xml(dict_data):
    if isinstance(dict_data, dict):
        xml = '<xml>'
        for k, v in dict_data.items():
            if isinstance(v, (int, float)):
                xml = '%s<%s>%s</%s>' % (xml, k, v, k)
            else:
                xml = '%s<%s><![CDATA[%s]]></%s>' % (xml, k, v, k)
        xml = '%s%s' % (xml, '</xml>')
        return smart_str(xml)
    return None


def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
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


def xml_to_dict(xml_text):
    e = ET.XML(smart_str(xml_text))
    return etree_to_dict(e)


def params_to_sign(params, wxpay_key):
    _temp = sorted(params.items())
    _temp.append(('key', wxpay_key))
    _temp = '&'.join(u'{}={}'.format(key, value) for key, value in _temp)
    sign = md5(_temp.encode('utf-8')).hexdigest().upper()
    return sign


def compare_sign(key, params):
    # 微信支付验证签名
    from copy import deepcopy
    _params = deepcopy(params)
    if 'sign' not in _params:
        return False
    sign = _params.pop('sign')
    _temp = sorted(_params.items())
    _temp.append(('key', key))
    _temp = '&'.join(u'{}={}'.format(_key, _value) for _key, _value in _temp)
    ret = md5(_temp.encode('utf-8')).hexdigest().upper()
    return sign == ret


def deal_with_wx_result(wx_result, result_key=None, default_error_msg=''):
    """
    处理微信反馈结果
    :param wx_result: 微信反馈的信息
    :param result_key: 需要的值的key
    :param default_error_msg: 默认错误信息，在微信没有相关字段时有用
    :return: (result, msg)分别对应需要的值和结果消息
    """
    return_code = wx_result.get("return_code", 'FAIL')
    result_code = wx_result.get("result_code", 'FAIL')
    SUCCESS_TAG = "SUCCESS"
    if return_code != SUCCESS_TAG:
        return None, wx_result.get('return_msg', default_error_msg)
    if result_code != SUCCESS_TAG:
        return None, wx_result.get('result_msg', '') or wx_result.get('err_code_des', default_error_msg)
    if not result_key:
        result_key = 'result_code'
    result = wx_result.get(result_key, None)
    msg = wx_result.get('result_msg', "OK")
    return result, msg
