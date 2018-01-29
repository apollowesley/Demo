#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from tornado import gen, ioloop
from uline.model.uline.info import MchInletInfo
from uline.model.uline.other import ChangeRecord
from uline.public.db import initdb
from uline.model.uline.base import uline_session, MchUser

# 解决原来审核通过，没有将ChangeRecord中区域信息保存到MchInletInfo表中


def get_mch_id():
    return uline_session.query(MchUser.mch_id).\
        join(MchInletInfo, MchInletInfo.mch_id == MchUser.mch_id).\
        filter(MchUser.ali_sub_mch_id.isnot(None),
               MchInletInfo.dt_id == '10000042547',
               MchUser.ali_level == 'M1').all()


def get_district(mch_id):
    try:
        data = uline_session.query(ChangeRecord.data_json).filter(ChangeRecord.mch_id == mch_id).first()
        if data:
            data = json.loads(data[0])
            district = data.get('district')
            if district:
                save_district(mch_id, district)
    except:
        raise


def save_district(mch_id, district):
    mch_inlet = uline_session.query(MchInletInfo).filter(MchInletInfo.mch_id == mch_id).first()
    if not mch_inlet.district:
        print '%s old:%s new:%s' % (mch_id, mch_inlet.district, district)
        mch_inlet.district = district
        uline_session.commit()


@gen.coroutine
def main():
    mch_ids = get_mch_id()
    for mch_id in mch_ids:
        get_district(mch_id)


if __name__ == "__main__":
    initdb()
    ioloop.IOLoop.instance().run_sync(main)
