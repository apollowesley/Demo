# -*- coding: utf-8 -*-
from __future__ import division

import re
from os import path, makedirs
import time
from openpyxl import Workbook

from uline.backend.__init__ import *
cur_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
from uline.public.constants import TO_PAY, DOWNLOAD_INFO_NUM_LIMIT, PAY_CHANNEL
from uline.public import common, log
from datetime import timedelta, datetime


@app.task
def generate_xls(user_id, create_at_start, create_at_end, pay_status, total_num, channel):
    '''结算日期 商户名称 所属渠道商 结算户名 结算账号 金额 状态'''
    wb = Workbook()
    inlet_info_ws = wb.create_sheet(u'商户结算信息', 0)

    order_id = common.create_order_id()
    file_name, file_path, static_path = general_filename(user_id)
    if total_num > DOWNLOAD_INFO_NUM_LIMIT:
        gen_order_download_info(order_id, user_id, file_name)

    try:
        inlet_info_data = db_inlet_info(
            user_id, create_at_start, create_at_end, pay_status, channel)

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
                          5, 1, 4, create_at, update_at))


def modify_order_download_info(order_id, status):
    update_at = common.timestamp_now()
    query = """update order_download_info set status=%s,update_at=%s where order_id=%s;"""
    db.executeSQL(query, (status, update_at, order_id))


def db_inlet_info(user_id, create_at_start, create_at_end, pay_status, channel):
    query = """select
           to_char(mdbi.pay_start_time, 'YYYY-MM-DD HH24:MI:SS'),
           mdbi.need_pay_time,
           mii.mch_name,
           du.dt_name,
           mdbi.rcvAcctName,
           mdbi.channel,
           mdbi.rcvacctno,
           mdbi.tranAmt,
           mdbi.pay_status,
           mdbi.mch_daily_balance_no,
           mii.mch_id,
           mii.mch_shortname,
           mdbi.rcvbankname
           from mch_daily_balance_info as mdbi
           inner join mch_inlet_info as mii on mii.mch_id = mdbi.mch_id
           inner join mch_balance as mb on mb.mch_id = mdbi.mch_id
           inner join dt_user as du on du.dt_id = mii.dt_id
           where mdbi.tranamt > 0
           and mii.mch_id=%(mch_id)s
           and (mdbi.pay_status=%(pay_status)s or %(pay_status)s is null)
           and (mdbi.channel=%(channel)s or %(channel)s is null)
           and (mdbi.create_at BETWEEN %(create_at_start)s::TIMESTAMP AND %(create_at_end)s::TIMESTAMP
           OR %(create_at_start)s IS NULL OR %(create_at_end)s IS NULL )
           ORDER BY mdbi.create_at desc;"""

    ret = db.selectSQL(query, {
        'pay_status': pay_status,
        'channel': channel,
        'mch_id': user_id,
        'create_at_start': create_at_start,
        'create_at_end': create_at_end
    }, fetchone=False)

    if ret:
        ret = [list(i) for i in ret]
        for index in range(0, len(ret)):
            ret[index][1] -= timedelta(days=1)
            ret[index][1] = datetime.strftime(ret[index][1], '%Y-%m-%d')
            ret[index][7], ret[index][8], ret[index][5], ret[index][9], ret[index][10] = ret[index][7] / 100, TO_PAY[str(ret[index][8])],\
                PAY_CHANNEL[ret[index][5]], str(
                    ret[index][9]), str(ret[index][10])
        return ret
    return ret


def gen_inlet_info(ws, datas):
    fields = [u'结算日期', u'交易日期', u'商户名称', u'所属渠道商', u'结算户名',
              u'支付渠道', u'结算账号', u'金额', u'状态', u'商户结算单号', u'商户编号', u'商户简称', u'结算银行']

    ws.append(fields)

    for data in datas:
        for index, val in enumerate(data):
            if isinstance(val, str):
                data[index] = re.sub(
                    r'[\000-\010]|[\013-\014]|[\016-\037]|[\x00-\x1f\x7f-\x9f]|[\uffff]', '', val.decode())
        ws.append(data)


def general_filename(user_id):
    _ts = str(time.time())
    filename = "mch_balance_export_" + _ts + ".xlsx"
    user_dl_path = path.join(cur_dir, "static/downloads/", str(user_id))
    if not path.exists(user_dl_path):
        makedirs(user_dl_path)
    file_path = path.join(user_dl_path, filename)
    static_path = path.join("/static/downloads/", str(user_id), filename)
    return filename, file_path, static_path
