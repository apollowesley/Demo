# -*- coding: utf-8 -*-
from __future__ import division
from os import path, makedirs
import time
from openpyxl import Workbook
import json

from uline.backend.__init__ import *

cur_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
from uline.public.constants import RECON_HANDLE_STATUS, RECON_EXCEPT_TYPE, DOWNLOAD_INFO_NUM_LIMIT
from uline.public import common, log


@app.task
def generate_xls(user_id, create_at_start,
                 create_at_end, out_trade_no,
                 except_type, handle_status, total_num):
    '''对账时间 商户订单号 处理状态 异常类型 uline对账金额 第三方对账金额 '''
    wb = Workbook()
    inlet_info_ws = wb.create_sheet(u'交易对账异常', 0)

    order_id = common.create_order_id()
    file_name, file_path, static_path = general_filename(user_id)
    if total_num > DOWNLOAD_INFO_NUM_LIMIT:
        gen_order_download_info(order_id, user_id, file_name)

    try:

        inlet_info_data = db_inlet_info(create_at_start,
                                        create_at_end, out_trade_no,
                                        except_type, handle_status)

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


def db_inlet_info(create_at_start,
                  create_at_end, out_trade_no,
                  except_type, handle_status):
    query = """select
            to_char(create_at, 'YYYY-MM-DD HH24:MI:SS'),
            out_trade_no,
            handle_status,
            except_type,
            detail
            from
            recon_tx_error_info
            where (except_type=%(except_type)s or %(except_type)s is null)
            and (handle_status=%(handle_status)s or %(handle_status)s is null)
            and (out_trade_no=%(out_trade_no)s or %(out_trade_no)s is null)
            AND (create_at BETWEEN %(create_at_start)s::TIMESTAMP AND %(create_at_end)s::TIMESTAMP
            OR %(create_at_start)s IS NULL OR %(create_at_end)s IS NULL )
            ORDER BY create_at;"""
    ret = db.selectSQL(query, {
        'except_type': except_type,
        'handle_status': handle_status,
        'out_trade_no': out_trade_no,
        'create_at_start': create_at_start,
        'create_at_end': create_at_end
    }, fetchone=False)

    if ret:
        ret = [list(i) for i in ret]
        ret_l = list()
        for data in ret:
            error_detail = json.loads(data[4])
            total_fee = deal_total_fee(error_detail['total_fee'])
            data[2], data[3] = RECON_HANDLE_STATUS[str(data[2])], RECON_EXCEPT_TYPE[str(data[3])]
            del data[4]
            data.extend(total_fee)
            ret_l.append(data)
        return ret_l
    return []


def gen_order_download_info(order_id, user_id, file_name):
    create_at = update_at = common.timestamp_now()
    query = """insert into order_download_info (order_id, user_id, file, type, status, platform, create_at, update_at)
            values (%s,%s,%s,%s,%s,%s,%s,%s)"""
    db.executeSQL(query, (order_id, user_id, file_name, 3, 1, 2, create_at, update_at))


def modify_order_download_info(order_id, status):
    update_at = common.timestamp_now()
    query = """update order_download_info set status=%s,update_at=%s where order_id=%s;"""
    db.executeSQL(query, (status, update_at, order_id))


def deal_total_fee(total_fee):
    if total_fee[0] and str(total_fee[0]).isdigit():
        total_fee[0] = int(total_fee[0]) / 100
    if total_fee[1] and str(total_fee[1]).isdigit():
        total_fee[1] = int(total_fee[1]) / 100
    return total_fee


def gen_inlet_info(ws, datas):
    fields = [u'对账时间', u'商户订单号', u'处理状态', u'异常类型', u'uline对账金额', u'第三方对账金额']

    ws.append(fields)
    for data in datas:
        ws.append(data)


def general_filename(user_id):
    _ts = str(time.time())
    filename = "recon_transaction_error_export_" + _ts + ".xlsx"
    user_dl_path = path.join(cur_dir, "static/downloads/", str(user_id))
    if not path.exists(user_dl_path):
        makedirs(user_dl_path)
    file_path = path.join(user_dl_path, filename)
    static_path = path.join("/static/downloads/", str(user_id), filename)
    return filename, file_path, static_path
