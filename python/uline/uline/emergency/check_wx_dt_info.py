#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado import gen, ioloop

from collections import defaultdict

from uline.public.db import initdb
from uline.model.uline.base import uline_session
from uline.model.uline.base import DtInletInfo, DtUser
from uline.public import log
from uline.utils.wxpay.query_wx import get_wx_mch_info_common, modify_wx_mch_info_common


def get_dt_infos():
    results = uline_session.query(DtUser.dt_id, DtUser.wx_sub_mch_id,
                                  DtInletInfo.dt_short_name, DtInletInfo.service_phone).\
        join(DtInletInfo, DtUser.dt_id == DtInletInfo.dt_id).\
        filter(DtUser.wx_sub_mch_id.isnot(None), DtInletInfo.auth_status != 3).all()

    # fields = ['mch_id', 'sub_mch_id', 'mch_shortname', 'service_phone']
    # _ret = []
    # for result in results:
    #     _ret.append(dict(zip(fields, result)))
    return results


@gen.coroutine
def compare_wx_uline_dt_info(results):
    success_results = []
    fail_results = defaultdict(list)
    for mch_id, sub_mch_id, merchant_shortname, service_phone in results:
        print(mch_id, merchant_shortname, service_phone)
        # if not merchant_shortname or not service_phone:
        #    continue
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
                    print('success#################')
                    break
            else:
                print('update%%%%%%%%%%%%%%')
                print(mch_id)
                # update 操作
                # update_dict = {'sub_mch_id': sub_mch_id, 'merchant_shortname': merchant_shortname,
                #               'service_phone': service_phone}
                # update_ret = yield modify_wx_mch_info_common(update_dict)

                fail_results[mch_id].append(['uline|service_phone:%s|mch_shortname:%s' % (service_phone, merchant_shortname),
                                             'wx|service_phone:%s|mch_shortname:%s' % (mchinfos[1].get('service_phone'), mchinfos[1].get('merchant_shortname'))])
        else:
            log.uline_script.info(u'mch_id:%s | message:%s' % (mch_id, wx_info.get('return_msg')))

    log.uline_script.info('success_results:%s' % success_results)
    log.uline_script.info('fail_results:%s' % fail_results)


@gen.coroutine
def main():
    results = get_dt_infos()

    # results = [('123', '31355660', 'abc', '1111')]
    yield compare_wx_uline_dt_info(results)


if __name__ == '__main__':
    initdb()
    ioloop.IOLoop.instance().run_sync(main)
