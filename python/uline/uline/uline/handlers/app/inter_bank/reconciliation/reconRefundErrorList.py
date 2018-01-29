# -*- coding: utf-8 -*-
'''
BEGIN
对账异常信息
    必选参数:

    可选参数:

    成功:
        {"code": 200, "msg": "成功"}
    失败:
        {"code": 406, "msg": "失败"}
END
'''
from __future__ import division
import json
import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import BkAdminHandler
from .form import ReconErrorRefundList
from uline.public.constants import RECON_HANDLE_STATUS, RECON_EXCEPT_TYPE
from uline.public.permit import check_permission


class ReconRefundErrorListHandler(BkAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        form = ReconErrorRefundList(self)
        if not form.validate():
            self.redirect('/bank/balance/refund/list')
            return
        self.out_refund_no = form.out_refund_no.data

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data, detail = self.do_execute()
        detail = self.deal_detail(detail)
        recon_error_html = self.render_string('common/recon_error_transaction.html', detail=detail)
        self.render('bank/reconciliation/refundList.html', recon_error_html=recon_error_html, data=data)

    def do_execute(self):
        ret, detail = self.get_recon_refund_error()
        tb_ret = self.get_order_refund()
        ul_mch_ret = self.get_mch_info(tb_ret)

        ret.update(tb_ret)
        ret.update(ul_mch_ret)
        detail = self.deal_detail_total_fee(detail)

        return ret, detail

    def deal_detail(self, detail):
        format_detail = {'sub_mch_id': '子商户号', 'cash_fee_type': '现金支付货币类型', 'transaction_id': '微信支付订单号',
                         'appid': 'Uine公众账号ID', 'time_end': '支付完成时间', 'bank_type': '付款银行',
                         'attach': '附加数据', 'mch_id': '优畅商户号	', 'out_refund_no': '商户退款号',
                         'total_fee': '订单金额', 'trade_state': '交易状态	', 'return_fee': '退款金额',
                         'out_trade_no': '商户交易号'}
        detail_new = dict()
        for d_key, value in detail.items():
            for f_key, f_value in format_detail.items():
                if d_key == f_key:
                    detail_new.update({f_value: value})
        sorted(detail_new.items(), key=lambda d: d[0])
        return detail_new

    def get_recon_refund_error(self):
        query = """select
                to_char(create_at, 'YYYY-MM-DD HH24:MI:SS'),
                detail,
                handle_status,
                except_type
                from
                recon_refund_error_info
                where out_refund_no=%s;"""
        ret = list(self.db.selectSQL(query, (self.out_refund_no,)))
        ret[2], ret[3] = RECON_HANDLE_STATUS[str(ret[2])], RECON_EXCEPT_TYPE[str(ret[3])]
        detail = json.loads(ret[1])

        fields = ['create_at', 'detail', 'handle_status', 'except_type']
        ul_ret = dict(zip(fields, ret))
        ul_ret['out_refund_no'] = self.out_refund_no
        return ul_ret, detail

    def get_order_refund(self):
        default_ret = [''] * 2
        query = """select ul_mch_id,transaction_id from order_refunds where out_refund_no=%s;"""
        ret = self.tdb.selectSQL(query, (self.out_refund_no,))
        fields = ['mch_id', 'transaction_id']
        tb_ret = dict(zip(fields, ret)) if ret else dict(zip(fields, default_ret))
        return tb_ret

    def get_mch_info(self, data):
        ret = [''] * 3
        if data['mch_id']:
            query = """select
                       mch_user.mch_name,
                       dt_user.dt_name,
                       dt_user.dt_id
                       from mch_user
                       inner join mch_inlet_info on mch_inlet_info.mch_id = mch_user.mch_id
                       inner join dt_user on dt_user.dt_id = mch_inlet_info.dt_id
                       where mch_user.mch_id=%s;"""
            ret = self.db.selectSQL(query, (data['mch_id'],))
        fields = ['mch_name', 'dt_name', 'dt_id']
        ul_mch_ret = dict(zip(fields, ret))
        return ul_mch_ret

    def deal_detail_total_fee(self, detail):
        total_fee = detail.get('return_fee')
        if total_fee:
            total_fee = self.deal_total_fee(total_fee)
            detail['total_fee'] = total_fee
        return detail

    def deal_total_fee(self, total_fee):
        if total_fee[0] and str(total_fee[0]).isdigit():
            total_fee[0] = int(total_fee[0]) / 100
        if total_fee[1] and str(total_fee[1]).isdigit():
            total_fee[1] = int(total_fee[1]) / 100
        return total_fee
