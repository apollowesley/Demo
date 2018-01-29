#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/13/16'

#  python -m test.db_test.generate_test_db_data --env=dev
# TODO 为测试环境的写入使用单独的配置文件

# 商户部分
# 商户进件信息表  支付方式表  商户用户表  商户结算账户表
########

# 渠道商部分
# 渠道商进件信息表  支付方式表  渠道商用户表  渠道商结算账户表
########
import os
import random
import codecs
from os import path
from datetime import datetime
from uline.model.uline.info import IndustryInfo
from uline.model.uline.user import BkUser, DtUser, MchUser, UbUser
from uline.util.db import uline_session_scope, uline_Session
from uline.model.uline.info import MchInletInfo, DtInletInfo, DtPayment, WxFixedRate, MchPayment, BalanceBankInfo
from uline.model.uline.info import DtBalance, MchBalance
from uline.common import random_str

cur_dir = path.dirname(path.abspath(__file__))


# 1.行业类别
def gen_industry():
    industry = path.join(cur_dir, 'industry_info.txt')
    with open(industry) as f:
        for line in f:
            IndustryInfo.create(industry_name=line.split(' ')[0].strip(), id=line.split(' ')[1].strip(),
                                commit=True)


PWD = '$2b$12$2erf1XR85SuJ8ZYYzAPt/.XZ0RiRaC6dMCbeDoj0iW1HOAJhEE8IC'


# 2. 银联号码
def gen_bank_code():
    # sed -i -e 's/\s\+\([0-9]\+\)/,\1/' bank_code.txt
    # sed '/./=' bank_code.txt | sed '/./N; s/\n/,/'
    # http://www.laurivan.com/load-a-csv-file-with-header-in-postgres-via-psycopg/
    bank_code_file = path.join(cur_dir, 'bank_code.txt')
    SQL_STATEMENT = """
        COPY %s FROM STDIN WITH
            CSV
            HEADER
            DELIMITER AS ','
        """
    print(u'导入银联商户')
    cur = uline_Session().connection().connection.cursor()
    with codecs.open(bank_code_file, encoding='UTF-8') as f:
        cur.copy_expert(sql=SQL_STATEMENT % 'balance_bank_info', file=f)
        cur.connection.commit()
        cur.connection.close()


# 3. 在bk_user 中创建1个银行账号
def gen_bk_user():
    data = {
        'bk_id': 1,
        'bk_name': u'银行用户名',
        'email': '123@123.com',
        'password': PWD,
        'create_at': datetime.now(),
        'update_at': datetime.now(),
    }
    BkUser.create(commit=True, **data)


def _gen_dt_user(dt_email=None):
    dt_name = u'随机渠道商名_' + str(random.randint(10000000, 99999999))
    address = u'随机地址' + str(random.randint(100, 999))
    content = u'随机人名' + str(random.randint(1000, 9999))
    email = dt_email or random_str(10) + '@gmail.com'
    mobile = '13' + str(random.randint(100000000, 999999999))
    create_at = datetime.now()
    update_at = datetime.now()
    dt_id = random.randint(1, 100000000)
    id_card_no = str(random.randint(100000000000000000, 999999999999999999))

    with uline_session_scope() as session:
        data = {
            "dt_id": dt_id,
            'dt_name': dt_name,
            'industry_type': 1,
            'province': u'湖北省',
            'city': u'荆门市',
            'address': address,
            'contact': content,
            'mobile': mobile,
            'email': email,
            'id_card_img_f': u'33809ceefd6e4be8b8fe2f9c5e273e18.jpg',
            'id_card_img_b': u'4edfef9bba1e42c097ad397501f56a3f.jpg',
            'auth_status': 2,
            'activated_status': 2,
            'create_at': create_at,
            'update_at': update_at
        }
        dt_inlet = DtInletInfo(**data)
        session.add(dt_inlet)

        objects = [DtPayment(**{
            'dt_id': dt_id,
            'payment_type': i,
            'payment_rate': 30,
            'activated_status': 2,
            'create_at': create_at,
            'update_at': update_at
        }) for i in range(1, 4)]
        session.bulk_save_objects(objects)

        user = {
            'dt_id': dt_id,
            'dt_name': dt_name,
            'email': email,
            'password': PWD,
            'create_at': create_at,
            'update_at': update_at
        }
        dt_user = DtUser(**user)
        session.add(dt_user)

        # balance_type 企业 1 个人 2
        balance = {
            'dt_id': dt_id,
            'balance_type': 1,
            'balance_name': u'联通测试',
            'bank_no': '001100001509',
            'balance_account': '592902360810902',
            'id_card_no': id_card_no,
            'create_at': create_at,
            'update_at': update_at
        }
        balance = DtBalance(**balance)
        session.add(balance)


def gen_ub_user():
    data = {
        'ub_id': 1,
        'ub_name': u'官方用户',
        'email': '123@123.com',
        'password': PWD,
        'create_at': datetime.now(),
        'update_at': datetime.now(),
    }
    UbUser.create(commit=True, **data)


# 4. 模拟官方后台进件操作  创建2个渠道商
def gen_dt_user():
    for _ in range(2):
        print(u'创建第{}个渠道商中'.format(_ + 1))
        _gen_dt_user()


# 5 每个渠道商创建2个商户
def gen_mch_user():
    all_dt = DtUser.get_by().all()
    id_card_no = str(random.randint(100000000000000000, 999999999999999999))
    for index, dt in enumerate(all_dt):
        dt_id = dt.dt_id
        print u'创建商户中'.format(index + 1)
        for _ in range(2):
            ran_str = str(random.randint(10000000, 99999999))
            mch_name = u'随机商户名_' + ran_str
            mch_shortname = ran_str
            address = u'随机地址' + str(random.randint(100, 999))
            content = u'随机人名' + str(random.randint(1000, 9999))
            email = random_str(10) + '@gmail.com'
            mobile = '13' + str(random.randint(100000000, 999999999))
            service_phone = '13' + str(random.randint(100000000, 999999999))
            create_at = datetime.now()
            update_at = datetime.now()

            mch_id = random.randint(1000000000, 9000000000)

            with uline_session_scope() as session:
                data = {
                    "mch_id": mch_id,
                    'mch_name': mch_name,
                    'mch_shortname': mch_shortname,
                    'dt_id': dt_id,
                    'industry_type': 1,
                    'province': u'湖北省',
                    'city': u'荆门市',
                    'address': address,
                    'contact': content,
                    'mobile': mobile,
                    'service_phone': service_phone,
                    'email': email,
                    'id_card_img_f': u'33809ceefd6e4be8b8fe2f9c5e273e18.jpg',
                    'id_card_img_b': u'4edfef9bba1e42c097ad397501f56a3f.jpg',
                    'auth_status': 2,
                    'activated_status': 2,
                    'create_at': create_at,
                    'update_at': update_at
                }
                mch_user = MchInletInfo(**data)
                session.add(mch_user)

                objects = [MchPayment(**{
                    'mch_id': mch_id,
                    'payment_type': i,
                    'payment_rate': 60,
                    'activated_status': 2,
                    'create_at': create_at,
                    'update_at': update_at
                }) for i in range(1, 4)]
                session.bulk_save_objects(objects)

                user = {
                    'mch_id': mch_id,
                    'mch_name': mch_name,
                    'email': email,
                    'password': PWD,
                    'create_at': create_at,
                    'update_at': update_at,
                    'mch_pay_key': 'mch_pay_key',
                    'wx_sub_mch_id': 'wx_sub_mch_id',
                    'status': 1
                }
                mch_user = MchUser(**user)
                session.add(mch_user)

                balance = {
                    'mch_id': mch_id,
                    'balance_type': 2,
                    'balance_name': u'全渠道',
                    'bank_no': '001100001509',
                    'balance_account': '6216261000000000018',
                    'id_card_no': id_card_no,
                    'create_at': create_at,
                    'update_at': update_at
                }
                mch_balance = MchBalance(**balance)
                session.add(mch_balance)


# 6. 生成微信对平台固定费率 千分之三
def gen_wx_fixed_rate():
    for i in range(1, 4):
        data = {
            'rate': 20,
            'create_at': datetime.now(),
            'payment_type': i
        }
        WxFixedRate.create(commit=True, **data)


def gen_random_num_str():
    return str(random.randint(10000000000000000000, 99999999999999999999))


def get_random_trade_type():
    return random.choice(['JSAPI', 'NATIVE', 'APP', 'MICROPAY'])


def get_random_trade_state():
    return random.choice(['SUCCESS', 'REFUND', 'NOTPAY', 'CLOSED', 'REVOKED', 'USERPAYING', 'PAYERROR'])


def main():
    if not UbUser.get_by().count():
        gen_ub_user()

    if not IndustryInfo.get_by().count():
        gen_industry()

    if not BalanceBankInfo.get_by().count():
        gen_bank_code()

    if not BkUser.get_by().count():
        gen_bk_user()
        bk_number = BkUser.get_by().count()
        assert bk_number == 1

    if not DtInletInfo.get_by().count():
        gen_dt_user()
        dt_inlet = DtInletInfo.get_by().count()
        assert dt_inlet == 2
        dt_number = DtUser.get_by().count()
        assert dt_number == 2

    if not MchInletInfo.get_by().count():
        gen_mch_user()
        mch_inlet = MchInletInfo.get_by().count()
        assert mch_inlet == 4
        mch_number = MchUser.get_by().count()
        assert mch_number == 4

    if not WxFixedRate.get_by().count():
        gen_wx_fixed_rate()
