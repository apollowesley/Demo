from concurrent.futures import ThreadPoolExecutor
from tornado.web import authenticated, asynchronous, HTTPError
from tornado import gen
from uline.public import common, log
from uline.handlers.app.distributor.inlet.form import GetMerchanInfo, GetMerchanPayCallbackUrl
from uline.handlers.baseHandlers import DtAdminHandler
from uline.public.permit import check_permission

__author__ = 'apple'


class SetCallbackUrlHandler(DtAdminHandler):
    executor = ThreadPoolExecutor(8)

    @authenticated
    @check_permission
    def prepare(self):
        if self.request.method == 'POST':
            self.form = GetMerchanPayCallbackUrl(self)
        else:
            self.form = GetMerchanInfo(self)
        setattr(self.form, 'dt_id', self.current_user)
        if not self.form.validate():
            f_rsp = common.f_rsp(code=406, msg='fail')
            self.finish(f_rsp)
        self.mch_id = self.form.mch_id.data

    @gen.coroutine
    def get(self):
        data = yield self.get_mch_callback_url()
        s_rsp = common.scc_rsp(code=200, msg='success', **data)
        self.write(s_rsp)

    @gen.coroutine
    def get_mch_callback_url(self):
        query = """select pay_notify_url from mch_inlet_info where mch_id=%s """
        ret = self.db.selectSQL(query, (self.mch_id,), fetchone=True)
        data = {'pay_notify_url': ret[0] if ret else None}
        raise gen.Return(data)

    @asynchronous
    @gen.coroutine
    def post(self):
        self.pay_notify_url = self.form.pay_notify_url.data
        # self.pay_notify_url = 'http://www.epub3434.com/adf/123/'
        self.dt_id = self.get_current_user()

        with self.db.get_db() as cur:
            yield self.update_mch_callback_url(cur)
            # yield self.update_mch_callback_url(cur)
        data = {'pay_notify_url': self.pay_notify_url}
        s_rsp = common.scc_rsp(code=200, msg='success', **data)
        self.write(s_rsp)
        # self.redirect('/dist/inlet/mch')

    @gen.coroutine
    def update_mch_callback_url(self, cursor):
        query = """update mch_inlet_info set
                   pay_notify_url=%(pay_notify_url)s
                   where mch_id=%(mch_id)s and dt_id=%(dt_id)s;"""
        cursor.execute(
            query, {
                'pay_notify_url': self.pay_notify_url,
                'mch_id': self.mch_id,
                'dt_id': self.dt_id
            }
        )
