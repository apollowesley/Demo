#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: ghost
# Create: '11/15/17'
import json
from copy import deepcopy
from uline.settings import env, MESSAGE_URL
from uline.backend.__init__ import *
# from uline.public import common, log
from datetime import timedelta, datetime
from os import path, makedirs
from openpyxl import Workbook
from uline.model.uline.info import DtInletInfo, MchInletInfo
from uline.model.uline.user import MchUser, DtUser
from uline.model.uline.other import GatherMchsEmailInfo, ActivatedDtEmailInfo, ActivatedMchEmailInfo
from uline.public.db import uline_session_scope, initdb
from sqlalchemy import func, cast, DateTime
import time
# from tornado.gen import coroutine, Return
from tornado.httpclient import HTTPClient
from tornado import gen, ioloop

cur_dir = path.dirname(path.dirname(path.abspath(__file__)))


DT_SEND = u"""尊敬的{dt_name}：
以下是您在{auth_date}通过ULINE审核的商户汇总,请点击链接进行下载:
{download_url}

重要信息,请注意保密

广州优畅信息技术有限公司
客服电话：400-8047555
"""


# @app.task
def generate_gather_mchs_activated_email(resend_date):

    # yesterday = (datetime.now() - timedelta(1)).strftime("%Y-%m-%d")
    yesterday = resend_date
    gather_send, email_send = [], {}
    fields = [u'商户编号', u'商户类型', u'商户名称', u'商户简称', u'密钥']
    with uline_session_scope() as session:

        auth_mchs = session.query(ActivatedMchEmailInfo).\
            filter(ActivatedMchEmailInfo.status == 3,
                   cast(func.to_char(ActivatedMchEmailInfo.create_at, 'YYYY-MM-DD'), DateTime) == yesterday).all()
        if auth_mchs:
            auth_mch_id = tuple(set([mchinfo.mch_id for mchinfo in auth_mchs]))
            # 查询有审核更新记录的商户门店 id
            mchs = session.query(MchInletInfo.dt_id, MchInletInfo.mch_id,
                                 MchInletInfo.mch_name, MchInletInfo.mch_shortname,
                                 MchUser.mch_pay_key, MchInletInfo.cs_id)
            mchs = mchs.join(MchUser, MchUser.mch_id == MchInletInfo.mch_id)
            mchs = mchs.filter(MchInletInfo.activate_email_tag == 2, MchInletInfo.mch_id.in_(auth_mch_id)).all()
            if mchs:
                mchs = map(list, mchs)
                for i in mchs:
                    if i[5]:
                        i.insert(2, "连锁门店")
                    else:
                        i.insert(2, "普通商户")
                    i.pop()
                gather_send.extend(mchs)

        auth_chains = session.query(ActivatedDtEmailInfo).\
            filter(ActivatedDtEmailInfo.status == 3,
                   cast(func.to_char(ActivatedDtEmailInfo.create_at, 'YYYY-MM-DD'), DateTime) == yesterday).all()
        if auth_chains:
            auth_chain_id = tuple(set([chaininfo.dt_id for chaininfo in auth_chains]))
            # 查询有审核更新记录的连锁商户 id
            chains = session.query(DtInletInfo.parent_id, DtInletInfo.dt_id,
                                   DtInletInfo.dt_name, DtInletInfo.dt_short_name)
            chains = chains.filter(DtInletInfo.activate_email_tag == 2,
                                   DtInletInfo.dt_id.in_(auth_chain_id), DtInletInfo.parent_id != None).all()
            if chains:
                chains = map(list, chains)
                for i in chains:
                    i.insert(2, "连锁商户")
                    i.append("/")
                gather_send.extend(chains)

        if gather_send:
            for i in gather_send:
                if not email_send.get(i[0]):
                    email_send[i[0]] = []
                    email_send[i[0]].append(i[1:])
                else:
                    email_send[i[0]].append(i[1:])
            yesterday = yesterday.split("-")
            send_yesterday = "{}年{}月{}日".format(*yesterday)
            for key, value in email_send.items():
                email_path, file_path, filename = general_filename(key, send_yesterday)
                wb = Workbook()
                activate_info = wb.create_sheet(u'商户开户汇总信息', 0)
                activate_info.append(fields)
                for i in value:
                    activate_info.append(i)
                wb.save(file_path)
                dt_ = session.query(DtInletInfo).filter(DtInletInfo.dt_id == key).one()

                send_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                email_info = {'dt_id': key, 'download_url': filename, "email": dt_.email, 'status': 1,
                              'create_at': send_date}
                session.add(GatherMchsEmailInfo(**email_info))
                try:
                    dt_info = {"dt_name": dt_.dt_name, "auth_date": send_yesterday.decode('utf-8'),
                               "download_url": email_path, "email": dt_.email}
                    response = send_active_dt_email(dt_info)

                    if response and response.body == "2":
                        session.query(GatherMchsEmailInfo).filter(GatherMchsEmailInfo.create_at ==
                                                                  send_date, GatherMchsEmailInfo.dt_id == key).update({'status': 2})
                except Exception as err:
                    # log.exception.info(err)
                    pass

    return


def send_active_dt_email(dt_info):

    receiver_info = deepcopy(dt_info)
    data = {
        'env': env,
        'reciver': receiver_info['email'],
        'title': u'uline商户汇总激活信息',
        'body': DT_SEND.format(**receiver_info)
    }
    http_client = HTTPClient()
    url = MESSAGE_URL + '/v1/email'
    response = http_client.fetch(url, body=json.dumps(data), method='POST')
    return response


def general_filename(user_id, send_yesterday):
    download_url_ = {'SPD_PROD': 'http://cms.spd.uline.cc', 'CMBC_PROD': 'http://cms.cmbxm.mbcloud.com',
                     'LOCAL': 'http://127.0.0.1:8893', "DEV": 'http://mch.stage.uline.cc',
                     'SPDLOCAL': 'http://127.0.0.1:8893'}
    filename = "商户开户汇总邮件" + send_yesterday + "_" + str(time.time()) + ".xlsx"
    user_dl_path = path.join(cur_dir, "uline/static/downloads/", str(user_id))
    if not path.exists(user_dl_path):
        makedirs(user_dl_path)
    file_path = path.join(user_dl_path, filename)
    email_path = (download_url_[env] + path.join("/uline/static/downloads/", str(user_id), filename)).decode('utf-8')
    return email_path, file_path, filename


def main():
    resend_date = "2017-11-21"  # 激活日期
    generate_gather_mchs_activated_email(resend_date)


if __name__ == '__main__':
    initdb()
    ioloop.IOLoop.instance().run_sync(main)
