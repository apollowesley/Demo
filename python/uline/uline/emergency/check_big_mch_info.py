#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado import gen, ioloop

from collections import defaultdict

from uline.public.db import initdb
from uline.model.uline.base import uline_session
from uline.model.uline.base import MchInletInfo, MchUser
from uline.public import log
from uline.utils.wxpay.query_wx import get_wx_mch_info_common, modify_wx_mch_info_common


def get_mch_infos():
    results = uline_session.query(MchUser.mch_id, MchUser.wx_sub_mch_id,
                                  MchInletInfo.mch_shortname, MchInletInfo.service_phone).\
        join(MchInletInfo, MchUser.mch_id == MchInletInfo.mch_id).\
        filter(MchUser.wx_sub_mch_id.isnot(None), MchInletInfo.auth_status != 3,
               MchInletInfo.dt_id == '10000008244',
               MchUser.wx_use_parent == 2).all()

    # fields = ['mch_id', 'sub_mch_id', 'mch_shortname', 'service_phone']
    # _ret = []
    # for result in results:
    #     _ret.append(dict(zip(fields, result)))
    return results


@gen.coroutine
def get_uline_mch_info(mch_id):
    return uline_session.query(MchUser.wx_sub_mch_id)


@gen.coroutine
def compare_wx_uline_mch_info(results):
    success_results = []
    fail_results = defaultdict(list)
    for mch_id, sub_mch_id, merchant_shortname, service_phone in results:
        query_dict = {'sub_mch_id': sub_mch_id,
                      'page_index': 1,
                      'page_size': 10
                      }
        wx_info = yield get_wx_mch_info_common(query_dict)

        if wx_info.get('return_code') == 'SUCCESS' and wx_info.get('result_code') == 'SUCCESS':
            mchinfos = wx_info.get('mchinfo')
            for singe_info in mchinfos:
                if singe_info.get('merchant_shortname') == u'招商银行微信支付商户':
                    success_results.append(mch_id)
                    break
            else:
                # update 操作
                update_dict = {'sub_mch_id': sub_mch_id, 'merchant_shortname': u'招商银行微信支付商户',
                               'service_phone': service_phone}
                update_ret = yield modify_wx_mch_info_common(update_dict)

                fail_results[mch_id].append(['uline|service_phone:%s|mch_shortname:%s' % (service_phone, merchant_shortname),
                                             'wx|service_phone:%s|mch_shortname:%s' % (mchinfos[1].get('service_phone'), mchinfos[1].get('merchant_shortname'))])
        else:
            log.uline_script.info(u'mch_id:%s | message:%s' % (mch_id, wx_info.get('return_msg')))

    log.uline_script.info('success_results:%s' % success_results)
    log.uline_script.info('fail_results:%s' % fail_results)


@gen.coroutine
def main():
    results = get_mch_infos()

    # results = [('123', '31355660', 'abc', '1111')]

    yield compare_wx_uline_mch_info(results)


if __name__ == '__main__':
    initdb()
    ioloop.IOLoop.instance().run_sync(main)
