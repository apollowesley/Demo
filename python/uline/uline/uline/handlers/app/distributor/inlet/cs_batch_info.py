# -*- coding: utf-8 -*-
import os
# import decimal
import json
from datetime import date
import itertools
from tornado.web import asynchronous, authenticated
from tornado import gen
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
from xlrd import open_workbook
from copy import deepcopy
from uline.public import log
from uline.public import common
from uline.handlers.baseHandlers import DtAdminHandler
from .form import CSBatchInletInfo, UploadCsInletInfo
from uline.utils.session import thread_db_session
from uline.public.constants import PAY_TYPES, CS_EXCEL, CS_EXCEL_TEMPLATE_PATH
from uline.settings import FEATURE_SWITCH
from uline.utils.chain import chain_utils
from uline.public.permit import check_permission


class CSBatchInletInfoHandler(DtAdminHandler):
    executor = ThreadPoolExecutor(16)

    @authenticated
    @check_permission
    def prepare(self):
        self.open_d0 = FEATURE_SWITCH.get('OPEN_D0')
        self.form = UploadCsInletInfo(self)
        self.uuid = self.form.uuid.data
        if not self.form.validate():
            self.redirect('/dist/inlet/cs')
            return

        self.dt_id = self.current_user
        self.file_path = self.is_exist_file_path(self.uuid)
        self.image_path = self.is_exist_img_path(self.uuid)
        if not os.path.exists(self.file_path) and not os.path.exists(self.image_path):
            self.redirect('/dist/inlet/cs')

    @run_on_executor
    @asynchronous
    @gen.coroutine
    @thread_db_session
    def get(self):
        self.set_secure_cookie('cookie', 'upload')
        inlet_data = yield self.get_inlet_result_info()
        s_rsp = common.scc_rsp(code=200, msg='success', **inlet_data)
        self.write(s_rsp)
        # self.render('distributor/inlet/csInformation.html',
        #             inlet_info=inlet_data)

    @run_on_executor
    @asynchronous
    @gen.coroutine
    @thread_db_session
    def post(self):
        if not self.get_secure_cookie("cookie"):
            self.set_secure_cookie("cookie", "upload")
        inlet_data = yield self.get_inlet_result_info()

        if inlet_data:
            self.render('distributor/inlet/csInformation.html',
                        inlet_info=inlet_data, OPEN_D0=self.open_d0)
            return
        else:
            msg = """
                您的进件模板是旧版，请下载新版的模板，填写后重新上传。
                如使用新模板仍能看到此提示，请联系管理员。
            """
            self.render('common/error_xls_msg.html', error_msg=msg)
            return

    @gen.coroutine
    def get_inlet_result_info(self):
        inlet_data = self.rdb.get(self.uuid)
        dt_wx = yield self.check_dt_wx()
        self.can_wx_app = True if dt_wx else False
        if inlet_data:
            inlet_data = json.loads(inlet_data)
        else:
            mch_info = yield self.read_excel(self.file_path)
            if not mch_info:
                raise gen.Return(mch_info)
            inlet_info = yield self.check_inlet_info(mch_info)
            mch_info_fd = yield self.check_mch_info_format(inlet_info)
            data, total, valid_num = mch_info_fd[0], mch_info_fd[1], mch_info_fd[2]
            status = 0 if valid_num > 0 else 1
            inlet_data = dict(data=data, total=total,
                              valid_num=valid_num, status=status)
            self.rdb.set(self.uuid, json.dumps(inlet_data), 60 * 60)
        raise gen.Return(inlet_data)

    @gen.coroutine
    def check_dt_wx(self):
        query = 'select wx_sub_mch_id from dt_user where dt_id=%s;'
        ret = self.db.selectSQL(query, (self.dt_id,))
        raise gen.Return(ret[0])

    @gen.coroutine
    def check_mch_info_format(self, inlet_info):
        '''
        :param inlet_info:
        :param payment_info:
        :return:
        '''
        inlet_info_data, total, valid_num = list(), len(inlet_info), 0

        for _, inlet_data in enumerate(inlet_info):
            form = CSBatchInletInfo(inlet_data)
            setattr(form, 'dt_id', self.dt_id)
            setattr(form, 'uuid', self.uuid)
            setattr(form, 'father_name', 'chain')
            f_data = deepcopy(form.data)

            if not f_data['cs_id']:
                f_data['cs_id'] = u'连锁商户编号不能为空！'
                self.cs_id = 0
            else:
                cs_ret = self.db.selectSQL("""
                    select 1 from dt_inlet_info where dt_id=%s and parent_id = %s
                """, (f_data['cs_id'], self.dt_id))

                if not cs_ret:
                    f_data['cs_id'] = u'连锁商户不存在'
                    self.cs_id = 0
                else:
                    self.cs_id = f_data['cs_id']
                    sql = """SELECT 1 from auth_dt_info where dt_id=%s and auth_status=2;"""
                    auth_dt = self.db.selectSQL(sql, (self.cs_id,))
                    if not auth_dt:
                        f_data['cs_id'] = u'该连锁商户未通过审核'
                        self.cs_id = 0

            chain_pays = self.db.selectSQL("""
                select payment_type, payment_rate from dt_payment where dt_id=%s;
            """, (self.cs_id,), fetchone=False)

            wx_alipay = self.db.selectSQL("""
                select wx, alipay from d0_withdraw_fee
                where role_type='chain' and role=%s
            """, (self.cs_id,), fetchone=True)

            # 说明开通D0
            if wx_alipay is not None:
                # 方便阅读，转成字典
                ret = {'wx': wx_alipay[0], 'alipay': wx_alipay[1]}
                f_data['wx'] = ret['wx']
                f_data['alipay'] = ret['alipay']

            for pay in chain_pays:
                f_data['checkItem' + str(pay[0])] = pay[1]

            payments = map(lambda x: f_data.get(
                'checkItem' + str(x)), PAY_TYPES)

            if not form.validate() or not any(x != '' and x >= 0 for x in payments):
                f_data['check_status'] = 1
                valid_num += 1
                if not form.validate():
                    for key in form.errors.keys():
                        f_data[key] = form.errors[key][0]
                if not any(x != '' and x >= 0 for x in payments):
                    for key in ['checkItem' + str(x) for x in PAY_TYPES]:
                        if key in ['checkItem4', 'checkItem104']:
                            f_data[key] = u'费率不能全部为空且必须大于等于6'
                        else:
                            f_data[key] = u'费率不能全部为空且必须大于等于0'

            else:
                f_data['check_status'] = 2
            if isinstance(f_data['license_start_date'], date):
                f_data['license_start_date'] = f_data['license_start_date'].strftime(
                    '%Y-%m-%d')
            if isinstance(f_data['license_end_date'], date):
                f_data['license_end_date'] = f_data['license_end_date'].strftime(
                    '%Y-%m-%d')
            if not f_data['license_period']:
                f_data['license_period'] = 1
            if not f_data['dt_sub_id']:
                f_data['dt_sub_id'] = ''

            if str(f_data.get('license_period')) == '1' and f_data['license_end_date'] is None:
                f_data['license_end_date'] = u'必须填写营业证结束时间'
                f_data['check_status'] = 1
                valid_num += 1

            inlet_info_data.append(f_data)

        raise gen.Return([inlet_info_data, total, valid_num])

    @gen.coroutine
    def check_inlet_info(self, mch_info):
        inlet_info = list()
        nrows = mch_info.nrows
        try:
            for row in range(1, nrows):
                _d = mch_info.row_values(row)
                _d = map(lambda x: x.strip() if isinstance(
                    x, basestring) else x, _d)
                # if _d[23] == u'是':
                #     _d[23] = 2
                # elif _d[23] == u'否':
                #     _d[23] = 1
                if _d[24] == u'是':
                    _d[24] = 2
                elif _d[24] == u'否':
                    _d[24] = 1
                inlet_info.append(
                    dict(itertools.izip_longest(CS_EXCEL, _d, fillvalue='')))
            for _, row in enumerate(inlet_info):
                yield self._filter(row, 'id_card_no')
                yield self._filter(row, 'mobile')
                yield self._filter(row, 'service_phone')
                yield self._filter(row, 'bank_no')
                yield self._filter(row, 'balance_account')
            log.exception.info(inlet_info)
        except Exception as err:
            log.exception.info(err)
        raise gen.Return(inlet_info)

    @gen.coroutine
    def _filter(self, row, v):
        if isinstance(row.get(v), float):
            row[v] = int(row[v])

    @gen.coroutine
    def _filter_pay_rate(self, row, v):
        if row.get(v) is not None:
            row[v] = str(row[v])
        else:
            row[v] = ''

    @gen.coroutine
    def read_excel(self, file_path):
        wb = open_workbook(file_path)
        info = None
        try:
            mch_info = wb.sheet_by_index(0)
            # 获取系统进件模板
            wb_template = open_workbook(self.get_excel_template_path())
            info_template = wb_template.sheet_by_index(0)
            # 判断标题是否相同
            if str(mch_info.row(0)) == str(info_template.row(0)):
                info = mch_info
        except Exception as err:
            log.exception.info(err)
        raise gen.Return(info)

    def is_exist_file_path(self, uuid):
        base_dir = os.path.join(self.application.base_dir,
                                'static/uploads/tmp/mch/inlet_excel')
        file_dir = os.path.join(base_dir, '{}'.format(self.current_user))
        file_name = '{}.xls'.format(uuid)
        file_path = os.path.join(file_dir, file_name)
        return file_path

    def get_excel_template_path(self):
        file_path = os.path.join(self.application.base_dir,
                                 CS_EXCEL_TEMPLATE_PATH)
        if os.path.exists(file_path):
            return file_path
        else:
            return False

    def is_exist_img_path(self, uuid):
        base_img_dir = os.path.join(
            self.application.base_dir, 'static/uploads/tmp/mch/idcard/')
        file_dir = os.path.join(base_img_dir, '{}'.format(
            self.current_user), '{}'.format(uuid))
        return file_dir
