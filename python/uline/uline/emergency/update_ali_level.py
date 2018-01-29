#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tornado import gen, ioloop
from uline.model.uline.info import MchInletInfo
from uline.public.db import initdb
from uline.utils.alipay.query_alipay import query_alipay_mch_common
from uline.model.uline.base import uline_session, MchUser, DtUser


@gen.coroutine
def update_ali_level(mch_id):
    query_dict = {'external_id': mch_id}
    ali_ret = yield query_alipay_mch_common(query_dict)
    if ali_ret.get('code') == '10000':
        level = None
        for sigle in ['M0', 'M1', 'M2', 'M3']:
            if ali_ret.get('indirect_level', '').endswith(sigle):
                level = sigle
                break
        if level:
            # 判断是否跟数据库的值一致
            mch_user = uline_session.query(MchUser).filter(MchUser.mch_id == mch_id).first()
            dt_user = None
            if not mch_user:
                dt_user = uline_session.query(DtUser).filter(DtUser.dt_id == mch_id).first()
            if (mch_user and mch_user.ali_level != level):
                mch_user.ali_level = level
                uline_session.commit()
            if (dt_user and dt_user.ali_level != level):
                dt_user.ali_level = level
                uline_session.commit()
            print('success|mch_id: %s|level: %s' % (mch_id, level))
        else:
            # 存在一种情况，支付宝还在审核等级
            if ali_ret.get('external_id') == mch_id:
                print('mch_id: %s支付宝正在审核该商户，3-5分钟后再尝试' % mch_id)
            else:
                print('mch_id: %s该商户没有进件到支付宝' % mch_id)


def get_mch_id_not_ali_level():
    return uline_session.query(MchUser.mch_id).\
        join(MchInletInfo, MchInletInfo.mch_id == MchUser.mch_id).\
        filter(MchUser.ali_sub_mch_id.isnot(None),
               MchUser.ali_level.is_(None)).all()


@gen.coroutine
def main():
    mch_ids = get_mch_id_not_ali_level()
    for mch_id in mch_ids:
        yield update_ali_level(str(mch_id[0]))


if __name__ == "__main__":
    initdb()
    ioloop.IOLoop.instance().run_sync(main)
