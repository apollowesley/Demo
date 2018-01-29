#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict

from tornado import gen, ioloop
from uline.model.uline.info import MchInletInfo
from uline.public.db import initdb
from uline.model.uline.base import uline_session
from city_json import city_json


def save_new_address(city_list):
    fail_mch_ids = defaultdict(list)
    mch_infos = uline_session.query\
        (MchInletInfo.dt_id, MchInletInfo.mch_id, MchInletInfo.address, MchInletInfo.province,
         MchInletInfo.city, MchInletInfo.district).\
        all()
    for dt_id, mch_id, address, province, city, district in mch_infos:
        # 如果存在区域信息，则跳过
        if district:
            continue

        find_district = None

        # 根据city找到所有有可能的区域信息
        districts = city_list.get(u'%s-%s' % (province, city))
        if not districts:
            fail_mch_ids[dt_id].append(mch_id)
            continue
        for single in districts[0]:
            if address.find(single) != -1:
                find_district = single
                break
        # 如果成功匹配，保存到district中
        if find_district:
            mch_inlet_info = uline_session.query(MchInletInfo).\
                filter(MchInletInfo.mch_id == mch_id).first()
            mch_inlet_info.district = find_district
            uline_session.commit()
        else:
            fail_mch_ids[dt_id].append(mch_id)
    print fail_mch_ids


def deal_city_to_utf8(city_json):
    city_list = defaultdict(list)
    for key, value in city_json.items():
        name = key.decode('utf-8')
        city_list[name].append([row.decode('utf-8') for row in value])

    return city_list


@gen.coroutine
def main():
    city_list = deal_city_to_utf8(city_json.get('a'))
    save_new_address(city_list)


if __name__ == "__main__":
    initdb()
    ioloop.IOLoop.instance().run_sync(main)
