#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import sys

import os
import xlrd

from uline.model.uline.info import DtInletInfo
from uline.public.db import initdb
from uline.public.db import uline_session_scope

logger = logging.getLogger('offline_add_dt_channel_id')

file_path = os.path.dirname(__file__)
filelog = logging.FileHandler(file_path + '/add_channel_id.log')
filelog.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
filelog.setFormatter(formatter)
logger.addHandler(filelog)

consolelog = logging.StreamHandler()
consolelog.setLevel(logging.DEBUG)
logger.addHandler(consolelog)


def add_dt_channel_id(session, dt_id, channel_ids):
    """
    修改微信渠道号
    """
    dt_inlet_info = session.query(DtInletInfo).filter(DtInletInfo.dt_id == int(dt_id)).first()
    if not dt_inlet_info:
        logger.error('错误的渠道商id:{}'.format(dt_id))
        return False
    wx_channel_id = channel_ids.get('wx_channel_id', '')
    wx_app_channel_id = channel_ids.get('wx_app_channel_id', '')
    if wx_channel_id and wx_channel_id != dt_inlet_info.wx_channel_id:
        dt_inlet_info.wx_channel_id = wx_channel_id
    if wx_app_channel_id and wx_app_channel_id != dt_inlet_info.wx_app_channel_id:
        dt_inlet_info.wx_app_channel_id = wx_app_channel_id
    session.commit()
    logger.info(
        '更新渠道商号成功，dt_id:{}, wx_channel_id:{}, wx_app_channel_id:{}'.format(dt_id, wx_channel_id, wx_app_channel_id))
    return True


def read_dt_channelid_from_file(file_path, channel_id_index=1, app_channel_id_index=2):
    """
    从excel文档中读取需要修改的渠道商微信渠道号
    """
    data = xlrd.open_workbook(file_path)
    table = data.sheets()[0]
    nrows = table.nrows
    wx_channel_ids = dict()
    for row in xrange(1, nrows):
        rowdata = table.row_values(row)[0:10]
        channel_ids = dict()
        dt_id = int(rowdata[0])
        if rowdata[channel_id_index]:
            channel_ids['wx_channel_id'] = str(rowdata[channel_id_index]).split('.')[0]
        if rowdata[app_channel_id_index]:
            channel_ids['wx_app_channel_id'] = str(rowdata[app_channel_id_index]).split('.')[0]
        if channel_ids:
            wx_channel_ids[dt_id] = channel_ids
    return wx_channel_ids


if __name__ == '__main__':
    xls_file = sys.argv[1]
    # wx_channel_id_index = input("请输入微信渠道商号列号(起始为0): \n")
    wx_channel_ids = read_dt_channelid_from_file(xls_file)
    logger.info('start add dt_channel id:')
    initdb()
    invalid_dt_ids = list()
    with uline_session_scope() as session:
        for each_dt_id in wx_channel_ids:
            result = add_dt_channel_id(session, each_dt_id, wx_channel_ids[each_dt_id])
            if not result:
                invalid_dt_ids.append(str(each_dt_id))
    if invalid_dt_ids:
        logger.error('错误的dt_id有{}个：{}'.format(len(invalid_dt_ids), ','.join(invalid_dt_ids)))
    logger.info('-------end add dt_channel id-------')
