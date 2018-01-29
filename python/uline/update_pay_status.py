#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: ficapy
# Create: '7/7/17'

from datetime import datetime, timedelta
from os import path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BASE_PATH = '/home/deploy/uline_clear/pay/spdb/addition'
ULINE_DB = 'postgresql+psycopg2://ulinesa:Xm.u7!nebio2@192.168.20.100/spd_uline'

Base = declarative_base()
uline_engine = create_engine(ULINE_DB, pool_recycle=3600)
uline_Session = sessionmaker()
uline_Session.configure(bind=uline_engine)
session = uline_Session()


def get_path():
    ret = []
    for i in [datetime.now().strftime("%Y%m%d"), (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")]:
        ret.append(path.join(BASE_PATH, i + '.txt'))
    return ret


def pick_trand_id(target_path):
    ret = []
    if not path.exists(target_path):
        return ret
    with open(target_path) as f:
        for i in f:
            if '|' not in i:
                continue
            else:
                ret.append(i.split("|")[0])
    return ret


def update_pay_status(trand_list):
    if not trand_list:
        return
    session.execute("UPDATE mch_daily_balance_info SET pay_status = 2 WHERE mch_trand_id IN :mch_trand_id", params={
        "mch_trand_id": tuple(trand_list)
    })
    session.execute("""UPDATE dt_daily_balance_info SET pay_status=2 WHERE dt_trand_id IN :dt_trand_id""", params={
        "dt_trand_id": tuple(trand_list)
    })
    session.commit()


if __name__ == "__main__":
    for target_path in get_path():
        trand_list = pick_trand_id(target_path)
        update_pay_status(trand_list)

