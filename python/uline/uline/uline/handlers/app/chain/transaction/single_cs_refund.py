# -*- coding: utf-8 -*-
from __future__ import division
from tornado.httpclient import AsyncHTTPClient
from tornado.web import authenticated, asynchronous
from tornado import gen
import xmltodict
from uline.handlers.app.merchant.transaction.initiateRefundToThirdpart import \
    initiateRefundToThirdpartHandle, generate_mch_refund_no
from uline.handlers.baseHandlers import ChainAdminHandler
from .form import MerchanCanRefund, MerchanInitiateRefund
from uline.public import common, log
from uline.public.common import bcrypt_pwd
from uline.settings import (
    WEIXIN_REFUND_URL, ALIPAY_REFUND_URL
)
from uline.public.permit import check_permission


class CsRefundDetailHandler(ChainAdminHandler):

    @authenticated
    @check_permission("/transaction/trade")
    def prepare(self):
        self.form = MerchanCanRefund(self)
        self.mch_id = self.form.mch_id.data
        if not self.form.validate():
            self.redirect('/chain/transaction/refund')
            return
        self.out_trade_no = self.form.out_trade_no.data

    @asynchronous
    @gen.coroutine
    def get(self):
        data = yield self.db_execute()
        data['out_trade_no'] = self.out_trade_no
        data['mch_id'] = self.mch_id
        self.render('chain/transaction/singleCsRefund.html', data=data)

    # @asynchronous
    # @gen.coroutine
    # def post(self):
    #     ret = yield self.db_execute(self.form, (self.pageindex - 1) * 10)
    #     data, total_number = ret[0], ret[1]
    #     navigate_html = self.get_navigate_html(total_number)
    #     self.render('merchant/transaction/merchantRefund.html', navigate_html=navigate_html, data=data,
    #                 form=self.form, total_num=total_number)

    @gen.coroutine
    def db_execute(self):
        # 查mch_trade_no 和 total_fee_query
        mch_trade_query = """select total_fee, mch_trade_no from orders where out_trade_no=%(out_trade_no)s"""
        ret = self.tdb.selectSQL(mch_trade_query, {'out_trade_no': self.out_trade_no})

        refund_fee_query = """SELECT sum(refund_fee)
                  from order_refunds WHERE out_trade_no=%(out_trade_no)s"""
        refund_ret = self.tdb.selectSQL(refund_fee_query, {'out_trade_no': self.out_trade_no})

        has_refund_fee = refund_ret[0] if refund_ret and refund_ret[0] else 0
        can_refund_fee = ret[0] - has_refund_fee

        raise gen.Return({'mch_trade_no': ret[1],
                          'can_refund_fee': can_refund_fee / 100 if can_refund_fee else 0,
                          'total_fee': ret[0] / 100 if ret[0] else 0,
                          'has_refund_fee': has_refund_fee / 100 if has_refund_fee else 0})


class CsInitiateRefundHandler(ChainAdminHandler):

    @authenticated
    @check_permission("/transaction/trade")
    def prepare(self):
        self.form = MerchanInitiateRefund(self)
        self.form.cs_id = self.get_current_user()
        if not self.form.validate():
            f_rsp = common.f_rsp(code=407, msg=self.form.errors)
            self.finish(f_rsp)
        self.out_trade_no = self.form.out_trade_no.data
        self.refund_fee = self.form.refund_fee.data
        self.mch_id = self.form.mch_id.data
        self.cs_id = self.get_current_user()
        self.refund_password = self.form.Pwd.data

    @asynchronous
    @gen.coroutine
    def post(self):
        validation_password = yield self.validation_mch_refund_password()
        if not validation_password:
            f_rsp = common.scc_rsp(code=408, msg='Invalid refund password')
            self.finish(f_rsp)
        else:
            data = yield self.get_trade_detail_by_out_trade_no()
            mch_pay_key = yield self.get_mch_pay_key()
            refund_fee = int(float(self.refund_fee) * 100)
            # 无可退金额
            if not mch_pay_key or not self.refund_fee:
                f_rsp = common.scc_rsp(code=406, msg='No refund amount')
                self.finish(f_rsp)
            else:
                initiate = initiateRefundToThirdpartHandle(self.mch_id,
                                                           data.get('mch_trade_no'),
                                                           generate_mch_refund_no(self.mch_id),
                                                           data.get('total_fee'),
                                                           refund_fee,
                                                           self.mch_id,
                                                           )
                xml = initiate.get_req_xml(mch_pay_key)
                log.detail.info(xml)
                http_client = AsyncHTTPClient()
                url = WEIXIN_REFUND_URL if data.get('channel') == 'weixin' else ALIPAY_REFUND_URL
                response = yield http_client.fetch(url, method='POST', body=xml)

                _dict = xmltodict.parse(response.body)
                # 成功退款
                if _dict.get('xml').get('return_code') == 'SUCCESS'\
                        and _dict.get('xml').get('result_code') == 'SUCCESS':
                    s_rsp = common.scc_rsp(code=200, msg='SUCCESS')

                # 退款失败
                else:
                    log.detail.info(_dict)
                    s_rsp = common.scc_rsp(code=405, msg=_dict.get('xml').get('err_code_des'))
                self.write(s_rsp)

    @gen.coroutine
    def get_trade_detail_by_out_trade_no(self):
        _query = """ select
                     mch_trade_no,
                     device_info,
                     total_fee,
                     fee_type,
                     channel
                     from orders where out_trade_no=%(out_trade_no)s"""
        ret = self.tdb.selectSQL(_query, {'out_trade_no': self.out_trade_no})
        fields = ["mch_trade_no", "device_info", "total_fee", "fee_type", "channel"]
        data = dict(zip(fields, ret))
        raise gen.Return(data)

    @gen.coroutine
    def get_mch_pay_key(self):
        _query = 'select mch_pay_key from mch_user where mch_id=%(mch_id)s'
        ret = self.db.selectSQL(_query, {'mch_id': self.mch_id})
        data = ret[0] if ret else None
        raise gen.Return(data)

    @gen.coroutine
    def validation_mch_refund_password(self):
        valid = False
        selSql = "select dt_id,refund_password from dt_user where dt_id=%s"
        db_ret = self.db.selectSQL(selSql, (self.cs_id,))
        if db_ret:
            valid = yield bcrypt_pwd(str(self.refund_password), db_ret[1])
        raise gen.Return(valid)
