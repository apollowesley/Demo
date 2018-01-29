#!/usr/bin/env python
# -*- coding: utf-8 -*-
from uline.model.uline.user import MchUser
from uline.public.db import initdb, uline_session_scope
from uline.model.uline.base import uline_session
from uline.model.uline.info import IndustryUlineInfo, MchInletInfo
from tornado import ioloop


def get_industry_code():
    industry_code = {}
    industry_ulines = uline_session.query(IndustryUlineInfo).filter(IndustryUlineInfo.status == 1).all()
    print len(industry_ulines)
    uline_session.close()
    for industry_uline in industry_ulines:
        industry_code[industry_uline.industry_code] = industry_uline.jd_ind_code
    return industry_code


def update_industry_code():
    code_dict = get_industry_code()
    mchinletintos = uline_session.query(MchInletInfo, MchUser).join(
        MchUser, MchUser.mch_id == MchInletInfo.mch_id).all()
    # filter(MchUser.ali_sub_mch_id.isnot(None)).all()
    uline_session.close()
    for mchinletinto, mch_user in mchinletintos:
        with uline_session_scope()as session:
            jd_ind_code = code_dict.get(mchinletinto.u_ind_code)
            if mchinletinto.jd_ind_code != jd_ind_code:
                mchinletinto.jd_ind_code = jd_ind_code
                session.add(mchinletinto)


if __name__ == "__main__":
    initdb()
    ioloop.IOLoop.instance().run_sync(update_industry_code)
