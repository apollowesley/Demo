# -*- coding: utf-8 -*-
from __future__ import division
import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import BkAdminHandler
from .form import DistributorBalanceList
from uline.public.constants import TO_PAY, PAY_CHANNEL
from datetime import timedelta, datetime
from uline.public.permit import check_permission


class DistributorBalanceListHandler(BkAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        form = DistributorBalanceList(self)
        if not form.validate():
            self.redirect('/bank/balance/dt/list')
        self.dt_daily_balance_no = form.ddb_no.data

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.do_execute()
        self.render('bank/balance/distributorBalanceList.html', data=data)

    def do_execute(self):
        query = """select
                   to_char(ddbi.pay_start_time, 'YYYY-MM-DD HH24:MI:SS'),
                   to_char(ddbi.need_pay_time,'YYYY-MM-DD'),
                   dii.dt_id,
                   ddbi.channel,
                   dii.dt_name,
                   ddbi.rcvAcctName,
                   ddbi.rcvacctno,
                   ddbi.rcvBankName,
                   ddbi.tranAmt,
                   ddbi.pay_status,
                   ddbi.failure_details,
                   bk_user.bk_id,
                   bk_user.bk_name
                   from dt_daily_balance_info as ddbi
                   inner join dt_inlet_info as dii on dii.dt_id = ddbi.dt_id
                   inner join bk_user on bk_user.bk_id = dii.bk_id
                   inner join dt_balance db on db.dt_id = ddbi.dt_id
                   where ddbi.dt_daily_balance_no=%(dt_daily_balance_no)s;"""
        ret = self.db.selectSQL(query, {'dt_daily_balance_no': self.dt_daily_balance_no})
        fields = ['create_at', 'need_pay_time', 'dt_id', 'channel', 'dt_name', 'rcvAcctName', 'balance_account', 'rcvBankName',
                  'tranAmt', 'pay_status', 'failure_details', 'bk_id', 'bk_name']
        dt_info = dict(zip(fields, ret))
        dt_info['tranAmt'], dt_info['pay_status'], dt_info['channel'] = dt_info['tranAmt'] / \
            100, TO_PAY[str(dt_info['pay_status'])], PAY_CHANNEL[str(dt_info['channel'])]

        dt_info['need_pay_time'] = datetime.strptime(dt_info['need_pay_time'], '%Y-%m-%d') - timedelta(days=1)
        dt_info['need_pay_time'] = datetime.strftime(dt_info['need_pay_time'], '%Y-%m-%d')
        # todo 缺少划付状态详情数据表
        return dt_info
