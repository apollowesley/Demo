# -*- coding:utf-8 -*-
import datetime
from random import choice, randint
from hashlib import md5


class initiateRefundToThirdpartHandle(object):

    def __init__(self, mch_id, out_trade_no, out_refund_no,
                 total_fee, refund_fee, op_user_id,
                 refund_fee_type='CNY'):
        """
        :param mch_id: 商户号
        :param out_trade_no: 商户系统内部的订单号
        :param out_refund_no: 订单金额
        :param total_fee: 商户退款单号(32位内随机字符串)
        :param refund_fee: 退款总金额,单位为分,可以做部分退款
        :param op_user_id: 操作员帐号,默认为商户号
        """
        self.params = {
            'mch_id': mch_id,
            'nonce_str': gen_random_str(),
            'out_trade_no': out_trade_no,
            'out_refund_no': out_refund_no,
            'total_fee': total_fee,
            'refund_fee': refund_fee,
            'op_user_id': op_user_id,
            'refund_fee_type': refund_fee_type,
        }
        self._values = {}

    def key_value_url(self, value):
        """将将键值对转为 key1=value1&key2=value2
        """
        key_az = sorted(value.keys())
        pair_array = []
        for k in key_az:
            try:
                v = value.get(k, '').strip()
            except AttributeError:
                v = str(value.get(k, ''))
            v = v.encode('utf8')
            k = k.encode('utf8')
            pair_array.append('%s=%s' % (k, v))

        tmp = '&'.join(pair_array)
        return tmp

    def get_sign(self, params, mch_pay_key):
        """生成sign
        """
        stringA = self.key_value_url(params)
        stringSignTemp = stringA + '&key=' + mch_pay_key
        sign = (md5(stringSignTemp.encode('utf-8')).hexdigest()).upper()
        params['sign'] = sign
        return params

    def get_req_xml(self, mch_pay_key):
        """拼接XML
        """
        self.get_sign(self.params, mch_pay_key)
        xml = "<xml>"
        for k, v in self.params.items():
            try:
                k, v = k.encode('utf8'), v.encode('utf8')
            except AttributeError:
                k, v = str(k), str(v)
            xml += '<' + k + '>' + v + '</' + k + '>'
        xml += "</xml>"
        return xml


def generate_mch_refund_no(mch_id):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return '%s%s%s' % (mch_id, timestamp, randint(1000, 100000))


def gen_random_str(min_length=30, max_length=30,
                   allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'):
    if min_length == max_length:
        length = min_length
    else:
        length = choice(range(min_length, max_length))

    return ''.join([choice(allowed_chars) for i in range(length)])
