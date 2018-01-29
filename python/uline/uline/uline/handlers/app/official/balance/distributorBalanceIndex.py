# -*- coding: utf-8 -*-
from __future__ import division
import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import OfclAdminHandler
from datetime import timedelta, datetime
from .form import DistributorBalanceSearch
from uline.public.constants import TO_PAY, PAY_CHANNEL
from uline.public.permit import check_permission


class DistributorBalanceIndexHandler(OfclAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        self.form = DistributorBalanceSearch(self)
        if not self.form.validate():
            self.redirect('/official/balance/dt')
            return
        pageindex = int(self.get_argument("p", 1))
        self.data, self.total_number = self.db_execute(
            self.form, (pageindex - 1) * 10)

    def get(self):
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('official/balance/distributorBalance.html', navigate_html=navigate_html, data=self.data,
                    form=self.form, total_num=self.total_number, expand_type=0)

    def post(self):
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('official/balance/distributorBalance.html', navigate_html=navigate_html, data=self.data,
                    form=self.form, total_num=self.total_number, expand_type=0)

    def db_execute(self, form, offset):
        """

        :param form:
        :param offset:
        :return:
        """
        create_at_start = form.create_at_start.data or None
        create_at_end = form.create_at_end.data or None
        pay_status = form.pay_status.data or None
        dt_name = form.dt_name.data or None
        channel = form.channel.data or None
        dt_id = form.dt_id.data or None
        balance_account = form.balance_account.data or None
        bk_id = form.bk_id.data or None
        bk_name = form.bk_name.data or None
        expand_type = form.expand_type.data or None

        # 因为end是0时0分,将它续一天┑(￣Д ￣)┍
        if create_at_end:
            create_at_end += timedelta(days=1)

        query = """select
                           to_char(ddbi.pay_start_time, 'YYYY-MM-DD HH24:MI:SS'),
                           ddbi.need_pay_time,
                           dii.dt_name,
                           ddbi.rcvAcctName,
                           ddbi.channel,
                           ddbi.rcvacctno,
                           ddbi.tranAmt,
                           ddbi.pay_status,
                           ddbi.dt_daily_balance_no,
                           count(*) over () as total
                           from dt_daily_balance_info as ddbi
                           inner join dt_inlet_info as dii on dii.dt_id = ddbi.dt_id
                           inner join dt_balance db on db.dt_id = ddbi.dt_id
                           where ddbi.tranamt > 0
                           AND (db.balance_account=%(balance_account)s or %(balance_account)s is null)
                           and (ddbi.pay_status=%(pay_status)s or %(pay_status)s is null)
                           and (ddbi.channel=%(channel)s or %(channel)s is null)
                           and (dii.dt_name ~ E%(dt_name)s or %(dt_name)s = '')

                          AND (dii.bk_id IN (SELECT bk_id FROM bk_user WHERE (bk_type = %(expand_type)s OR %(expand_type)s IS NULL)
                                                    AND  (bk_id::VARCHAR ~ E%(bk_id)s OR %(bk_id)s IS NULL) AND (bk_name ~ E%(bk_name)s OR %(bk_name)s IS NULL) ))

                           and (dii.dt_id::VARCHAR ~ E%(dt_id)s or %(dt_id)s = '')
                           and (ddbi.pay_start_time BETWEEN %(create_at_start)s::TIMESTAMP AND %(create_at_end)s::TIMESTAMP
                           OR %(create_at_start)s IS NULL OR %(create_at_end)s IS NULL )
                           ORDER BY ddbi.create_at desc
                           OFFSET %(offset)s ROWS FETCH NEXT 10 ROWS ONLY;"""
        ret = self.db.selectSQL(query, {
            'pay_status': pay_status,
            'channel': channel,
            'dt_name': self.db.escape(dt_name),
            'dt_id': self.db.escape(dt_id),
            'create_at_start': create_at_start,
            'create_at_end': create_at_end,
            'balance_account': balance_account,
            'expand_type': expand_type,
            'bk_id': self.db.escape(bk_id),
            'bk_name': self.db.escape(bk_name),
            'offset': offset
        }, fetchone=False)

        if ret:
            ret = [list(i) for i in ret]
            for index in range(0, len(ret)):
                ret[index][1] -= timedelta(days=1)
                ret[index][1] = datetime.strftime(ret[index][1], '%Y-%m-%d')
                ret[index][7], ret[index][6], ret[index][4] = TO_PAY[str(ret[index][7])], ret[index][6] / 100, \
                    PAY_CHANNEL[ret[index][4]]
            return ret, ret[0][-1]  # 数据,总数
        return ret, 0
