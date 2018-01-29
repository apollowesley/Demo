#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict

from tornado import gen, ioloop
from uline.model.uline.info import MchInletInfo, AddressInfo
from uline.public.db import initdb
from uline.model.uline.base import uline_session
import json


def get_address():
    address = uline_session.query(AddressInfo.upper_code, AddressInfo.area_code,
                                  AddressInfo.area_name).filter().all()
    _dict = {}
    for upper_code, area_code, area_name in address:
        if not upper_code:
            continue

        temp = _dict.get(upper_code)
        if not temp:
            _dict[upper_code] = {area_code: area_name.encode('utf-8')}
        else:
            temp[area_code] = area_name.encode('utf-8')
            # _dict[area_code] = temp
    return _dict


@gen.coroutine
def main():
    _dict = get_address()
    new_dict = json.dumps(_dict, encoding="UTF-8", ensure_ascii=False)
    file_object = open('/Users/apple/ulaiber-projects/uline/emergency/1.txt', 'w')
    file_object.write(str(new_dict))
    file_object.close()


if __name__ == "__main__":
    initdb()
    ioloop.IOLoop.instance().run_sync(main)
