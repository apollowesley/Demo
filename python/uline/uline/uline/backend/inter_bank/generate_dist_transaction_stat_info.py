# -*- coding: utf-8 -*-
from __future__ import division
from os import path, makedirs
import time
from openpyxl import Workbook
from collections import defaultdict
from datetime import datetime, timedelta
from uline.backend.__init__ import *
from uline.public import log, common

cur_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))


@app.task
def generate_xls(dt_id, create_at_start, create_at_end, query_date):
    '''日期 支付笔数 支付成功金额 退款笔数 退款金额 交易总净额 手续费'''
    wb = Workbook()
    inlet_info_ws = wb.create_sheet(u'交易数据统计', 0)

    create_at_start_search, \
        create_at_end_search = common.downloads_query_date(query_date,
                                                           create_at_start,
                                                           create_at_end)

    inlet_info_data = db_transaction_stats(
        dt_id, create_at_start_search, create_at_end_search, query_date)
    if int(query_date) == 2:
        months = len(common.get_mon_seq(create_at_start, create_at_end))
        if len(inlet_info_data) > months:
            inlet_info_data.pop()
    gen_inlet_info(inlet_info_ws, inlet_info_data)
    file_path, static_path = general_filename(dt_id)

    wb.save(file_path)
    return static_path


def db_transaction_stats(dt_id, create_at_start, create_at_end, query_date):
    query = """select
                    {switch}
                    max(dt_user.dt_id),
                    max(dt_user.dt_name),
                    sum(di.day_tx_count),
                    round(sum(di.day_tx_amount), 2),
                    sum(di.day_refund_count),
                    abs(round(sum(di.day_refund_amount),2)),
                    round(sum(di.day_tx_net_amout),2),
                    round(sum(di.day_profit_amount),2)
                    from dt_daily_balance_info AS di
                    left join dt_user on di.dt_id = dt_user.dt_id
                    where (di.dt_id = %(dt_id)s or %(dt_id)s is null)
                    and (to_char({date_query}, 'YYYY-MM-DD')::TIMESTAMP between %(create_at_start)s::timestamp and %(create_at_end)s::timestamp)
                    GROUP BY  pay_time;
                    """
    switch = " to_char(di.need_pay_time - INTERVAL '1 day', 'YYYY-MM-DD') as pay_time," if int(
        query_date) == 1 else "to_char(di.need_pay_time - INTERVAL '1 day','YYYY-MM') as pay_time,"
    date_query = "di.need_pay_time" if int(
        query_date) == 1 else "di.need_pay_time - INTERVAL '1 day'"

    query = query.format(switch=switch, date_query=date_query)

    ret = db.selectSQL(query, {
        'dt_id': dt_id,
        'create_at_start': create_at_start,
        'create_at_end': create_at_end
    }, fetchone=False)
    ret = [(d[0], d[1], d[2], int(d[3]), d[4] / 100, int(d[5]), abs(d[6]) / 100, d[7] / 100, d[8] / 100) for d in
           ret] if ret else []
    ret = deal_search_count_details(ret)
    return ret


def gen_inlet_info(ws, datas):
    fields = [u'日期', u'渠道商id', u'渠道商名称', u'支付笔数',
              u'支付成功金额(元)', u'退款笔数', u'退款金额(元)', u'交易总净额(元)', u'渠道分润']

    ws.append(fields)

    for data in datas:
        ws.append(data)


def deal_search_count_details(search_count_details):
    date_range_default = defaultdict(list)

    for pay_start_time, dt_id, dt_name, day_tx_count, day_tx_amount, day_refund_count, day_refund_amount, day_tx_net_amout, day_profit_amount in search_count_details:
        if not date_range_default[pay_start_time]:
            date_range_default[pay_start_time].extend(
                [pay_start_time, dt_id, dt_name, day_tx_count, day_tx_amount, day_refund_count, day_refund_amount, day_tx_net_amout,
                 day_profit_amount])
        else:
            date_range_default[pay_start_time][3] += day_tx_count
            date_range_default[pay_start_time][4] += day_tx_amount
            date_range_default[pay_start_time][5] += day_refund_count
            date_range_default[pay_start_time][6] += day_refund_amount
            date_range_default[pay_start_time][7] += day_tx_net_amout
            date_range_default[pay_start_time][8] += day_profit_amount
    details = date_range_default.values()
    return sorted(details)


def general_filename(dt_id):
    _ts = str(time.time())
    filename = "transaction_statistic_export_" + _ts + ".xlsx"
    user_dl_path = path.join(cur_dir, "static/downloads/", str(dt_id))
    if not path.exists(user_dl_path):
        makedirs(user_dl_path)
    file_path = path.join(user_dl_path, filename)
    static_path = path.join("/static/downloads/", str(dt_id), filename)
    return file_path, static_path
