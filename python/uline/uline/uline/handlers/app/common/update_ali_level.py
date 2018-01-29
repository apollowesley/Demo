#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Guozhihua

from tornado.web import authenticated, gen
from uline.handlers.baseHandlers import CommanHandler
from uline.public import common
from uline.utils.alipay.query_alipay import query_alipay_mch_common
from uline.model.uline.base import uline_session, MchUser, DtUser


class UpdateAliLevel(CommanHandler):

    @authenticated
    @gen.coroutine
    def get(self):
        mch_id = self.get_argument('mch_id')
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

                rsp = common.scc_rsp(code=200, msg='success', level=level)
            else:
                # 存在一种情况，支付宝还在审核等级
                if ali_ret.get('external_id') == mch_id:
                    rsp = common.f_rsp(code=407, msg='支付宝正在审核该商户，3-5分钟后再尝试')
                else:
                    rsp = common.f_rsp(code=407, msg='该商户没有进件到支付宝')
            self.write(rsp)
            self.finish()
            return

        rsp = common.f_rsp(code=406, msg='fail')
        self.write(rsp)
        self.finish()
        return
