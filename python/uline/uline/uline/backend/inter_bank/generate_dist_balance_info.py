# -*- coding: utf-8 -*-
from __future__ import division
from os import path, makedirs
import time
from openpyxl import Workbook

from uline.backend.__init__ import *

cur_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
from uline.public.constants import TO_PAY, DOWNLOAD_INFO_NUM_LIMIT, PAY_CHANNEL
from uline.public import common, log
from datetime import timedelta, datetime


@app.task
def generate_xls(user_id, dt_name, dt_id, create_at_start, create_at_end, pay_status, total_num, channel, balance_account):
    '''结算日期 所属渠道商 结算户名 结算账号 金额 状态'''
    wb = Workbook()
    inlet_info_ws = wb.create_sheet(u'渠道商结算信息', 0)

    order_id = common.create_order_id()
    file_name, file_path, static_path = general_filename(user_id)
    if total_num > DOWNLOAD_INFO_NUM_LIMIT:
        gen_order_download_info(order_id, user_id, file_name)
    try:
        inlet_info_data = db_inlet_info(user_id,
                                        dt_name, dt_id, create_at_start, create_at_end, pay_status, channel, balance_account)

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
                          6, 1, 1, create_at, update_at))


def modify_order_download_info(order_id, status):
    update_at = common.timestamp_now()
    query = """update order_download_info set status=%s,update_at=%s where order_id=%s;"""
    db.executeSQL(query, (status, update_at, order_id))


def db_inlet_info(user_id, dt_name, dt_id, create_at_start, create_at_end, pay_status, channel, balance_account):
    query = """select
               to_char(ddbi.pay_start_time, 'YYYY-MM-DD HH24:MI:SS'),
               ddbi.need_pay_time,
               dii.dt_name,
               ddbi.rcvAcctName,
               ddbi.channel,
               ddbi.rcvacctno,
               ddbi.tranAmt,
               ddbi.pay_status,
               ddbi.dt_daily_balance_no,
               dii.dt_id,
               ddbi.rcvbankname
               from dt_daily_balance_info as ddbi
               inner join dt_inlet_info as dii on dii.dt_id = ddbi.dt_id
               inner join dt_balance db on db.dt_id = ddbi.dt_id
               where ddbi.tranamt > 0
               and(db.balance_account=%(balance_account)s or %(balance_account)s is null)
               and (ddbi.pay_status=%(pay_status)s or %(pay_status)s is null)
               and (ddbi.channel=%(channel)s or %(channel)s is null)
               and (dii.dt_name ~ %(dt_name)s or %(dt_name)s is null)
              and (dii.bk_id=%(bk_id)s)
               and (dii.dt_id::VARCHAR ~ %(dt_id)s::VARCHAR or %(dt_id)s::VARCHAR is null)
               and (ddbi.pay_start_time BETWEEN %(create_at_start)s::TIMESTAMP AND %(create_at_end)s::TIMESTAMP
               OR %(create_at_start)s IS NULL OR %(create_at_end)s IS NULL )
               ORDER BY ddbi.create_at desc;"""
    ret = db.selectSQL(query, {
        'pay_status': pay_status,
        'channel': channel,
        'dt_name': dt_name,
        'dt_id': dt_id,
        'create_at_start': create_at_start,
        'create_at_end': create_at_end,
        'balance_account': balance_account,
        'bk_id': user_id
    }, fetchone=False)

    if ret:
        ret = [list(i) for i in ret]
        for index in range(0, len(ret)):
            ret[index][1] -= timedelta(days=1)
            ret[index][1] = datetime.strftime(ret[index][1], '%Y-%m-%d')
            ret[index][6], ret[index][7], ret[index][4], ret[index][8], ret[index][9] = ret[index][6] / \
                100, TO_PAY[str(ret[index][7])], PAY_CHANNEL[ret[index][4]], str(
                    ret[index][8]), str(ret[index][9])
        return ret
    return ret,


def gen_inlet_info(ws, datas):
    fields = [u'结算日期', u'交易日期', u'所属渠道商', u'结算户名', u'支付渠道',
              u'结算账号', u'金额', u'状态', u'渠道商结算单号', u'渠道编号', u'结算银行']

    ws.append(fields)
    for data in datas:
        ws.append(data[:len(fields)])


def general_filename(user_id):
    _ts = str(time.time())
    filename = "distributor_balance_export_" + _ts + ".xlsx"
    user_dl_path = path.join(cur_dir, "static/downloads/", str(user_id))
    if not path.exists(user_dl_path):
        makedirs(user_dl_path)
    file_path = path.join(user_dl_path, filename)
    static_path = path.join("/static/downloads/", str(user_id), filename)
    return filename, file_path, static_path
