# -*- coding: utf-8 -*-
from __future__ import division
import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import DtAdminHandler
from datetime import timedelta, datetime
from .form import DistributorBalanceSearch
from uline.public.constants import TO_PAY, PAY_CHANNEL
from uline.public.permit import check_permission


class DistributorBalanceIndexHandler(DtAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        self.form = DistributorBalanceSearch(self)
        if not self.form.validate():
            self.redirect('/dist/balance/dt')
            return
        pageindex = int(self.get_argument("p", 1))
        self.data, self.total_number = self.db_execute(self.form, (pageindex - 1) * 10)

    def get(self):
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('distributor/balance/distributorBalance.html', navigate_html=navigate_html, data=self.data,
                    form=self.form, total_num=self.total_number)

    def post(self):
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('distributor/balance/distributorBalance.html', navigate_html=navigate_html, data=self.data,
                    form=self.form, total_num=self.total_number)

    def db_execute(self, form, offset):
        """

        :param form:
        :param offset:
        :return:
        """
        create_at_start = form.create_at_start.data or None
        create_at_end = form.create_at_end.data or None
        pay_status = form.pay_status.data or None
        channel = form.channel.data or None

        dt_id = self.current_user

        # 因为end是0时0分,将它续一天┑(￣Д ￣)┍
        if create_at_end:
            create_at_end += timedelta(days=1)

        query = """select
                   to_char(ddbi.pay_start_time, 'YYYY-MM-DD HH24:MI:SS'),
                   ddbi.need_pay_time,
                   ddbi.rcvAcctName,
                   ddbi.channel,
                   ddbi.rcvacctno,
                   ddbi.tranAmt,
                   ddbi.pay_status,
                   ddbi.dt_daily_balance_no,
                   count(*) over () as total
                   from dt_daily_balance_info as ddbi
                   inner join dt_balance db on db.dt_id = ddbi.dt_id
                   where ddbi.tranamt > 0
                   and ddbi.dt_id=%(dt_id)s
                   and (ddbi.pay_status=%(pay_status)s or %(pay_status)s is null)
                   and (ddbi.channel=%(channel)s or %(channel)s is null)
                   and (ddbi.pay_start_time BETWEEN %(create_at_start)s::TIMESTAMP AND %(create_at_end)s::TIMESTAMP
                   OR %(create_at_start)s IS NULL OR %(create_at_end)s IS NULL )
                   ORDER BY ddbi.create_at desc
                   OFFSET %(offset)s ROWS FETCH NEXT 10 ROWS ONLY;"""
        ret = self.db.selectSQL(query, {
            'pay_status': pay_status,
            'channel': channel,
            'dt_id': dt_id,
            'create_at_start': create_at_start,
            'create_at_end': create_at_end,
            'offset': offset
        }, fetchone=False)

        if ret:
            ret = [list(i) for i in ret]
            for index in range(0, len(ret)):
                ret[index][1] -= timedelta(days=1)
                ret[index][1] = datetime.strftime(ret[index][1], '%Y-%m-%d')
                ret[index][3], ret[index][5], ret[index][6] = PAY_CHANNEL[ret[index][3]], ret[index][5] / 100, TO_PAY[
                    str(ret[index][6])]
            return ret, ret[0][-1]  # 数据,总数
        return ret, 0
