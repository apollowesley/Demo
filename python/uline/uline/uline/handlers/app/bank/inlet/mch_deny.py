# -*- coding: utf-8 -*-
'''
BEGIN
ajax请求 审核/驳回商户进件信息
    必选参数:

    可选参数:

    成功:
        {"code": 200, "msg": "成功"}
    失败:
        {"code": 406, "msg": "失败"}
END
'''
import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import BkAdminHandler
from uline.public import common, constants
from .form import DenyMerchantInfo
from uline.backend.tasks import callback_for_merchant_status
from uline.utils.record import record_utils
from uline.public.common import gen_randown_mch_pkey
from uline.settings import FEATURE_SWITCH
from uline.public.permit import check_permission


class DenyMerchantInletStatusHandler(BkAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        form = DenyMerchantInfo(self)
        if not form.validate():
            f_rsp = common.f_rsp(code=406, msg='fail')
            self.finish(f_rsp)
        self.mch_id = form.mch_id.data
        self.comment = form.comment.data
        self.status = 3
        self.create_at = self.update_at = common.timestamp_now()
        self.open_review = FEATURE_SWITCH['REVIEW']

    # 商户进件驳回
    @tornado.gen.coroutine
    def get(self):
        rsp = common.scc_rsp(code=200, msg='success')
        with self.db.get_db() as cur:
            try:
                # 如果需要多次审核
                if self.open_review:
                    latest_auth_status = self.get_latest_auth_info(cur)
                    # 如果获取的最近一次审核记录为审核通过
                    if latest_auth_status == constants.AUTH_STATUS_SUBMIT:
                        self.status = constants.AUTH_STATUS_FIRST_DENY
                self.auth_mch_inlet(cur)
                self.add_auth_inlet_info(cur)
                # yield record_utils.rollback_mch_payments(self, self.mch_id, change_type=2)
                yield record_utils.rollback(self, change_type=2)
            except Exception as err:
                cur.connection.rollback()
                rsp = common.f_rsp(code=406, msg='fail')

        if rsp['msg'] == 'success' and rsp['code'] == 200:
            # 银行驳回商户进件的请求，恢复为渠道商申请前的数据
            message_id = gen_randown_mch_pkey(8)
            callback_for_merchant_status.apply_async((self.mch_id, 1, message_id), )
        self.write(rsp)

    def auth_mch_inlet(self, cursor):

        # activated_status = 1 if self.status in [1, 3] else 2
        query = """update mch_inlet_info set
            auth_status=%(auth_status)s, update_at=%(update_at)s where mch_id=%(mch_id)s"""
        cursor.execute(query, {
            'auth_status': self.status,
            'update_at': self.update_at,
            'mch_id': self.mch_id
        })

    def add_auth_inlet_info(self, cursor):
        auth_user = self.get_bk_email(cursor)
        query = """
            insert into auth_mch_info (mch_id, comment, auth_user, auth_status, create_at)
            values (%s, %s, %s, %s, %s);"""
        cursor.execute(query, (self.mch_id, self.comment, auth_user, self.status, self.create_at))

    def get_bk_email(self, cursor):
        query = """select email from bk_user where bk_id=%s"""
        cursor.execute(query, (self.current_user,))
        ret = cursor.fetchone()
        return ret[0]

    def get_latest_auth_info(self, cursor):
        query = """select auth_status from auth_mch_info WHERE mch_id=%s and auth_status in %s order by id DESC limit 1"""
        cursor.execute(query, (self.mch_id,(constants.AUTH_STATUS_SUBMIT,constants.AUTH_STATUS_PREVIEWD)))
        result = cursor.fetchone()
        return result[0] if result else constants.AUTH_STATUS_SUBMIT
