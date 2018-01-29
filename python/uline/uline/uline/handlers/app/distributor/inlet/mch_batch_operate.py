# -*- coding: utf-8 -*-
import json
import shutil
import uuid
from multiprocessing import cpu_count
from sqlalchemy.sql import func
import datetime

from uline.model.uline.other import SysType
from uline.model.uline.base import uline_session
from uline.model.uline.permit import Role, EmployeeRolePermit
from uline.model.uline.info import EmployeeUserLog, UserProfile
from uline.model.uline.user import Employee

import os
from concurrent.futures import ThreadPoolExecutor
from tornado import gen
from tornado.concurrent import run_on_executor
from tornado.web import authenticated, asynchronous

from uline.handlers.baseHandlers import DtAdminHandler
from uline.public import common
from uline.public import log
from uline.public.constants import D1_WX_PAY_TYPES, D1_ALI_PAY_TYPES, D1_PAY_TYPES, translate_payment_type
from .form import UploadMerchantInletInfo
from uline.utils.dayzero import form_verify
from uline.public.permit import check_permission
from uline.settings import FEATURE_SWITCH

thread_num = cpu_count()


class MerchantBatchInletOperateHandler(DtAdminHandler):
    executor = ThreadPoolExecutor(thread_num)

    @authenticated
    @check_permission
    def prepare(self):
        self.form = UploadMerchantInletInfo(self)
        if not self.form.validate():
            self.write({'msg': 'fail', 'code': 406})
            self.finish()
        self.uuid = self.form.uuid.data
        self.dt_id = self.current_user
        self.create_at = common.timestamp_now()

    @run_on_executor
    @asynchronous
    @gen.coroutine
    def get(self):
        # (同业银行版本添加)判断所属银行
        bk_info = self.get_bank_for_dt(self.dt_id)
        if not bk_info:
            self.write({'msg': 'fail', 'code': 406})
            return
        self.bank_id = bk_info[2]

        self.set_secure_cookie('cookie', 'upload')
        inlet_info = self.rdb.get(self.uuid)
        if not inlet_info:
            self.write({'msg': 'fail', 'code': 406})
            self.finish()
            return
        inlet_info = json.loads(inlet_info)
        inlet_data = inlet_info.get('data')
        inlet_result = list()

        self.dt_name = yield self.get_dt_name()

        try:
            for index, data in enumerate(inlet_data):
                if data['check_status'] in [2, '2']:
                    self.mch_id = common.create_mch_id()
                    self.mch_name = data.get('mch_name')
                    self.mchShortName = data.get('mch_shortname')
                    self.industry_code = data.get('industry_code')
                    self.province = data.get('province')
                    self.city = data.get('city')
                    self.district = data.get('district')
                    self.address = data.get('address')
                    self.servicePhone = data.get('service_phone')
                    self.contact = data.get('contact')
                    self.mobile = data.get('mobile')
                    self.email = data.get('email')
                    self.balance_type = yield self.get_balance_type(
                        data.get('balance_type'))
                    self.balance_name = data.get('balance_name')
                    self.balance_account = data.get('balance_account')
                    self.id_card_no = data.get('id_card_no')
                    self.id_card_img_f = data.get('id_card_img_f')
                    self.id_card_img_b = data.get('id_card_img_b')
                    self.bank_no = data.get('bank_no')
                    self.auth_status = 1
                    self.activated_status = 1

                    self.license_num = data.get('license_num')
                    self.license_start_date = data.get('license_start_date')
                    self.license_end_date = data.get('license_end_date')
                    self.license_period = data.get('license_period')
                    self.license_scope = data.get('license_scope')
                    self.license_img = data.get('license_img')

                    id_card_path = yield self.save_idCard_img()
                    self.id_card_img_f = id_card_path[0]
                    self.id_card_img_b = id_card_path[1]
                    self.license_img = id_card_path[2]

                    # 围餐图片存储
                    if data.get('use_dine', '') == '2':
                        yield self.save_mch_extensions(data)

                    # 初始化变量
                    self.annex_img1 = None
                    self.annex_img2 = None
                    self.annex_img3 = None
                    self.annex_img4 = None
                    self.annex_img5 = None

                    # 进件补充材料图片存储
                    yield self.save_mch_annex_img(data)

                    # 默认使用，不能修改
                    self.wx_use_parent = 1
                    self.dt_sub_id = data.get('dt_sub_id')
                    if not self.dt_sub_id:
                        self.dt_sub_id = None

                    # 先进行提现手续费的处理和保存
                    if data.get('d0_wx_pay') != 'True' and data.get('d0_wx_pay') != True:
                        data['wx'] = None

                    if data.get('d0_ali_pay') != 'True' and data.get('d0_ali_pay') != True:
                        data['alipay'] = None

                    if not form_verify.check_fee_is_correct(data.get('alipay')):
                        data['alipay'] = None
                    else:
                        data['alipay'] = float(data['alipay'])

                    if not form_verify.check_fee_is_correct(data.get('wx')):
                        data['wx'] = None
                    else:
                        data['wx'] = float(data['wx'])

                    if data.get('alipay') is not None or data.get('wx') is not None:
                        yield self.save_d0_withdraw_fee(data)

                    yield self.add_mch_user()
                    yield self.save_inlet_info()
                    yield self.save_mch_balance()
                    yield self.save_mch_payment(data)
                    yield self.add_auth_inlet_info()
                    self.update_employee_profile()
                    data['inlet_status'] = 2
                    inlet_result.append(data)
        except Exception as err:
            log.exception.exception(err)
            self.write({'msg': 'fail', 'code': 407, 'data': inlet_result})
            self.finish()
            return

        self.write({'msg': 'success', 'code': 200, 'data': inlet_result})

    @gen.coroutine
    def get_balance_type(self, balance_type):
        _d = {u'企业': 1, u'个人': 2}
        raise gen.Return(_d[balance_type])

    @gen.coroutine
    def save_idCard_img(self):
        # 不需要根据环境判断存入目录
        base_dir = os.path.join(
            self.application.base_dir, 'static/uploads/mch/idcard')
        file_dir = os.path.join(base_dir, '{}'.format(self.mch_id))

        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        base_tmp_dir = os.path.join(
            self.application.base_dir, 'static/uploads/tmp/mch/idcard')
        filr_base_dir = os.path.join(
            base_tmp_dir,
            '{}'.format(self.current_user),
            '{}'.format(self.uuid)
        )

        file_tmp_f_name = str(os.path.join(filr_base_dir, self.id_card_img_f))
        file_tmp_b_name = str(os.path.join(filr_base_dir, self.id_card_img_b))
        file_tmp_license_name = str(
            os.path.join(filr_base_dir, self.license_img))

        file_f_name = '{}.jpg'.format(uuid.uuid4().hex)
        file_b_name = '{}.jpg'.format(uuid.uuid4().hex)
        file_license_name = '{}.jpg'.format(uuid.uuid4().hex)
        img_f_path = str(os.path.join(file_dir, file_f_name))
        img_b_path = str(os.path.join(file_dir, file_b_name))
        img_license_path = str(os.path.join(file_dir, file_license_name))

        try:
            shutil.copy(file_tmp_f_name, img_f_path)
            shutil.copy(file_tmp_b_name, img_b_path)
            shutil.copy(file_tmp_license_name, img_license_path)
        except Exception as err:
            log.exception.info(err)
        raise gen.Return([file_f_name, file_b_name, file_license_name])

    @gen.coroutine
    def get_dt_name(self):
        query = """select dt_name from dt_user where dt_id=%s;"""
        ret = self.db.selectSQL(query, (self.dt_id,))
        raise gen.Return(ret[0])

    @gen.coroutine
    def get_wx_ali_ind_code(self):
        query = """select wx_ind_code,
        new_ali_ind_code, jd_ind_code from industry_uline_info where industry_code=%s;"""
        ret = self.db.selectSQL(query, (self.industry_code,))
        raise gen.Return(ret)

    @gen.coroutine
    def add_mch_user(self):
        # 新建一个商户,默认密码123456
        self._password = common.bcrypt_pwd_new(str(self.mobile))
        status = 1  # 创建
        create_at = update_at = common.timestamp_now()

        if self.wx_use_parent in [2, '2']:
            mch_pay_key = yield self.get_dt_wx_pay_info()
        else:
            mch_pay_key = common.gen_randown_mch_pkey(32)

        query = """
          INSERT INTO mch_user(
          mch_id, mch_name, email, password,
          status, create_at, update_at, wx_use_parent, mch_pay_key)
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"""

        self.db.executeSQL(
            query,
            (
                self.mch_id, self.mch_name, self.email, self._password,
                status, create_at, update_at, self.wx_use_parent,
                mch_pay_key
            )
        )

    @gen.coroutine
    def get_dt_wx_pay_info(self):
        query = """select mch_pay_key from dt_user where dt_id=%s;"""
        ret = self.db.selectSQL(query, (self.current_user,))
        raise gen.Return(ret[0])

    @gen.coroutine
    def save_inlet_info(self):
        # 添加的商户的基本信息,下一步保存支付信息
        auth_status = 1
        activated_status = 1
        province = self.province
        city = self.city
        create_at = update_at = common.timestamp_now()

        ret_code = yield self.get_wx_ali_ind_code()
        wx_ind_code, ali_ind_code, jd_ind_code = ret_code[0], ret_code[1], ret_code[2]

        self.db.executeSQL(
            """
            INSERT INTO mch_inlet_info (
            mch_name, mch_shortname, dt_id, province, city, district,address,
            contact, mobile, service_phone, email,
            id_card_img_f, id_card_img_b,
            auth_status, activated_status, mch_id, u_ind_code,
            wx_ind_code, ali_ind_code, jd_ind_code, create_at, update_at,
            license_num, license_start_date, license_end_date,
            license_period, license_scope, license_img, dt_sub_id,
            annex_img1,annex_img2,annex_img3,annex_img4,annex_img5,bk_id
            ) VALUES (
            %s, %s, %s,%s,
            %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s,%s,
            %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s, %s,%s
            )""",
            (
                self.mch_name, self.mchShortName, self.dt_id,
                province, city, self.district, self.address,
                self.contact, self.mobile, self.servicePhone, self.email,
                self.id_card_img_f, self.id_card_img_b,
                auth_status, activated_status, self.mch_id, self.industry_code,
                wx_ind_code, ali_ind_code, jd_ind_code, create_at, update_at,
                self.license_num, self.license_start_date, self.license_end_date,
                self.license_period, self.license_scope, self.license_img, self.dt_sub_id,
                self.annex_img1, self.annex_img2, self.annex_img3, self.annex_img4, self.annex_img5,
                self.bank_id
            )
        )

    @gen.coroutine
    def save_mch_balance(self):
        # 商户结算账户表(mch_balance)
        # 商户支付方式表(mch_payment)
        create_at = update_at = common.timestamp_now()
        self.db.executeSQL(
            """
            INSERT INTO mch_balance(
            mch_id, balance_way, balance_type, balance_name,
            bank_no, balance_account, id_card_no,
            create_at, update_at)
            VALUES (
            %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s);""",
            (
                self.mch_id, 1, self.balance_type, self.balance_name,
                self.bank_no, self.balance_account, self.id_card_no,
                create_at, update_at
            )
        )

    @gen.coroutine
    def save_d0_withdraw_fee(self, data):
        # 数据库只能存int
        wx = data.get('wx') * 100 if data.get('wx') else data.get('wx')
        alipay = data.get('alipay') * 100 if data.get('alipay') else data.get('alipay')
        if isinstance(wx, float):
            wx = int(wx)

        if isinstance(alipay, float):
            alipay = int(alipay)
        query = """insert into d0_withdraw_fee(role, role_type, wx, alipay) values(%s,%s,%s,%s)"""
        self.db.executeSQL(query, (self.mch_id, 'mch', wx, alipay))

    @gen.coroutine
    def save_mch_payment(self, data):
        # 支持多种支付类型 万分率
        # 转变成[[payment_type,payment_rate]] for循环
        create_at = update_at = common.timestamp_now()

        wx = data.get('wx') * 100 if data.get('wx') else data.get('wx')
        alipay = data.get('alipay') * 100 if data.get('alipay') else data.get('alipay')
        if isinstance(wx, float):
            wx = int(wx)
        if isinstance(alipay, float):
            alipay = int(alipay)

        for payment_type in D1_PAY_TYPES:
            payment_rate = data.get('payment_type' + str(payment_type))
            if payment_rate:
                data['payment_type'] = payment_type
                payment_rate = int(float(payment_rate) * 10)
                log.exception.exception('payment_rate:%s' % payment_rate)
                db_pay_type = None
                if payment_type in D1_WX_PAY_TYPES:
                    if data.get('wx') is not None:
                        db_pay_type = payment_type + 100
                    elif data.get('use_dine') == '2':
                        db_pay_type = payment_type + 10
                    else:
                        db_pay_type = payment_type

                if payment_type in D1_ALI_PAY_TYPES:
                    if data.get('alipay') is not None:
                        db_pay_type = payment_type + 100
                    else:
                        db_pay_type = payment_type

                if db_pay_type is not None:
                    tmp_str = translate_payment_type.get(payment_type)
                    if tmp_str:
                        uline_payment_id, uline_settle_id, trade_type,\
                            thirdparty_mch_id, uline_payment_code = tmp_str.split('|')
                        data['uline_payment_id'] = uline_payment_id
                        data['uline_settle_id'] = uline_settle_id
                        data['trade_type'] = trade_type
                        data['thirdparty_mch_id'] = thirdparty_mch_id
                        data['uline_payment_code'] = uline_payment_code

                        # 添加手续费和垫资费
                        if uline_payment_code.find('WX') != -1 and data.get('wx') is not None:
                            data['withdraw_fee'] = wx
                            if FEATURE_SWITCH.get('NEW_INLET'):
                                if data.get('wx') is not None:
                                    withdraw_rate = self.get_dt_withdraw_rate('WX')
                                    if withdraw_rate:
                                        data['withdraw_rate'] = withdraw_rate
                        if uline_payment_code.find('ALI') != -1 and data.get('alipay') is not None:
                            data['withdraw_fee'] = alipay
                            if FEATURE_SWITCH.get('NEW_INLET'):
                                if data.get('alipay') is not None:
                                    withdraw_rate = self.get_dt_withdraw_rate('ALI')
                                    if withdraw_rate:
                                        data['withdraw_rate'] = withdraw_rate
                        # paymnet_type减去100
                        if FEATURE_SWITCH.get('NEW_INLET') and data.get('withdraw_rate'):
                            if data.get('payment_type') > 100:
                                data['payment_type'] -= 100
                            payment_rate -= data['withdraw_rate']

                    if data.get('withdraw_fee') and data.get('withdraw_rate'):
                        self.db.executeSQL("""
                        INSERT INTO mch_payment(
                    mch_id, dt_id, settle_rate, uline_payment_id, uline_payment_code, uline_settle_id, trade_type,
                    payment_type, payment_rate, withdraw_rate, withdraw_fee, activated_status, create_at, update_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                                           (self.mch_id, str(self.dt_id), payment_rate, data.get('uline_payment_id'),
                                            data.get('uline_payment_code'), uline_settle_id,
                                            data.get('trade_type'), data.get('payment_type'),
                                            payment_rate, data.get(
                                                'withdraw_rate'), data.get('withdraw_fee'), 1,
                                            create_at, update_at))
                    else:
                        self.db.executeSQL("""
                        INSERT INTO mch_payment(
                    mch_id, dt_id, settle_rate, uline_payment_id, uline_payment_code, uline_settle_id, trade_type,
                    payment_type, payment_rate, activated_status, create_at, update_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                                           (self.mch_id, str(self.dt_id), payment_rate, data.get('uline_payment_id'),
                                            data.get('uline_payment_code'), uline_settle_id,
                                            data.get('trade_type'), data.get('payment_type'),
                                            payment_rate, 1,
                                            create_at, update_at))

                    # self.db.executeSQL(
                    #     """
                    #     INSERT INTO mch_payment(
                    #     mch_id, payment_type, payment_rate,
                    #     activated_status, create_at, update_at)
                    #     VALUES (
                    #     %s, %s, %s,
                    #     %s, %s, %s);
                    #     """,
                    #     (
                    #         self.mch_id, db_pay_type, float(payment_rate) * 10,
                    #         1, create_at, update_at
                    #     )
                    # )

    def get_dt_withdraw_rate(self, type):
        log.detail.info('##############type:%s | dt_id:%s' % (type, self.dt_id))
        if type == 'WX':
            log.detail.info('WX')
            query = """select withdraw_rate from dt_payment where dt_id=%s and uline_payment_code
                        LIKE %s and payment_type in (1, 2, 3);"""
            ret = self.db.selectSQL(query, (self.dt_id, 'WX_OFFLINE%'))
        else:
            query = """select withdraw_rate from dt_payment where dt_id=%s and uline_payment_code
                        LIKE %s and payment_type in (7, 8, 9);"""
            ret = self.db.selectSQL(query, (self.dt_id, 'ALI_OFFLINE%'))
        log.detail.info('query:%s' % query)
        log.detail.info('##############ret:%s | dt_id:%s' % (ret, self.dt_id))
        if ret is not None:
            try:
                return ret[0]
            except:
                return None
        else:
            return None

    @gen.coroutine
    def add_auth_inlet_info(self):
        auth_user = yield self.get_dt_user()
        create_at = common.timestamp_now()
        query = """
            insert into auth_mch_info (
            mch_id, comment, auth_user, auth_status, create_at)
            values (%s, %s, %s, %s, %s);"""
        self.db.executeSQL(
            query,
            (self.mch_id, u'提交审核', auth_user, 1, create_at)
        )

    @gen.coroutine
    def get_dt_user(self):
        query = """select dt_name from dt_user where dt_id=%s"""
        ret = self.db.selectSQL(query, (self.current_user,))
        raise gen.Return(ret[0])

    def save_dine_imgs(self):
        dine_imgs = {
            'mch_front_img': self.mch_front_img,
            'mch_inner_img': self.mch_inner_img,
            'mch_desk_img': self.mch_desk_img,
        }
        for index in range(1, 6):
            key = 'wx_dine_annex_img' + str(index)
            dine_imgs[key] = getattr(self, key, None)
        sql = """insert into
                  role_info_extension(role_id, role_type, extension_name,extension_value,create_time,update_time)
                 values(%s, %s, %s, %s, %s, %s)"""
        for each_key in dine_imgs:
            config_value = dine_imgs.get(each_key, None)
            if config_value:
                self.db.executeSQL(sql, (self.mch_id, 'mch', each_key,
                                         config_value, self.create_at, self.create_at))

    @gen.coroutine
    def save_id_image(self, image_name):
        # 不需要根据环境判断存入目录
        base_dir = os.path.join(self.application.base_dir, 'static/uploads/mch/idcard')
        file_dir = os.path.join(base_dir, '{}'.format(self.mch_id))

        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        base_tmp_dir = os.path.join(self.application.base_dir, 'static/uploads/tmp/mch/idcard')
        file_base_dir = os.path.join(base_tmp_dir, '{}'.format(self.current_user), '{}'.format(self.uuid))

        file_tmp_f_name = str(os.path.join(file_base_dir, image_name))

        file_f_name = '{}.jpg'.format(uuid.uuid4().hex)
        img_f_path = str(os.path.join(file_dir, file_f_name))

        try:
            shutil.copy(file_tmp_f_name, img_f_path)
        except Exception as err:
            log.exception.info(err)
        raise gen.Return(file_f_name)

    @gen.coroutine
    def save_mch_extensions(self, data):
        self.mch_front_img = data.get('mch_front_img', None)
        self.mch_inner_img = data.get('mch_inner_img', None)
        self.mch_desk_img = data.get('mch_desk_img', None)
        self.mch_front_img = yield self.save_id_image(self.mch_front_img)
        self.mch_inner_img = yield self.save_id_image(self.mch_inner_img)
        self.mch_desk_img = yield self.save_id_image(self.mch_desk_img)

        for each_index in range(1, 6):
            img_key = 'wx_dine_annex_img' + str(each_index)
            img_name = data.get(img_key, None)
            if img_name:
                img_name = yield self.save_id_image(img_name)
            setattr(self, img_key, img_name)
        self.save_dine_imgs()

    @gen.coroutine
    def save_mch_annex_img(self, data):
        for img_count in range(1, 6):
            annex_key = 'annex_img' + str(img_count)
            annex_img = data.get(annex_key, None)
            if annex_img:
                annex_img = yield self.save_id_image(annex_img)
            setattr(self, annex_key, annex_img)

    def update_employee_profile(self):

        status = 2
        creator_id = 0
        create_at = update_at = datetime.datetime.now()
        user_id = uline_session.query(func.max(Employee.id)).first()
        user_id = user_id[0] + 1 if user_id[0] else 10000000
        sys_type_id = uline_session.query(SysType).filter(SysType.code == "mch").one()
        new_user = UserProfile(
            id=user_id,
            name=self.mch_name,
            city=self.city,
            phone1=self.mobile,
            email=self.email,
            sex=None,
            status=status,
            creator_id=creator_id,
            create_at=create_at,
            update_at=update_at
        )
        login_employee = Employee(
            id=user_id,
            sys_id=self.mch_id,
            login_passwd=self._password,
            login_name=str(self.mch_id) + ".mch",

            sys_type_id=sys_type_id.id,
            create_at=create_at,
            update_at=update_at,
            creator_id=creator_id,
            status=status,
            user_id=user_id

        )
        uline_session.add(new_user)
        uline_session.add(login_employee)
        uline_session.commit()

        role_id = uline_session.query(Role) \
            .filter(Role.sys_type_id == sys_type_id.id, Role.sp_type == 1).one()
        employee_role = EmployeeRolePermit(employee_id=user_id, role_id=role_id.id)
        uline_session.add(employee_role)

        new_create_record = EmployeeUserLog(eutype=1,
                                            employee_id=user_id,
                                            comment="成功创建账号",
                                            operate_id=0,
                                            create_at=create_at)
        uline_session.add(new_create_record)
        uline_session.commit()
