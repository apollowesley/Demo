# -*- coding: utf-8 -*-
from __future__ import division
import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import MchAdminHandler
from .form import MerchantBalanceList
from uline.public.constants import TO_PAY, PAY_CHANNEL
from datetime import timedelta, datetime
from uline.public.permit import check_permission


class MerchantBalanceIndexListHandler(MchAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        form = MerchantBalanceList(self)
        if not form.validate():
            self.redirect('/merchant/balance/mch/list')
            return
        self.mch_daily_balance_no = form.mdb_no.data

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.do_execute()
        self.render('merchant/balance/merchantBalanceList.html', data=data)

    def do_execute(self):
        mch_id = self.current_user
        query = """select
                   to_char(mdbi.pay_start_time, 'YYYY-MM-DD HH24:MI:SS'),
                   to_char(mdbi.need_pay_time, 'YYYY-MM-DD'),
                   mii.mch_id,
                   mdbi.channel,
                   mii.mch_name,
                   mdbi.rcvAcctName,
                   mdbi.rcvacctno,
                   mdbi.rcvBankName,
                   mdbi.tranAmt,
                   mdbi.pay_status,
                   mdbi.failure_details
                   from mch_daily_balance_info as mdbi
                   inner join mch_inlet_info as mii on mii.mch_id = mdbi.mch_id
                   inner join mch_balance as mb on mb.mch_id = mdbi.mch_id
                   where mii.mch_id=%(mch_id)s
                   and mdbi.mch_daily_balance_no=%(mch_daily_balance_no)s;"""
        ret = self.db.selectSQL(query, {'mch_id': mch_id, 'mch_daily_balance_no': self.mch_daily_balance_no})

        fields = ['create_at', 'need_pay_time', 'mch_id', 'channel', 'mch_name', 'rcvAcctName', 'balance_account', 'rcvBankName', 'tranAmt',
                  'pay_status', 'failure_details']
        mch_info = dict(zip(fields, ret))
        mch_info['tranAmt'] = mch_info['tranAmt'] / 100 if mch_info['tranAmt'] else 0
        mch_info['pay_status'] = TO_PAY[str(mch_info['pay_status'])]
        mch_info['channel'] = PAY_CHANNEL[str(mch_info['channel'])]
        mch_info['need_pay_time'] = datetime.strptime(
            mch_info['need_pay_time'], '%Y-%m-%d') - timedelta(days=1)
        mch_info['need_pay_time'] = datetime.strftime(mch_info['need_pay_time'], '%Y-%m-%d')
        # todo 缺少划付状态详情数据表
        return mch_info
