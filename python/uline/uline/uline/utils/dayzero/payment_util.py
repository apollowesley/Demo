# -*- coding: utf-8 -*-
'''
D0费率工具
    主要是一些方便操作D0 D1，乃至于后面的各种类型的。
'''


def get_dt_support_payment_type(cur, channel, dt_id):
    """
    检查渠道商是否开通某种支付类型
    :param channel: 可选参数 D1_wx，D0_wx，D1_alipay，D0_alipay
    :param dt_id: 渠道商ID
    :return: True 代表支持 False 代表不支持 None代表参数错误
    """
    channels = {
        'D1_wx': [1, 4], 'D1_alipay':[5, 10],
        'D0_wx': [100, 104], 'D0_alipay': [105, 200]
    }
    if channel not in (channels.keys()):
        return None

    sql = """
        select count(1) from dt_payment inner join
        d0_withdraw_fee on d0_withdraw_fee.role = dt_payment.dt_id
        where dt_payment.dt_id=%s
        and dt_payment.payment_type > %s and dt_payment.payment_type < %s
    """

    rate = channel.split('-')

    if rate[0] == 'D0':
        sql += " and d0_withdraw_fee.{fee_type} is not null ".format(fee_type=rate[1])
    count = cur.selectSQL(sql, (dt_id, channels.get(channel)[0], channels.get(channel)[1]))
    if len(count) == 1:
        if count[0] > 0:
            return True
        else:
            return False
    else:
        return False
