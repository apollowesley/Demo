# -*- coding: utf-8 -*-
from __future__ import division
from os import path, makedirs
import time
from io import BytesIO as StringIO
import csv

from uline.backend.__init__ import *

cur_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
from uline.public.constants import WX_TRADE_STATE, WX_TRADE_TYPE, PAY_CHANNEL, DOWNLOAD_INFO_NUM_LIMIT
from uline.public import common, log


@app.task
def generate_xls(user_id, dt_name, mch_name, dt_id, mch_id, complete_at_start, complete_at_end,
                 out_trade_no, mch_trade_no, wx_transaction_id, trade_state,
                 trade_type, channel, total_num, cs_mch_shortname, cs_mch_id):
    '''创建时间 商户交易号 平台交易号 商户名称 所属渠道商 支付类型 交易金额 当前状态'''
    fields = [u'支付时间'.encode('GB18030'), u'所属渠道商'.encode('GB18030'),
              u'所属渠道商编号'.encode('GB18030'), u'商户编号'.encode('GB18030'),
              u'商户名称'.encode('GB18030'), u'商户简称'.encode('GB18030'),
              u'门店编号'.encode('GB18030'), u'门店名称'.encode('GB18030'),
              u'门店简称'.encode('GB18030'), u'商户交易号'.encode('GB18030'),
              u'ULINE交易号'.encode('GB18030'), u'第三方交易号'.encode('GB18030'),
              u'支付渠道'.encode('GB18030'), u'支付类型'.encode('GB18030'),
              u'交易金额'.encode('GB18030'), u'当前状态'.encode('GB18030'),
              u'备注'.encode('GB18030')]

    si = StringIO()
    cw = csv.writer(si, dialect='excel')
    cw.writerow(fields)

    order_id = common.create_order_id()
    file_name, file_path, static_path = general_filename(user_id)
    if total_num > DOWNLOAD_INFO_NUM_LIMIT:
        gen_order_download_info(order_id, user_id, file_name)

    try:

        inlet_info_data = db_inlet_info(dt_name, mch_name, dt_id, mch_id, complete_at_start, complete_at_end,
                                        out_trade_no, mch_trade_no, wx_transaction_id,
                                        trade_state, trade_type, channel, cs_mch_shortname, cs_mch_id)

        for single_row in inlet_info_data:
            temp = []
            # 暂时没有找到解决数字长度过长，被excel转译的问题。先在头部添加\t 禁止其转译
            for i in single_row:
                i = str(i) if i is not None else ''
                if len(i) >= 11:
                    i = '\t %s' % str(i)
                temp.append(i.encode('GB18030'))
            cw.writerow(temp)
            # cw.writerow([str(i).encode('GB18030') for i in single_row])

        with open(file_path, 'w') as f:
            f.write(si.getvalue())
            f.flush()

        if total_num > DOWNLOAD_INFO_NUM_LIMIT:
            modify_order_download_info(order_id, 2)
    except Exception as err:
        if total_num > DOWNLOAD_INFO_NUM_LIMIT:
            modify_order_download_info(order_id, 3)
        log.exception.info(err)
        return {'static_path': False}
    return {'static_path': static_path}


def gen_order_download_info(order_id, user_id, file_name):
    create_at = update_at = common.timestamp_now()
    query = """insert into order_download_info (order_id, user_id, file, type, status, platform, create_at, update_at)
            values (%s,%s,%s,%s,%s,%s,%s,%s)"""
    db.executeSQL(query, (order_id, user_id, file_name,
                          7, 1, 1, create_at, update_at))


def modify_order_download_info(order_id, status):
    update_at = common.timestamp_now()
    query = """update order_download_info set status=%s,update_at=%s where order_id=%s;"""
    db.executeSQL(query, (status, update_at, order_id))


def db_inlet_info(dt_name, mch_name, dt_id, mch_id, complete_at_start, complete_at_end,
                  out_trade_no, mch_trade_no, wx_transaction_id,
                  trade_state, trade_type, channel, cs_mch_shortname, cs_mch_id):
    data = []
    ul_query = """select
               dt_user.dt_name,
               dt_user.dt_id,
               dt_inlet_info.dt_id,
               dt_inlet_info.dt_name,
               dt_inlet_info.dt_short_name,
               mch_inlet_info.mch_id,
               mch_inlet_info.mch_name,
               mch_inlet_info.mch_shortname,
               mch_inlet_info.cs_id
               from mch_inlet_info
               inner join dt_user on dt_user.dt_id = mch_inlet_info.dt_id
               left join dt_inlet_info on dt_inlet_info.dt_id = mch_inlet_info.cs_id
               where (dt_user.dt_name ~ %(dt_name)s or %(dt_name)s is null)
                and (mch_inlet_info.mch_id::VARCHAR ~ E%(mch_id)s::VARCHAR or %(mch_id)s::VARCHAR is null)
               and (mch_inlet_info.mch_shortname ~ E%(cs_mch_shortname)s or %(cs_mch_shortname)s is null)
               and (mch_inlet_info.mch_name ~ E%(mch_name)s or %(mch_name)s is null)
               {find_type}
               and (dt_user.dt_id::VARCHAR ~ %(dt_id)s::VARCHAR or %(dt_id)s::VARCHAR is null);
               """
    query_dict = {
        "dt_name": dt_name,
        "dt_id": dt_id,
        'mch_name': db.escape(mch_name),
        'cs_mch_shortname': db.escape(cs_mch_shortname),
        'mch_id': db.escape(mch_id)
    }

    query_dict.update({'cs_mch_shortname': db.escape(cs_mch_shortname),
                       'mch_id': db.escape(cs_mch_id)}) if cs_mch_shortname or cs_mch_id else \
        query_dict.update({'mch_id': db.escape(mch_id)})

    if cs_mch_shortname or cs_mch_id:
        find_type = "and mch_inlet_info.cs_id is not null"
    else:
        find_type = "and mch_inlet_info.cs_id is null" if mch_name or mch_id else ""
    ul_ret = db.selectSQL(ul_query.format(
        find_type=find_type), query_dict, fetchone=False)

    ul_rets = {str(i[5]): list(i) for i in ul_ret}

    ul_mch_id = ul_rets.keys() if ul_ret else []
    if ul_mch_id:
        ul_mch_id = tuple(ul_mch_id)

        # 需要用到in查询
        if mch_name or dt_name or mch_id or dt_id or cs_mch_shortname or cs_mch_id:
            tb_query = """select
                    ul_mch_id,
                    to_char(complete_at, 'YYYY-MM-DD HH24:MI:SS'),
                    mch_trade_no,
                    out_trade_no,
                    wx_transaction_id,
                    channel,
                    trade_type,
                    total_fee,
                    trade_state,
                    detail
                    from orders
                    where ul_mch_id in %(ul_mch_id)s
                    and (complete_at is not null)
                    and (trade_state in %(trade_state)s or %(trade_state)s is null)
                    and (trade_type=%(trade_type)s or %(trade_type)s is null)
                    and (channel=%(channel)s or %(channel)s is null)
                    and (out_trade_no ~ %(out_trade_no)s or %(out_trade_no)s is null)
                    and (mch_trade_no ~ %(mch_trade_no)s or %(mch_trade_no)s is null)
                    and (wx_transaction_id ~ %(wx_transaction_id)s or %(wx_transaction_id)s is null)
                    and (complete_at between %(complete_at_start)s::timestamp and %(complete_at_end)s::timestamp
                    or %(complete_at_start)s is null or %(complete_at_end)s is null)
                    order by complete_at desc;"""
        else:
            tb_query = """select
                     ul_mch_id,
                    to_char(complete_at, 'YYYY-MM-DD HH24:MI:SS'),
                    mch_trade_no,
                    out_trade_no,
                    wx_transaction_id,
                    channel,
                    trade_type,
                    total_fee,
                    trade_state,
                    detail
                    from orders
                    where (complete_at is not null)
                    and (trade_state in %(trade_state)s or %(trade_state)s is null)
                    and (trade_type=%(trade_type)s or %(trade_type)s is null)
                    and (channel=%(channel)s or %(channel)s is null)
                    and (out_trade_no ~ %(out_trade_no)s or %(out_trade_no)s is null)
                    and (mch_trade_no ~ %(mch_trade_no)s or %(mch_trade_no)s is null)
                    and (wx_transaction_id ~ %(wx_transaction_id)s or %(wx_transaction_id)s is null)
                    and (complete_at between %(complete_at_start)s::timestamp and %(complete_at_end)s::timestamp
                    or %(complete_at_start)s is null or %(complete_at_end)s is null)
                    order by complete_at desc;"""

        tb_ret = tdb.selectSQL(tb_query, {
            'ul_mch_id': ul_mch_id,
            'trade_type': trade_type,
            'trade_state': trade_state,
            'channel': channel,
            'out_trade_no': out_trade_no,
            'mch_trade_no': mch_trade_no,
            'wx_transaction_id': wx_transaction_id,
            'complete_at_start': complete_at_start,
            'complete_at_end': complete_at_end
        }, fetchone=False)

        if tb_ret:
            data = gen_tb_ret(tb_ret, ul_rets)
    return data


def gen_tb_ret(tb_ret, ul_ret):
    data = []
    for tb_data in tb_ret:
        tb_data = list(tb_data)
        if ul_ret.get(tb_data[0]):
            temp = tb_data[0:2] + ul_ret[tb_data[0]] + tb_data[2:]
            # tb_data.extend(ul_ret[tb_data[0]])
            data.append(enhance_deal_data(temp))
    return data


def enhance_deal_data(_d):

    if _d[-2]:
        _d[-2] = WX_TRADE_STATE[str(_d[-2])]
    if _d[-4]:
        _d[-4] = u'JS支付' if _d[-5] == 'alipay' and str(
            _d[-4]) == 'JSAPI' else WX_TRADE_TYPE[str(_d[-4])]
    if _d[-3]:
        _d[-3] = _d[-3] / 100
    if _d[-5]:
        _d[-5] = PAY_CHANNEL[_d[-5]]
    if not _d[10]:
        _d[4], _d[5], _d[6] = _d[7], _d[8], _d[9]
        _d[7], _d[8], _d[9] = ["-"] * 3
    del _d[10]
    del _d[0]
    return _d


def deal_data(data):
    for _d in data:
        if _d[4]:
            _d[4] = WX_TRADE_STATE[str(_d[4])]
        if _d[5]:
            _d[5] = u'JS支付' if _d[7] == 'alipay' and str(
                _d[5]) == 'JSAPI' else WX_TRADE_TYPE[str(_d[5])]
        if _d[6]:
            _d[6] = _d[6] / 100
        if _d[7]:
            _d[7] = PAY_CHANNEL[_d[7]]
    return data


def gen_inlet_info(cw):
    fields = [u'支付时间', u'所属渠道商', u'所属渠道商编号', u'商户编号', u'商户名称', u'商户简称', u'门店编号', u'门店名称', u'门店简称', u'商户交易号', u'uline交易号',
              u'第三方交易号', u'支付渠道', u'支付类型', u'交易金额', u'当前状态', u'备注']
    cw.writerow(fields)
    # 商户交易信息
    # ws.append(fields)
    # for data in datas:
    #     ws.append(list(data))


def general_filename(user_id):
    _ts = str(time.time())
    filename = "mch_inlet_trade_export_" + _ts + ".csv"
    user_dl_path = path.join(cur_dir, "static/downloads/", str(user_id))
    if not path.exists(user_dl_path):
        makedirs(user_dl_path)
    file_path = path.join(user_dl_path, filename)
    static_path = path.join("/static/downloads/", str(user_id), filename)
    return filename, file_path, static_path
