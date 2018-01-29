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
def generate_xls(user_id, create_at_start, create_at_end, out_trade_no, mch_trade_no, transaction_id, refund_status,
                 mch_refund_no, out_refund_no, refund_id,
                 channel, total_num):
    '''创建时间 商户交易号 平台交易号 商户退款单号 平台退款单号	 商户名称	 所属渠道商 退款金额 当前状态'''
    wb = Workbook()
    inlet_info_ws = wb.create_sheet(u'渠道基本信息', 0)
    order_id = common.create_order_id()
    file_name, file_path, static_path = general_filename(user_id)
    if total_num > DOWNLOAD_INFO_NUM_LIMIT:
        gen_order_download_info(order_id, user_id, file_name)

    try:
        inlet_info_data = db_inlet_info(user_id, create_at_start, create_at_end, out_trade_no, mch_trade_no,
                                        transaction_id, refund_status,
                                        mch_refund_no, out_refund_no, refund_id,
                                        channel)

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
                          8, 1, 4, create_at, update_at))


def modify_order_download_info(order_id, status):
    update_at = common.timestamp_now()
    query = """update order_download_info set status=%s,update_at=%s where order_id=%s;"""
    db.executeSQL(query, (status, update_at, order_id))


def db_inlet_info(user_id, create_at_start, create_at_end, out_trade_no, mch_trade_no, transaction_id, refund_status,
                  mch_refund_no, out_refund_no, refund_id,
                  channel):
    data = []
    ul_query = """select
               mch_user.mch_name,
               dt_user.dt_name,
               mch_inlet_info.mch_shortname
               from mch_user
               inner join mch_inlet_info on mch_inlet_info.mch_id = mch_user.mch_id
               inner join dt_user on dt_user.dt_id = mch_inlet_info.dt_id
               where mch_inlet_info.mch_id=%(mch_id)s
               """
    ul_ret = db.selectSQL(ul_query, {"mch_id": user_id})

    ul_ret = list(ul_ret)

    tb_query = """select
                ul_mch_id,
                to_char(created_at, 'YYYY-MM-DD HH24:MI:SS'),
                mch_trade_no,
                out_trade_no,
                refund_id,
                out_refund_no,
                refund_fee,
                refund_status,
                channel
                from order_refunds
                where ul_mch_id=%(ul_mch_id)s
                and (refund_status=%(refund_status)s or %(refund_status)s is null)
                and (mch_refund_no ~ %(mch_refund_no)s or %(mch_refund_no)s is null)
                and (out_refund_no ~ %(out_refund_no)s or %(out_refund_no)s is null)
                and (refund_id ~ %(refund_id)s or %(refund_id)s is null)
                and (channel ~ %(channel)s or %(channel)s is null)
                and (out_trade_no ~ %(out_trade_no)s or %(out_trade_no)s is null)
                and (mch_trade_no ~ %(mch_trade_no)s or %(mch_trade_no)s is null)
                and (transaction_id ~ %(transaction_id)s or %(transaction_id)s is null)
                and (created_at between %(create_at_start)s::timestamp and %(create_at_end)s::timestamp
                or %(create_at_start)s is null or %(create_at_end)s is null)
                order by created_at desc;"""

    tb_ret = tdb.selectSQL(tb_query, {
        'ul_mch_id': str(user_id),
        'refund_status': refund_status,
        'mch_refund_no': mch_refund_no,
        'out_refund_no': out_refund_no,
        'refund_id': refund_id,
        'channel': channel,
        'out_trade_no': out_trade_no,
        'mch_trade_no': mch_trade_no,
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
    for _d in ret:
        _d.extend(ul_ret)
        data.append(_d)
    return data


def deal_data(data):
    for _d in data:
        _d[6], _d[7], _d[8] = _d[6] / \
            100, WX_REFUND_STATE[_d[7]], PAY_CHANNEL[_d[8]]
    return data


def gen_inlet_info(ws, datas):
    fields = [u'商户编号', u'创建时间', u'商户交易号', u'平台交易号', u'商户退款单号',
              u'平台退款单号', u'退款金额', u'当前状态', u'支付渠道', u'商户名称', u'所属渠道商', u'商户简称']
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