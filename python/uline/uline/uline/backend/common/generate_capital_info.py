#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
from __future__ import division
from os import path, makedirs
import time
from openpyxl import Workbook
from collections import defaultdict
from uline.handlers.app.common import merchant_capital_util
from uline.model.uline.info import OrderDownloadInfo
from uline.public import common, log, constants
from uline.public.db import uline_session_scope
from uline.model.uline.info import DtInletInfo

from uline.backend.__init__ import *

cur_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
from uline.public.constants import PAYMENT, AUTH_STATUS, BALANCE_TYPE, BALANCE_WAY, DOWNLOAD_INFO_NUM_LIMIT, \
    WX_USE_PARENT


# 任务队列
# 生成商户进件信息
@app.task
def generate_xls(user_id, query_conditions, total_num):
    wb = Workbook()
    inlet_info_ws = wb.create_sheet(u'商户转入转出信息', 0)
    order_id = common.create_order_id()
    file_name, file_path, static_path = general_filename(user_id)
    capital_list = []
    if total_num > DOWNLOAD_INFO_NUM_LIMIT:
        gen_order_download_info(order_id, user_id, file_name)
    try:
        with uline_session_scope() as session:
            total_count, capital_info_list = merchant_capital_util.get_merchant_capital_list(session, query_conditions,
                                                                                             page_size=0)
            for capital_db_info in capital_info_list:
                capital_info = {key: getattr(capital_db_info, key, '') for key in capital_db_info.keys()}
                cs_id = capital_db_info.cs_id
                capital_info['chain_name'] = ''
                capital_info['chain_id'] = ''
                if cs_id:
                    chain_info = session.query(DtInletInfo).filter(DtInletInfo.dt_id == cs_id).filter(
                        DtInletInfo.parent_id != None)
                    if chain_info:
                        capital_info['chain_name'] = chain_info.dt_name
                        capital_info['chain_id'] = chain_info.dt_id
                capital_list.append(capital_info)
        log.uline_celery.info('capital count:{}'.format(len(capital_list)))
        gen_capital_info(inlet_info_ws, capital_list)

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
    db.executeSQL(query, (order_id, user_id, file_name, 13, 1, 1, create_at, update_at))


def modify_order_download_info(order_id, status):
    update_at = common.timestamp_now()
    query = """update order_download_info set status=%s,update_at=%s where order_id=%s;"""
    db.executeSQL(query, (status, update_at, order_id))


def gen_capital_info(ws, datas):
    fields = [u'创建时间', u'业务单号', u'业务名称', u'商户/门店名称', u'商户/门店编号', u'商户/门店简称', u'所属连锁商户名称',
              u'所属连锁商户编号', u'所属渠道名称', u'所属渠道编号', u'结算银行', u'支行联行号', u'结算户名', u'结算账号',
              u'资金账户', u'金额', u' 状态', u'备注']
    # 渠道基本信息表
    ws.append(fields)
    keys = ['create_at', 'mch_clear_no', 'business_type', 'mch_name', 'mch_id', 'mch_shortname', 'chain_name',
            'chain_id', 'dt_name', 'dt_id', 'rcvbankname', 'rcvbanksettleno', 'rcvacctname', 'rcvacctno', 'channel',
            'trade_amount', 'pay_status', 'remarks']
    for data in datas:
        business_type = data.get('business_type', '')
        data['business_type'] = constants.MCH_CLEAR_TYPES.get(int(business_type), '')
        data['pay_status'] = merchant_capital_util.get_capital_pay_status(business_type, data.get('pay_status', ''))
        data_info = [data.get(key, '') for key in keys]
        ws.append(data_info)


def general_filename(user_id):
    _ts = str(time.time())
    filename = "mch_capital_" + _ts + ".xlsx"
    user_dl_path = path.join(cur_dir, "static/downloads/", str(user_id))
    if not path.exists(user_dl_path):
        makedirs(user_dl_path)
    file_path = path.join(user_dl_path, filename)
    static_path = path.join("/static/downloads/", str(user_id), filename)
    return filename, file_path, static_path
