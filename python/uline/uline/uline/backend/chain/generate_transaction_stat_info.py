# -*- coding: utf-8 -*-
from __future__ import division
from os import path, makedirs
import time
from openpyxl import Workbook
from collections import defaultdict

from uline.backend.__init__ import *
cur_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))


@app.task
def generate_xls(user_id, create_at_start, create_at_end):
    '''日期 支付笔数 支付成功金额 退款笔数 退款金额 交易总净额 手续费'''
    wb = Workbook()
    inlet_info_ws = wb.create_sheet(u'交易数据统计', 0)

    inlet_info_data = db_transaction_stats(
        user_id, create_at_start, create_at_end)

    gen_inlet_info(inlet_info_ws, inlet_info_data)
    file_path, static_path = general_filename(user_id)

    wb.save(file_path)
    return static_path


def db_transaction_stats(user_id, create_at_start, create_at_end):
    query = """select
            to_char(need_pay_time - INTERVAL '1 day', 'YYYY-MM-DD'),
            day_tx_count,
            day_tx_amount,
            day_refund_count,
            day_refund_amount,
            day_tx_net_amout,
            day_profit_amount
            from dt_daily_balance_info
            where dt_id=%(dt_id)s
            and need_pay_time between %(create_at_start)s::timestamp and %(create_at_end)s::timestamp;"""
    ret = db.selectSQL(query, {
        'dt_id': user_id,
        'create_at_start': create_at_start,
        'create_at_end': create_at_end
    }, fetchone=False)
    ret = [(d[0], int(d[1]), d[2] / 100, int(d[3]), abs(d[4]) / 100, d[5] / 100, d[6] / 100) for d in
           ret] if ret else []
    ret = deal_search_count_details(ret)
    return ret


def gen_inlet_info(ws, datas):
    fields = [u'日期', u'支付笔数',
              u'支付成功金额(元)', u'退款笔数', u'退款金额(元)', u'交易总净额(元)', u'手续费支出']

    ws.append(fields)

    for data in datas:
        ws.append(data)


def deal_search_count_details(search_count_details):
    date_range_default = defaultdict(list)

    for pay_start_time, day_tx_count, day_tx_amount, day_refund_count, day_refund_amount, day_tx_net_amout, day_profit_amount in search_count_details:
        if not date_range_default[pay_start_time]:
            date_range_default[pay_start_time].extend(
                [pay_start_time, day_tx_count, day_tx_amount, day_refund_count, day_refund_amount, day_tx_net_amout,
                 day_profit_amount])
        else:
            date_range_default[pay_start_time][1] += day_tx_count
            date_range_default[pay_start_time][2] += day_tx_amount
            date_range_default[pay_start_time][3] += day_refund_count
            date_range_default[pay_start_time][4] += day_refund_amount
            date_range_default[pay_start_time][5] += day_tx_net_amout
            date_range_default[pay_start_time][6] += day_profit_amount
    details = date_range_default.values()
    return sorted(details)


def general_filename(user_id):
    _ts = str(time.time())
    filename = "transaction_statistic_export_" + _ts + ".xlsx"
    user_dl_path = path.join(cur_dir, "static/downloads/", str(user_id))
    if not path.exists(user_dl_path):
        makedirs(user_dl_path)
    file_path = path.join(user_dl_path, filename)
    static_path = path.join("/static/downloads/", str(user_id), filename)
    return [file_path, static_path]
