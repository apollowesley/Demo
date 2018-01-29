# -*- coding: utf-8 -*-
from __future__ import division
from os import path, makedirs
import time
from openpyxl import Workbook

from uline.backend.__init__ import *

cur_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
from uline.public.constants import WX_TRADE_STATE, WX_TRADE_TYPE, PAY_CHANNEL, DOWNLOAD_INFO_NUM_LIMIT
from uline.public import common, log
from datetime import timedelta


@app.task
def generate_xls(user_id, dt_name, dt_id, mch_name, mch_id, create_at_start, order_by, total_num):
    wb = Workbook()
    inlet_info_ws = wb.create_sheet(u'商户交易信息汇总', 0)

    order_id = common.create_order_id()
    file_name, file_path, static_path = general_filename(user_id)
    if total_num > DOWNLOAD_INFO_NUM_LIMIT:
        gen_order_download_info(order_id, user_id, file_name)

    try:

        mch_statistics_data = db_statistics_info(
            dt_name, dt_id, mch_name, mch_id, create_at_start, order_by)

        gen_inlet_info(inlet_info_ws, mch_statistics_data)
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
                          11, 1, 3, create_at, update_at))


def modify_order_download_info(order_id, status):
    update_at = common.timestamp_now()
    query = """update order_download_info set status=%s,update_at=%s where order_id=%s;"""
    db.executeSQL(query, (status, update_at, order_id))


def db_statistics_info(dt_name, dt_id, mch_name, mch_id, create_at_start, order_by):
    create_at_end = create_at_start + timedelta(days=1)
    _query = """SELECT mch_inlet_info.mch_name, mch_inlet_info.mch_id,
                    sum(mb.day_tx_count) as day_tx_count,
                    round(sum(mb.day_tx_amount)/100, 2) as day_tx_amount,
                    sum(mb.day_refund_count) as day_refund_count,
                    abs(round(sum(mb.day_refund_amount)/100, 2)) as day_refund_amount,
                    round(sum(mb.day_tx_net_amout)/100, 2) as day_tx_net_amout,
                    abs(round(sum(mb.day_profit_amount)/100, 2)) as day_profit_amount,
                 COUNT(*) OVER () AS total
                 FROM mch_daily_balance_info as mb
                 LEFT JOIN mch_inlet_info on mb.mch_id = mch_inlet_info.mch_id
                 INNER JOIN dt_user on dt_user.dt_id = mch_inlet_info.dt_id
                 WHERE (mb.pay_start_time between %(create_at_start)s::timestamp and %(create_at_end)s::timestamp)
                 AND (mch_inlet_info.mch_name ~ %(mch_name)s or %(mch_name)s is null)
                 AND (mch_inlet_info.mch_id::VARCHAR ~ %(mch_id)s::VARCHAR or %(mch_id)s::VARCHAR is null)
                 AND (dt_user.dt_id::VARCHAR ~ %(dt_id)s::VARCHAR or %(dt_id)s::VARCHAR is null)
                 AND (dt_user.dt_name::VARCHAR ~ %(dt_name)s::VARCHAR or %(dt_name)s::VARCHAR is null)
                 GROUP BY mch_inlet_info.mch_name, mch_inlet_info.mch_id
                 """

    order_by_query = ' ORDER BY %s DESC;' % (order_by)
    _query += order_by_query

    data = db.selectSQL(_query,
                        {"create_at_start": create_at_start,
                         "create_at_end": create_at_end,
                         "dt_name": dt_name, "dt_id": dt_id,
                         'mch_id': mch_id, "mch_name": mch_name},
                        fetchone=False)

    if data:
        data = deal_data(data)
    return data if data else []


def deal_data(data):
    new_data = []
    for index, sigle_row in enumerate(data):
        new_row = list(sigle_row)
        new_row.insert(0, index + 1)
        new_data.append(new_row)
    return new_data


def gen_inlet_info(ws, datas):
    fields = [u'排名', u'商户名称', u'商户编号', u'支付笔数',
              u'支付成功金额', u'退款笔数', u'退款金额', u'交易总净额', u'商户支出']
    # 渠道商汇总信息
    ws.append(fields)
    for data in datas:
        ws.append(list(data))


def general_filename(user_id):
    _ts = str(time.time())
    filename = "mch_statistics_export_" + _ts + ".xlsx"
    user_dl_path = path.join(cur_dir, "static/downloads/", str(user_id))
    if not path.exists(user_dl_path):
        makedirs(user_dl_path)
    file_path = path.join(user_dl_path, filename)
    static_path = path.join("/static/downloads/", str(user_id), filename)
    return filename, file_path, static_path
