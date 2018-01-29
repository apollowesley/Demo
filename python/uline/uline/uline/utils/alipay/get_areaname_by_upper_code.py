#!/usr/bin/env python
# -*- coding: utf-8 -*-
from uline.model.uline.info import AddressInfo
from uline.model.uline.base import uline_session
from sqlalchemy import or_


def get_areanames_by_city(city):
    addressinfo_list = uline_session.query(AddressInfo.area_code).filter(or_(
        AddressInfo.area_name == city, AddressInfo.short_name == city)).first()
    new_addressinfos = uline_session.query(AddressInfo).filter(
        AddressInfo.upper_code == addressinfo_list).all()
    uline_session.close()
    return [new_addressinfo.area_name for new_addressinfo in new_addressinfos] if new_addressinfos else None
