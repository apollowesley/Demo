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
from datetime import timedelta
from .form import ReconErrorSearch
from uline.public.constants import RECON_EXCEPT_TYPE, RECON_HANDLE_STATUS
from uline.public.permit import check_permission


class ReconTransactionErrorIndexHandler(BkAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        self.form = ReconErrorSearch(self)
        if not self.form.validate():
            self.redirect('/bank/recon/transaction')
            return
        pageindex = int(self.get_argument("p", 1))
        self.data, self.total_number = self.db_execute(self.form, (pageindex - 1) * 10)

    def get(self):
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('bank/reconciliation/transaction.html', navigate_html=navigate_html, data=self.data, form=self.form,
                    total_num=self.total_number)

    def post(self):
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('bank/reconciliation/transaction.html', navigate_html=navigate_html, data=self.data, form=self.form,
                    total_num=self.total_number)

    def db_execute(self, form, offset):
        create_at_start = form.create_at_start.data or None
        create_at_end = form.create_at_end.data or None
        except_type = form.except_type.data or None
        handle_status = form.handle_status.data or None
        out_trade_no = form.out_trade_no.data or None
        # transaction_id = form.transaction_id.data or None

        # 因为end是0时0分,将它续一天┑(￣Д ￣)┍
        if create_at_end:
            create_at_end += timedelta(days=1)
        query = """select
        to_char(create_at, 'YYYY-MM-DD HH24:MI:SS'),
        out_trade_no,
        handle_status,
        except_type,
        detail,
        count(*) over () as total
        from
        recon_tx_error_info
        where (except_type=%(except_type)s or %(except_type)s is null)
        and (handle_status=%(handle_status)s or %(handle_status)s is null)
        and (out_trade_no=%(out_trade_no)s or %(out_trade_no)s is null)
        AND (create_at BETWEEN %(create_at_start)s::TIMESTAMP AND %(create_at_end)s::TIMESTAMP
        OR %(create_at_start)s IS NULL OR %(create_at_end)s IS NULL )
        ORDER BY create_at DESC
        OFFSET %(offset)s ROWS FETCH NEXT 10 ROWS ONLY;"""
        ret = self.db.selectSQL(query, {
            'except_type': except_type,
            'handle_status': handle_status,
            'out_trade_no': out_trade_no,
            'create_at_start': create_at_start,
            'create_at_end': create_at_end,
            'offset': offset
        }, fetchone=False)
        if ret:
            ret = [list(i) for i in ret]
            ret_l = list()
            for data in ret:
                error_detail = json.loads(data[4])
                total_fee = self.deal_total_fee(error_detail['total_fee'])
                data[2], data[3] = RECON_HANDLE_STATUS[str(data[2])], RECON_EXCEPT_TYPE[str(data[3])]
                del data[4]
                data.extend(total_fee)
                ret_l.append(data)
            return ret_l, ret_l[0][-3]
        return [], 0

    def deal_total_fee(self, total_fee):
        if total_fee[0] and str(total_fee[0]).isdigit():
            total_fee[0] = int(total_fee[0]) / 100
        if total_fee[1] and str(total_fee[1]).isdigit():
            total_fee[1] = int(total_fee[1]) / 100
        return total_fee
