# -*- coding: utf-8 -*-
from __future__ import division
from os import path, makedirs
import time
from openpyxl import Workbook

from uline.backend.__init__ import *

cur_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
from uline.public.constants import WX_REFUND_STATE, PAY_CHANNEL, DOWNLOAD_INFO_NUM_LIMIT
from uline.public import common, log


@app.task
def generate_xls(user_id, mch_name, mch_id, create_at_start, create_at_end, mch_trade_no, out_trade_no,
                 transaction_id, refund_status,
                 mch_refund_no, out_refund_no, refund_id,
                 channel, total_num, dt_sub_id, cs_mch_shortname, cs_mch_id):
    '''创建时间 商户交易号 平台交易号 商户退款单号 平台退款单号	 商户名称	 所属渠道商 退款金额 当前状态'''
    wb = Workbook()
    inlet_info_ws = wb.create_sheet(u'渠道基本信息', 0)

    order_id = common.create_order_id()
    file_name, file_path, static_path = general_filename(user_id)
    if total_num > DOWNLOAD_INFO_NUM_LIMIT:
        gen_order_download_info(order_id, user_id, file_name)
    try:
        inlet_info_data = db_inlet_info(user_id, mch_name, mch_id, create_at_start, create_at_end, mch_trade_no,
                                        out_trade_no, transaction_id, refund_status,
                                        mch_refund_no, out_refund_no, refund_id,
                                        channel, dt_sub_id, cs_mch_shortname, cs_mch_id)

        gen_inlet_info(inlet_info_ws, inlet_info_data)
        wb.save(file_path)

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
                          8, 1, 3, create_at, update_at))


def modify_order_download_info(order_id, status):
    update_at = common.timestamp_now()
    query = """update order_download_info set status=%s,update_at=%s where order_id=%s;"""
    db.executeSQL(query, (status, update_at, order_id))


def db_inlet_info(user_id, mch_name, mch_id, create_at_start, create_at_end, mch_trade_no, out_trade_no,
                  transaction_id, refund_status,
                  mch_refund_no, out_refund_no, refund_id, channel, dt_sub_id, cs_mch_shortname, cs_mch_id):
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
               mch_inlet_info.dt_sub_id,
               dt_subuser.dt_sub_name,
                 mch_inlet_info.cs_id
               from mch_inlet_info
               inner join dt_user on dt_user.dt_id = mch_inlet_info.dt_id
               left join dt_subuser on mch_inlet_info.dt_sub_id = dt_subuser.dt_sub_id
                left join dt_inlet_info on dt_inlet_info.dt_id = mch_inlet_info.cs_id
               where dt_user.dt_id=%(dt_id)s
               and (mch_inlet_info.mch_id::VARCHAR ~ E%(mch_id)s::VARCHAR or %(mch_id)s::VARCHAR is null)
               and (mch_inlet_info.mch_shortname ~ E%(cs_mch_shortname)s or %(cs_mch_shortname)s is null)
               and (mch_inlet_info.mch_name ~ E%(mch_name)s or %(mch_name)s is null)
                {find_type}
               and (mch_inlet_info.dt_sub_id = %(dt_sub_id)s OR %(dt_sub_id)s is NULL );
               """

    query_dict = {"dt_id": user_id,
                  "dt_sub_id": dt_sub_id,
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

    ul_mch_id = [str(i[5]) for i in ul_ret] if ul_ret else []
    if ul_mch_id:
        ul_mch_id = tuple(ul_mch_id)

        tb_query = """select
                    order_refunds.ul_mch_id,
                    to_char(order_refunds.created_at, 'YYYY-MM-DD HH24:MI:SS'),
                    order_refunds.mch_trade_no,
                    order_refunds.mch_refund_no,
                    order_refunds.out_trade_no,
                    order_refunds.out_refund_no,
                    order_refunds.transaction_id,
                    order_refunds.refund_id,
                    order_refunds.channel,
                    orders.trade_type,
                    order_refunds.total_fee,
                    order_refunds.refund_fee,
                    order_refunds.checked_flag,
                    to_char(order_refunds.created_at, 'YYYY-MM-DD HH24:MI:SS'),
                    order_refunds.refund_status
                    from order_refunds
                    inner join orders on order_refunds.out_trade_no = orders.out_trade_no
                    where order_refunds.ul_mch_id in %(ul_mch_id)s
                    and (order_refunds.refund_status=%(refund_status)s or %(refund_status)s is null)
                    and (order_refunds.mch_refund_no ~ %(mch_refund_no)s or %(mch_refund_no)s is null)
                    and (order_refunds.out_refund_no ~ %(out_refund_no)s or %(out_refund_no)s is null)
                    and (order_refunds.refund_id ~ %(refund_id)s or %(refund_id)s is null)
                    and (order_refunds.channel ~ %(channel)s or %(channel)s is null)
                    and (order_refunds.mch_trade_no ~ %(mch_trade_no)s or %(mch_trade_no)s is null)
                    and (order_refunds.out_trade_no ~ %(out_trade_no)s or %(out_trade_no)s is null)
                    and (order_refunds.transaction_id ~ %(transaction_id)s or %(transaction_id)s is null)
                    and (order_refunds.created_at between %(create_at_start)s::timestamp and %(create_at_end)s::timestamp
                    or %(create_at_start)s is null or %(create_at_end)s is null)
                    order by order_refunds.created_at desc;"""

        tb_ret = tdb.selectSQL(tb_query, {
            'ul_mch_id': ul_mch_id,
            'refund_status': refund_status,
            'channel': channel,
            'mch_refund_no': mch_refund_no,
            'out_refund_no': out_refund_no,
            'refund_id': refund_id,
            'mch_trade_no': mch_trade_no,
            'out_trade_no': out_trade_no,
            'transaction_id': transaction_id,
            'create_at_start': create_at_start,
            'create_at_end': create_at_end
        }, fetchone=False)

        if tb_ret:
            data = gen_tb_ret(tb_ret, ul_ret)
            data = deal_data(data)
    return data


def gen_tb_ret(tb_ret, ul_ret):
    data = []
    ret = [list(i) for i in tb_ret]
    for tb_data in ret:
        for ul_data in ul_ret:
            if int(tb_data[0]) == ul_data[5]:
                temp = tb_data[0:2] + [ul_data[0], ul_data[1], ul_data[2], ul_data[3], ul_data[4], ul_data[5],
                                       ul_data[6], ul_data[7], ul_data[8], ul_data[9], ul_data[10]] + tb_data[2:]
                data.append(temp)
    return data


def deal_data(data):
    for _d in data:
        _d[-4] = _d[-4] / 100
        _d[-5] = _d[-5] / 100
        _d[-1] = WX_REFUND_STATE[_d[-1]]
        _d[-7] = PAY_CHANNEL[_d[-7]]
        _d[3], _d[4], _d[7] = str(_d[3]), str(_d[4]), str(_d[7])
        if not _d[12]:
            _d[4], _d[5], _d[6] = _d[7], _d[8], _d[9]
            _d[7], _d[8], _d[9] = ['-'] * 3
        del _d[12]
        del _d[0]
    return data


def gen_inlet_info(ws, datas):
    fields = [u'创建时间',
              u'所属渠道商', u'所属渠道商编号', u'商户编号', u'商户名称', u'商户简称', u'门店编号', u'门店名称', u'门店简称', u'业务员名称', u'业务员编号',
              u'商户交易号', u'商户退款单号', u'ULINE交易号', u'ULINE退款单号', u'第三方交易号', u'第三方退款单号',
              u'支付渠道', u'支付类型', u'交易金额', u'退款金额', u'对账状态', u'变更时间', u'退款状态']
    # 渠道基本信息表
    ws.append(fields)

    for data in datas:
        ws.append(list(data))


def general_filename(user_id):
    _ts = str(time.time())
    filename = "mch_inlet_refund_export_" + _ts + ".xlsx"
    user_dl_path = path.join(cur_dir, "static/downloads/", str(user_id))
    if not path.exists(user_dl_path):
        makedirs(user_dl_path)
    file_path = path.join(user_dl_path, filename)
    static_path = path.join("/static/downloads/", str(user_id), filename)
    return filename, file_path, static_path
