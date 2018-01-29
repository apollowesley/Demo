# -*- coding: utf-8 -*-
import itertools
# import decimal
import json
import os
from copy import deepcopy
from datetime import date

from concurrent.futures import ThreadPoolExecutor
from tornado import gen
from tornado.concurrent import run_on_executor
from tornado.web import asynchronous, authenticated
from xlrd import open_workbook

from uline.handlers.baseHandlers import DtAdminHandler
from uline.public import common
from uline.public import log
from uline.public.constants import (PAY_TYPES, MCH_EXCEL, EXCEL_TEMPLATE_PATH, DINNER_TOGGETHER_PAY_TYPES,
                                    OFFLINE_D0_WX_PAY_TYPES, OFFLINE_D1_WX_PAY_TYPES, ONLINE_D0_WX_PAY_TYPES,
                                    ONLINE_D1_WX_PAY_TYPES, D1_ALI_PAY_TYPES, D1_WX_PAY_TYPES, WX_PAY_TYPES
)
from uline.settings import FEATURE_SWITCH
from uline.utils.dayzero import form_verify
from uline.utils.session import thread_db_session
from .form import MerchantBatchInletInfo, UploadMerchantInletInfo
from uline.public.permit import check_permission


class MerchantBatchInletInfoHandler(DtAdminHandler):
    executor = ThreadPoolExecutor(16)

    @authenticated
    @check_permission
    def prepare(self):
        self.open_d0 = FEATURE_SWITCH.get('OPEN_D0')
        self.form = UploadMerchantInletInfo(self)
        self.uuid = self.form.uuid.data
        if not self.form.validate():
            self.redirect('/dist/inlet/mch')
            return

        self.dt_id = self.current_user
        self.file_path = self.is_exist_file_path(self.uuid)
        self.image_path = self.is_exist_img_path(self.uuid)
        if not os.path.exists(self.file_path) and not os.path.exists(
                self.image_path):
            self.redirect('/dist/inlet/mch')

    def generate_unchanged_render_params(self):
        return {
            'use_dine': FEATURE_SWITCH.get('DINE_TOGETHER', False)
        }

    @run_on_executor
    @asynchronous
    @gen.coroutine
    @thread_db_session
    def get(self):
        self.set_secure_cookie('cookie', 'upload')
        inlet_data = yield self.get_inlet_result_info()
        s_rsp = common.scc_rsp(code=200, msg='success', **inlet_data)
        self.write(s_rsp)
        # self.render('distributor/inlet/merchantInformation.html',
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
            self.render('distributor/inlet/merchantInformation.html',
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
            inlet_data = dict(data=data, total=total, valid_num=valid_num, status=status)
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
        dt_has_dine = bool(self.has_dine_payments())

        for _, inlet_data in enumerate(inlet_info):
            fee_flag = True

            form = MerchantBatchInletInfo(inlet_data)
            setattr(form, 'dt_id', self.dt_id)
            setattr(form, 'uuid', self.uuid)
            setattr(form, 'father_name', 'dt')
            f_data = deepcopy(form.data)

            if not form.validate():
                f_data['check_status'] = 1
                fee_flag = False
                for key in form.errors.keys():
                    f_data[key] = form.errors[key][0]

            # 验证用户填写信息的合法性
            wx_pay = inlet_data.get('wx_pay')
            ali_pay = inlet_data.get('ali_pay')
            d0_wx_pay = inlet_data.get('d0_wx_pay')
            d0_ali_pay = inlet_data.get('d0_ali_pay')
            use_dine = str(inlet_data.get('use_dine', '1'))

            if wx_pay or ali_pay:
                if wx_pay:
                    # 围餐支付方式
                    if use_dine == '2':
                        if d0_wx_pay:
                            f_data['use_dine'] = u'围餐和微信D0不能同时开通'
                            fee_flag = False
                        else:
                            for each_type in WX_PAY_TYPES:
                                f_data['payment_type' + str(each_type)] = ''
                            for each_type in OFFLINE_D1_WX_PAY_TYPES:
                                f_data['payment_type' + str(each_type)] = '0'
                            f_data['wx'] = None
                            if not inlet_data.get('mch_front_img'):
                                f_data['mch_front_img'] = u'围餐商户必填信息'
                                fee_flag = False
                            if not inlet_data.get('mch_desk_img'):
                                f_data['mch_desk_img'] = u'围餐商户必填信息'
                                fee_flag = False
                            if not inlet_data.get('mch_inner_img'):
                                f_data['mch_inner_img'] = u'围餐商户必填信息'
                                fee_flag = False
                            if not dt_has_dine:
                                f_data['use_dine'] = u'渠道商未开通围餐'
                                fee_flag = False
                    else:
                        # 判断微信费率是否符合标准
                        wx_pays_status = self.check_rate_is_null(inlet_data, 'payment_type', D1_WX_PAY_TYPES)
                        if wx_pays_status:
                            fee_flag = False
                            for pt in D1_WX_PAY_TYPES:
                                f_data['payment_type' + str(pt)] = u'微信费率不能全部为空'

                        # 判断微信D0提现手续费是否符合标准
                        if d0_wx_pay and self.open_d0:
                            fee_status, fee_message = form_verify.check_d0_withdraw_fee(inlet_data.get('wx'), self.dt_id, 'weixin')
                            if not fee_status:
                                f_data['wx'] = fee_message
                                fee_flag = False
                        else:
                            f_data['wx'] = None
                else:
                    # 清空微信费率
                    for wx_type in D1_WX_PAY_TYPES:
                        f_data['payment_type' + str(wx_type)] = ''

                    if use_dine == '2':
                        fee_flag = False
                        f_data['wx'] = None
                        f_data['d0_wx_pay'] = False
                        f_data['wx_pay'] = u'请先开通微信支付'
                    else:
                        # 清空微信围餐费率
                        for wx_dine_type in DINNER_TOGGETHER_PAY_TYPES:
                            f_data['payment_type' + str(wx_dine_type)] = ''

                        f_data['wx'] = None
                        f_data['d0_wx_pay'] = False
                        f_data['use_dine'] = '否'

                if ali_pay:
                    # 判断支付宝费率是否符合标准
                    ali_pays_status = self.check_rate_is_null(inlet_data, 'payment_type', D1_ALI_PAY_TYPES)
                    if ali_pays_status:
                        fee_flag = False
                        for pt in D1_ALI_PAY_TYPES:
                            f_data['payment_type' + str(pt)] = u'支付宝费率不能全部为空'

                    # 判断支付宝D0提现手续费是否符合标准
                    if d0_ali_pay and self.open_d0:
                        fee_status, fee_message = form_verify.check_d0_withdraw_fee(inlet_data.get('alipay'),
                                                                                    self.dt_id, 'alipay')
                        if not fee_status:
                            f_data['alipay'] = fee_message
                            fee_flag = False
                    else:
                        f_data['alipay'] = None
                else:
                    for ali_type in D1_ALI_PAY_TYPES:
                        f_data['payment_type' + str(ali_type)] = ''
                    f_data['alipay'] = None
                    f_data['d0_ali_pay'] = False
            else:
                f_data['wx_pay'] = u'至少开通一种支付渠道'
                f_data['ali_pay'] = u'至少开通一种支付渠道'
                fee_flag = False

            # 验证微信费率是否符合标准
            for pay_type in D1_WX_PAY_TYPES:
                if d0_wx_pay:
                    d0_status = True
                else:
                    d0_status = False
                status, error_message = self._filter_pay_rate(
                    inlet_data, pay_type, d0_status
                )
                if not status:
                    f_data['payment_type' + str(pay_type)] = error_message
                    fee_flag = False

            # 验证支付宝费率是否符合标准
            for pay_type in D1_ALI_PAY_TYPES:
                if d0_ali_pay:
                    d0_status = True
                else:
                    d0_status = False
                status, error_message = self._filter_pay_rate(
                    inlet_data, pay_type, d0_status
                )
                if not status:
                    f_data['payment_type' + str(pay_type)] = error_message
                    fee_flag = False

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
                fee_flag = False

            # 围餐支付方式
            if f_data.get('use_dine', '1') == '2':
                if not form.mch_front_img.data:
                    fee_flag = False
                    f_data['mch_front_img'] = u'门店门口照片必填'
                if not form.mch_desk_img.data:
                    fee_flag = False
                    f_data['mch_desk_img'] = u'收银台照片必填'
                if not form.mch_inner_img.data:
                    fee_flag = False
                    f_data['mch_inner_img'] = u'店内环境照片必填'
                has_dine_annex_img = False
                for each_index in range(1, 6):
                    if getattr(getattr(form, 'wx_dine_annex_img' + str(each_index)), 'data'):
                        has_dine_annex_img = True
                        break
                if not has_dine_annex_img:
                    fee_flag = False
                    f_data['wx_dine_annex_img1'] = u'围餐补充材料必填'


            if not fee_flag:
                f_data['check_status'] = 1
                valid_num += 1
            else:
                f_data['check_status'] = 2

            inlet_info_data.append(f_data)

        raise gen.Return([inlet_info_data, total, valid_num])

    def check_rate_is_null(self, inlet_data, key, pays):
        """
        判断某几个费率是否全部为空
        :param inlet_data: 存放费率key value对应关系的字典
        :param key: 获取字典的前缀，如：payment_type
        :param pays: 获取字典的后缀，接收的是一个数组，如 [1,2,3,4]
        :return: True 代表全部为空， False代表有不为空的
        """
        payments = map(lambda x: inlet_data.get(key + str(x)), pays)
        if not any(form_verify.check_fee_is_correct(x) for x in payments):
            return True
        else:
            return False

    @gen.coroutine
    def check_inlet_info(self, mch_info):
        inlet_info = list()
        nrows = mch_info.nrows
        try:
            for row in range(1, nrows):
                _d = mch_info.row_values(row)
                _d = map(lambda x: x.strip() if isinstance(x, basestring) else x, _d)

                """
                    有些用户给Excel设置各种数据类型
                    导致各种奇葩问题
                    全部转换成str类型
                """
                for i in range(len(_d)):
                    if not isinstance(_d[i], str):
                        _d[i] = str(_d[i])
                # 转换成字典，使用字典操作
                _d = dict(itertools.izip_longest(MCH_EXCEL, _d, fillvalue=''))

                # 转换用户填写的数据，只判断填写 是 的，其他均为 否

                # 营业执照是否长期有效(是 / 否), 非长期 1  长期 2
                _d['license_period'] = 2 if _d.get('license_period') == u'是' else 1

                # 是否开通微信支付
                _d['wx_pay'] = True if _d.get('wx_pay') == u'是' else False

                # 是否开通D0微信支付
                _d['d0_wx_pay'] = True if _d.get('d0_wx_pay') == u'是' else False

                # 是否开通支付宝支付
                _d['ali_pay'] = True if _d.get('ali_pay') == u'是' else False

                # 是否开通D0支付宝支付
                _d['d0_ali_pay'] = True if _d.get('d0_ali_pay') == u'是' else False

                # 是否开通围餐支付
                _d['use_dine'] = True if _d.get('use_dine') == u'是' else False

                # 如果开通围餐
                if _d['use_dine']:
                    _d['use_dine'] = 2

                    wx_pays = OFFLINE_D0_WX_PAY_TYPES + OFFLINE_D1_WX_PAY_TYPES + ONLINE_D0_WX_PAY_TYPES + ONLINE_D1_WX_PAY_TYPES
                    for each_type in wx_pays:
                        _d['payment_type' + str(each_type)] = ''
                else:
                    _d['use_dine'] = 1

                inlet_info.append(_d)

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

    def _filter_pay_rate(self, inlet_data, pay_type, d0_status):
        pay_key = 'payment_type' + str(pay_type)
        use_dine = False
        if str(inlet_data.get('use_dine')) == '2':
            use_dine = True
        # 判断传进来的费率，是不是有效的数值，如果不是就原样返回不作处理
        if form_verify.check_fee_is_correct(inlet_data.get(pay_key)):
            # 围餐开通状态，并且费率属于微信的费率
            if use_dine and (pay_type in OFFLINE_D1_WX_PAY_TYPES):
                pay_type += 10
            elif d0_status:
                pay_type += 100

            return form_verify.validate_one_payment_rate(
                pay_type, inlet_data[pay_key], self.dt_id
            )
        else:
            if inlet_data.get(pay_key) in ["", None]:
                return True, inlet_data.get(pay_key)
            else:
                return False, inlet_data.get(pay_key)

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
        file_dir = os.path.join(base_dir, '{}'.format(self.dt_id))
        file_name = '{}.xls'.format(uuid)
        file_path = os.path.join(file_dir, file_name)
        return file_path

    def get_excel_template_path(self):
        file_path = os.path.join(self.application.base_dir, EXCEL_TEMPLATE_PATH)
        if os.path.exists(file_path):
            return file_path
        else:
            return False

    def is_exist_img_path(self, uuid):
        base_img_dir = os.path.join(
            self.application.base_dir, 'static/uploads/tmp/mch/idcard/')
        file_dir = os.path.join(base_img_dir, '{}'.format(
            self.dt_id), '{}'.format(uuid))
        return file_dir

    def has_dine_payments(self):
        sql = """select 1 from dt_payment where dt_id=%s and payment_type in (11, 12, 13)"""
        return self.db.selectSQL(sql, (self.current_user,))
