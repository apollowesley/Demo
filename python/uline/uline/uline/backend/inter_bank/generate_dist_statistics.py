# -*- coding: utf-8 -*-
from __future__ import division
from os import path, makedirs
import time
from openpyxl import Workbook
from datetime import timedelta

from uline.backend.__init__ import *

cur_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
from uline.public.constants import WX_TRADE_STATE, WX_TRADE_TYPE, PAY_CHANNEL, DOWNLOAD_INFO_NUM_LIMIT
from uline.public import common, log


@app.task
def generate_xls(user_id, dt_name, dt_id, create_at_start, create_at_end, order_by, total_num):
    wb = Workbook()
    inlet_info_ws = wb.create_sheet(u'渠道商交易信息汇总', 0)

    order_id = common.create_order_id()
    file_name, file_path, static_path = general_filename(user_id)
    if total_num > DOWNLOAD_INFO_NUM_LIMIT:
        gen_order_download_info(order_id, user_id, file_name)

    try:

        dist_statistics_data = db_statistics_info(user_id, dt_name, dt_id, create_at_start, create_at_end, order_by)

        gen_inlet_info(inlet_info_ws, dist_statistics_data)
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
    db.executeSQL(query, (order_id, user_id, file_name, 10, 1, 1, create_at, update_at))


def modify_order_download_info(order_id, status):
    update_at = common.timestamp_now()
    query = """update order_download_info set status=%s,update_at=%s where order_id=%s;"""
    db.executeSQL(query, (status, update_at, order_id))


def db_statistics_info(user_id, dt_name, dt_id, create_at_start, create_at_end, order_by):
    _query = """SELECT dt_user.dt_name, dt_user.dt_id,
                    sum(dtb.day_tx_count) as day_tx_count,
                    round(sum(dtb.day_tx_amount)/100, 2) as day_tx_amount,
                    sum(dtb.day_refund_count) as day_refund_count,
                    abs(round(sum(dtb.day_refund_amount)/100, 2)) as day_refund_amount,
                    round(sum(dtb.day_tx_net_amout)/100, 2) as day_tx_net_amout,
                    abs(round(sum(dtb.day_profit_amount)/100, 2)) as day_profit_amount
                 FROM dt_daily_balance_info as dtb
                 LEFT JOIN dt_user on dtb.dt_id = dt_user.dt_id
                 LEFT JOIN dt_inlet_info on dt_inlet_info.dt_id=dt_user.dt_id
                 WHERE (dtb.need_pay_time between %(create_at_start)s::timestamp and %(create_at_end)s::timestamp)
                 AND (dt_user.dt_name ~ E%(dt_name)s or %(dt_name)s = '')
                 AND (dt_inlet_info.bk_id=%(bk_id)s)
                 AND (dt_user.dt_id::VARCHAR ~ E%(dt_id)s or %(dt_id)s = '')
                 GROUP BY dt_user.dt_name, dt_user.dt_id
                 """

    order_by_query = ' ORDER BY %s DESC' % (order_by)
    _query += order_by_query

    data = db.selectSQL(_query,
                        {"create_at_start": create_at_start,
                         "create_at_end": create_at_end,
                         "dt_name": db.escape(dt_name),
                         "bk_id": user_id,
                         "dt_id": db.escape(dt_id)},
                        fetchone=False)

    if data:
        data = deal_data(data)
    return data if data else []


def gen_tb_ret(tb_ret, ul_ret):
    data = []
    ret = [list(i) for i in tb_ret]
    for tb_data in ret:
        for ul_data in ul_ret:
            if int(tb_data[0]) == ul_data[0]:
                tb_data.extend([ul_data[1], ul_data[2]])
                data.append(tb_data)
    return data


def deal_data(data):
    new_data = []
    for index, sigle_row in enumerate(data):
        new_row = list(sigle_row)
        new_row.insert(0, index + 1)
        new_data.append(new_row)
    return new_data


def gen_inlet_info(ws, datas):
    fields = [u'排名', u'渠道商名称', u'渠道商编号', u'支付笔数',
              u'支付成功金额', u'退款笔数', u'退款金额', u'交易总净额', u'渠道商分润']
    # 渠道商汇总信息
    ws.append(fields)
    for data in datas:
        ws.append(list(data))


def general_filename(user_id):
    _ts = str(time.time())
    filename = "dist_statistics_export_" + _ts + ".xlsx"
    user_dl_path = path.join(cur_dir, "static/downloads/", str(user_id))
    if not path.exists(user_dl_path):
        makedirs(user_dl_path)
    file_path = path.join(user_dl_path, filename)
    static_path = path.join("/static/downloads/", str(user_id), filename)
    return filename, file_path, static_path
