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


@app.task
def generate_xls(user_id, dt_name, mch_name, dt_id, mch_id, create_at_start, create_at_end, pay_status,
                 total_num, channel, balance_account, cs_mch_shortname, cs_mch_id):
    '''结算日期 商户名称 所属渠道商 结算户名 结算账号 金额 状态'''
    wb = Workbook()
    inlet_info_ws = wb.create_sheet(u'商户结算信息', 0)

    order_id = common.create_order_id()
    file_name, file_path, static_path = general_filename(user_id)
    if total_num > DOWNLOAD_INFO_NUM_LIMIT:
        gen_order_download_info(order_id, user_id, file_name)

    try:
        inlet_info_data = db_inlet_info(user_id, dt_name, mch_name, dt_id, mch_id,
                                        create_at_start, create_at_end, pay_status, channel, balance_account, cs_mch_shortname, cs_mch_id)

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
                          5, 1, 1, create_at, update_at))


def modify_order_download_info(order_id, status):
    update_at = common.timestamp_now()
    query = """update order_download_info set status=%s,update_at=%s where order_id=%s;"""
    db.executeSQL(query, (status, update_at, order_id))


def db_inlet_info(user_id, dt_name, mch_name, dt_id, mch_id, create_at_start, create_at_end,
                  pay_status, channel, balance_account, cs_mch_shortname, cs_mch_id):
    query = """select
           to_char(mdbi.pay_start_time, 'YYYY-MM-DD HH24:MI:SS'),
           to_char(mdbi.create_at, 'YYYY-MM-DD HH24:MI:SS'),
           du.dt_name,
           dii.dt_id,
           dii.dt_name,
           dii.dt_short_name,
           mii.mch_id,
           mii.mch_name,
           mii.mch_shortname,
           mdbi.rcvbankname,
           mb.bank_no,
           mdbi.rcvacctname,
           mdbi.rcvacctno,
           mdbi.channel,
           mdbi.tranamt,
           mdbi.pay_status,
           mdbi.failure_details,
           mii.cs_id
           from mch_daily_balance_info as mdbi
           inner join mch_inlet_info as mii on mii.mch_id = mdbi.mch_id
           inner join mch_balance as mb on mb.mch_id = mdbi.mch_id
           inner join dt_user as du on du.dt_id = mii.dt_id
           left join dt_inlet_info as dii on dii.dt_id = mii.cs_id
           where mdbi.tranamt > 0
           and(mb.balance_account=%(balance_account)s or %(balance_account)s is null)
           and (mdbi.pay_status=%(pay_status)s or %(pay_status)s is null)
           and (mdbi.channel=%(channel)s or %(channel)s is null)
           and (du.dt_name ~ %(dt_name)s or %(dt_name)s is null)
           and (mii.mch_id::VARCHAR ~ E%(mch_id)s::VARCHAR or %(mch_id)s::VARCHAR is null)
           and (mii.mch_shortname ~ E%(cs_mch_shortname)s or %(cs_mch_shortname)s is null)
           and (mii.mch_name ~ E%(mch_name)s or %(mch_name)s is null)
            {find_type}
           and (mii.bk_id=%(bk_id)s)
           and (du.dt_id::VARCHAR ~ %(dt_id)s::VARCHAR or %(dt_id)s::VARCHAR is null)
           and (mdbi.pay_start_time BETWEEN %(create_at_start)s::TIMESTAMP AND %(create_at_end)s::TIMESTAMP
           OR %(create_at_start)s IS NULL OR %(create_at_end)s IS NULL )
           ORDER BY mdbi.create_at desc;"""

    query_dict = {
        'pay_status': pay_status,
        'channel': channel,
        'dt_id': dt_id,
        'dt_name': dt_name,
        'create_at_start': create_at_start,
        'create_at_end': create_at_end,
        'balance_account': balance_account,
        'mch_name': db.escape(mch_name),
        'cs_mch_shortname': db.escape(cs_mch_shortname),
        'bk_id': user_id
    }

    query_dict.update({'cs_mch_shortname': db.escape(cs_mch_shortname),
                       'mch_id': db.escape(cs_mch_id)}) if cs_mch_shortname or cs_mch_id else \
        query_dict.update({'mch_id': db.escape(mch_id)})

    if cs_mch_shortname or cs_mch_id:
        find_type = "and mii.cs_id is not null"
    else:
        find_type = "and mii.cs_id is null" if mch_name or mch_id else ""

    ret = db.selectSQL(query.format(find_type=find_type),
                       query_dict, fetchone=False)

    if ret:
        ret = [list(i) for i in ret]
        for index in range(0, len(ret)):
            ret[index][14], ret[index][15], ret[index][13], ret[index][3], ret[index][6] = ret[index][14] / 100, \
                TO_PAY[str(ret[index][15])], PAY_CHANNEL[ret[index][13]], str(
                    ret[index][3]), str(ret[index][6])
            if not ret[index][17]:
                ret[index][3], ret[index][4], ret[index][5] = ret[index][6], ret[index][7], ret[index][8]
                ret[index][6], ret[index][7], ret[index][8] = ["-"] * 3
            del ret[index][17]
        return ret
    return ret


def gen_inlet_info(ws, datas):
    fields = [u'结算日期', u'交易日期', u'所属渠道商', u'商户编号', u'商户名称', u'商户简称', u'门店编号', u'门店名称', u'门店简称', u'结算银行', u'支行联行号', u'结算户名',
              u'结算账号', u'支付渠道',  u'金额', u'状态', u'备注']

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
