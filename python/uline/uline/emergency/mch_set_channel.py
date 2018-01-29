#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado import gen, ioloop

from collections import defaultdict

from uline.public.db import initdb
from uline.model.uline.base import uline_session
from uline.model.uline.base import MchInletInfo, MchUser, DtUser, DtInletInfo
from uline.utils.wxpay import query_wx
from uline.settings import (
    WX_MCH_ID, WXPAY_KEY, APPID, WX_PUB_KEY, WX_PRIVATE_KEY, WX_ROOT_CA,
    WX_APP_MCH_ID, WXPAY_APP_KEY, WX_APP_APPID, WX_APP_PUB_KEY,
    WX_APP_PRIVATE_KEY, WX_APP_ROOT_CA,
)

from uline.public import log


def get_dt_id_has_channel_id():
    return uline_session.query(DtInletInfo.dt_id, DtInletInfo.wx_channel_id).\
        filter(DtInletInfo.wx_channel_id.isnot(None)).all()


def get_dt_id_has_app_channel_id():
    return uline_session.query(DtInletInfo.dt_id, DtInletInfo.wx_app_channel_id).\
        filter(DtInletInfo.wx_app_channel_id.isnot(None)).all()


def get_mch_ids_by_dt(dt_id):
    return uline_session.query(MchInletInfo.mch_id, MchUser.wx_sub_mch_id).\
        join(MchUser, MchUser.mch_id == MchInletInfo.mch_id).\
        filter(MchInletInfo.dt_id == dt_id, MchUser.wx_sub_mch_id.isnot(None)).all()


def wx_app_get_mch_ids_by_dt(dt_id):
    return uline_session.query(MchInletInfo.mch_id, MchUser.wx_app_sub_mch_id).\
        join(MchUser, MchUser.mch_id == MchInletInfo.mch_id).\
        filter(MchInletInfo.dt_id == dt_id, MchUser.wx_app_sub_mch_id.isnot(None)).all()


@gen.coroutine
def set_mch_channel_id(dt_infos, inlet_type='wx'):
    success_results = defaultdict(list)
    fail_results = defaultdict(list)
    for dt_id, channel_id in dt_infos:
        log.uline_script.info(u'dt_id:%s | channel_id:%s' % (dt_id, channel_id))
        mch_infos = get_mch_ids_by_dt(dt_id) if inlet_type == 'wx' else wx_app_get_mch_ids_by_dt(dt_id)

        if inlet_type == 'wx':
            app_id = APPID
            wx_mch_id = WX_MCH_ID
            wx_pay_key = WXPAY_KEY
            wx_private_key = WX_PRIVATE_KEY
            wx_pub_key = WX_PUB_KEY
            wx_root_ca = WX_ROOT_CA
        else:
            app_id = WX_APP_APPID
            wx_mch_id = WX_APP_MCH_ID
            wx_pay_key = WXPAY_APP_KEY
            wx_private_key = WX_APP_PRIVATE_KEY
            wx_pub_key = WX_APP_PUB_KEY
            wx_root_ca = WX_APP_ROOT_CA

        for mch_id, sub_mch_id in mch_infos:
            if sub_mch_id:
                args = {
                    'appid': app_id,
                    'mch_id': wx_mch_id,
                    'sub_mch_id': sub_mch_id,
                    'channel_id': channel_id,
                }

                result = yield query_wx.set_mch_channel_id(args, wx_pay_key, wx_private_key, wx_pub_key, wx_root_ca)

                # 将结果记录起来
                if result['return_code'] == 'SUCCESS' and result['result_code'] == 'SUCCESS':
                    success_results[dt_id].append(mch_id)
                else:
                    error_msg = result.get('err_code_des', '修改子商户配置出现位置错误!')
                    fail_results[dt_id].append({'mch_id': mch_id, 'reason': error_msg})

    log.uline_script.info(u'set_mch_channel_id | success_results:%s' % success_results)
    log.uline_script.info(u'set_mch_channel_id | fail_results:%s' % fail_results)


@gen.coroutine
def main():
    """
    获取有wx_channel_id的渠道商
    """
    log.uline_script.info(u'获取有wx_channel_id的渠道商')
    dt_infos = get_dt_id_has_channel_id()
    yield set_mch_channel_id(dt_infos)

    log.uline_script.info(u'获取有wx_app_channel_id的渠道商')
    dt_infos = get_dt_id_has_app_channel_id()
    yield set_mch_channel_id(dt_infos, inlet_type='wx_app')


if __name__ == '__main__':
    initdb()
    ioloop.IOLoop.instance().run_sync(main)
