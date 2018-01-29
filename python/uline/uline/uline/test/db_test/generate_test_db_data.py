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
from uline.public.baseTradeDB import TradeDbClient
import random
import codecs
from os import path
from uline.public.baseDB import DbClient
from .db_util import random_str, random_timestramp, bcrypt_pwd_test, random_ch
from uline.public.common import create_mch_id, create_bk_id, create_dt_id, create_ub_id

db = DbClient()
tdb = TradeDbClient()

PWD = bcrypt_pwd_test('123456')

cur_dir = path.dirname(path.abspath(__file__))

# 如果存在表的时候就先删除再重建
table_number = db.selectSQL("""SELECT count(*)
FROM
  pg_stat_user_tables
WHERE schemaname = 'public'""")

exists = True if table_number else False

if exists:
    db.executeSQL("""
    DROP TABLE IF EXISTS public.recon_tx_error_info;
    DROP TABLE IF EXISTS public.recon_refund_error_info;
    DROP TABLE IF EXISTS public.p_daily_balance_info;
    DROP TABLE IF EXISTS public.p_clear_info;
    DROP TABLE IF EXISTS public.mch_user;
    DROP TABLE IF EXISTS public.mch_payment;
    DROP TABLE IF EXISTS public.mch_inlet_info;
    DROP TABLE IF EXISTS public.mch_daily_balance_info;
    DROP TABLE IF EXISTS public.mch_clear_topay_info;
    DROP TABLE IF EXISTS public.mch_clear_info;
    DROP TABLE IF EXISTS public.mch_balance;
    DROP TABLE IF EXISTS public.industry_info;
    DROP TABLE IF EXISTS public.dt_user;
    DROP TABLE IF EXISTS public.dt_payment;
    DROP TABLE IF EXISTS public.dt_inlet_info;
    DROP TABLE IF EXISTS public.dt_daily_balance_total_info;
    DROP TABLE IF EXISTS public.dt_daily_balance_info;
    DROP TABLE IF EXISTS public.dt_clear_topay_info;
    DROP TABLE IF EXISTS public.dt_clear_info;
    DROP TABLE IF EXISTS public.dt_balance;
    DROP TABLE IF EXISTS public.bk_user;
    DROP TABLE IF EXISTS public.balance_bank_info;
    DROP TABLE IF EXISTS public.ub_user;
    DROP TABLE IF EXISTS public.auth_mch_info;
    DROP TABLE IF EXISTS public.auth_dt_info;
    DROP TABLE IF EXISTS public.activated_mch_info;
    DROP TABLE IF EXISTS public.activated_dt_info;
    DROP TABLE IF EXISTS public.wx_fixed_rate;
    DROP TABLE IF EXISTS public.mch_inlet_to_wx_info;
    DROP SEQUENCE IF EXISTS public.tb_bk_id_seq;
    DROP SEQUENCE IF EXISTS public.tb_dt_id_seq;
    DROP SEQUENCE IF EXISTS public.tb_mch_id_seq;
    DROP SEQUENCE IF EXISTS public.tb_ub_id_seq;
    DROP SEQUENCE IF EXISTS public.recon_refund_error_info_id_seq;
    """)

schema = path.join(cur_dir, 'db_schema')
with codecs.open(schema, encoding='UTF-8') as f:
    db.executeSQL(f.read())


# 1.行业类别
def gen_industry():
    industry = path.join(cur_dir, 'industry_info.txt')
    with open(industry) as f:
        db.executeSQL('INSERT INTO industry_info (industry_name,industry_code) VALUES (%s, %s);',
                      [(line.split(' ')[0].strip(), line.split(' ')[1].strip()) for line in f])


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
    with codecs.open(bank_code_file, encoding='UTF-8') as f:
        with db.get_db() as cur:
            cur.copy_expert(sql=SQL_STATEMENT % 'balance_bank_info', file=f)
            cur.connection.commit()


# 3. 在bk_user 中创建1个银行账号
# TODO 目前update_at不一定大于create_at
def gen_bk_user():
    bk_name = u'银行用户'
    bk_users = [(create_bk_id(), bk_name, random_str() + '@gmail.com', PWD, random_timestramp(), random_timestramp())
                for _ in range(1)]
    db.executeSQL(
        'INSERT INTO bk_user (bk_id, bk_name, email,password,create_at,update_at) VALUES (%s, %s,%s,%s,%s,%s);',
        bk_users)
    db.executeSQL('insert into bk_user (bk_id, bk_name, email,password,create_at,update_at) '
                  'VALUES (%s, %s,%s,%s,%s,%s);',
                  (create_bk_id(), bk_name, '123@123.com', PWD, random_timestramp(), random_timestramp()))


def gen_ub_user():
    ub_name = u'官方用户'
    ub_users = [(create_ub_id(), ub_name, random_str(6) + '@gmail.com', PWD, random_timestramp(), random_timestramp())
                for _ in range(1)]
    db.executeSQL(
        'INSERT INTO ub_user (ub_id, ub_name, email,password,create_at,update_at) VALUES (%s, %s,%s,%s,%s, %s);',
        ub_users)
    db.executeSQL('INSERT INTO ub_user (ub_id, ub_name, email,password,create_at,update_at) '
                  'VALUES (%s, %s,%s,%s,%s, %s);',
                  (create_ub_id(), ub_name, '123@123.com', PWD, random_timestramp(), random_timestramp()))


def _gen_dt_user(dt_email=None):
    dt_name = u'随机渠道商名_' + str(random.randint(10000000, 99999999))
    address = u'随机地址' + str(random.randint(100, 999))
    content = u'随机人名' + str(random.randint(1000, 9999))
    email = dt_email or random_str(10) + '@gmail.com'
    mobile = '13' + str(random.randint(100000000, 999999999))
    create_at = random_timestramp()
    update_at = random_timestramp()
    dt_id = create_dt_id()
    id_card_no = str(random.randint(100000000000000000, 999999999999999999))

    with db.get_db() as cur:
        cur.execute("""
            INSERT INTO dt_inlet_info (dt_id, dt_name, industry_type, province, city, address, contact, mobile, email, id_card_img_f, id_card_img_b, auth_status, activated_status, create_at, update_at)
            VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING dt_id;""",
                    (dt_id, dt_name, 1, u'湖北省', u'荆门市', address, content, mobile, email,
                     u'33809ceefd6e4be8b8fe2f9c5e273e18.jpg', u'4edfef9bba1e42c097ad397501f56a3f.jpg', 2, 2, create_at,
                     update_at))

        cur.executemany("""
            INSERT INTO dt_payment (dt_id,payment_type,payment_rate,activated_status,create_at,update_at) VALUES (%s,%s,%s,%s,%s,%s);""",
                        [(dt_id, i, 40, 2, create_at, update_at) for i in range(1, 4)])

        cur.execute("""
            INSERT INTO dt_user(dt_id, dt_name, email, password, create_at, update_at) VALUES (%s,%s,%s,%s,%s,%s)""",
                    (dt_id, dt_name, email, PWD, create_at, update_at))

        cur.execute("""
            INSERT INTO dt_balance (dt_id, balance_type, balance_name, bank_no, balance_account, id_card_no, create_at, update_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s);""", (
            dt_id, 1, content, '001100001509', random_str(10), id_card_no, create_at, update_at))
        cur.connection.commit()


# 4. 模拟官方后台进件操作  创建1000个渠道商
def gen_dt_user():
    _gen_dt_user('123@123.com')
    for _ in range(1000):
        if random.random() > 0.9:
            print(u'创建第{}个渠道商中'.format(_ + 1))
        _gen_dt_user()


# 默认添加
# {
# :mch_id = > "100010",
# :mch_name = > "兰州拉面深圳总店",
# :mch_pay_key = > "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456",
# :status = > 1,
# :email = > "y@u.cc",
# :wx_sub_mch_id = > "15048267"
# }
# 5 取出600个渠道商  每个创建100个商户
def gen_mch_user():
    # 。。。。为了匹配123@123我先这样了
    all_dt = db.selectSQL(
        """SELECT dt_id,dt_name FROM dt_user WHERE email LIKE '1%' ORDER BY email""", fetchone=False)
    id_card_no = str(random.randint(100000000000000000, 999999999999999999))
    for index, (dt_id, dt_user) in enumerate(all_dt):
        if random.random() > 0.9:
            print u'创建第{}*100个商户中'.format(index + 1)
        for _ in range(11):
            ran_str = str(random.randint(10000000, 99999999))
            mch_name = u'兰州拉面深圳总店' if index == 0 and _ == 0 else u'随机商户名_' + ran_str
            mch_shortname = ran_str
            address = u'随机地址' + str(random.randint(100, 999))
            content = u'随机人名' + str(random.randint(1000, 9999))
            email = random_str(10) + '@gmail.com'
            mobile = '13' + str(random.randint(100000000, 999999999))
            service_phone = '13' + str(random.randint(100000000, 999999999))
            create_at = random_timestramp()
            update_at = random_timestramp()

            mch_id = 100010 if index == 0 and _ == 0 else create_mch_id()

            with db.get_db() as cur:
                cur.execute("""
                    INSERT INTO mch_inlet_info(mch_id, mch_name, mch_shortname, dt_id, industry_type, province, city, address, contact, mobile, service_phone, email, id_card_img_f, id_card_img_b, auth_status, activated_status, create_at, update_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                            (mch_id, mch_name, mch_shortname, dt_id, 1, u'湖北省', u'荆门市', address, content, mobile,
                             service_phone, email,
                             u'33809ceefd6e4be8b8fe2f9c5e273e18.jpg', u'4edfef9bba1e42c097ad397501f56a3f.jpg',
                             2, 2, create_at, update_at))

                cur.executemany("""
                    INSERT INTO mch_payment (mch_id,payment_type,payment_rate,activated_status,create_at,update_at) VALUES (%s,%s,%s,%s,%s,%s);""",
                                [(mch_id, i, 60, 2, create_at, update_at) for i in range(1, 4)])

                cur.execute("""
                    INSERT INTO mch_user(mch_id, mch_name, email, password, create_at, update_at,mch_pay_key,wx_sub_mch_id,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                            (mch_id, mch_name, email, PWD, create_at, update_at, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ123456',
                             '15048267', '1'))

                cur.execute("""
                    INSERT INTO mch_balance (mch_id, balance_type, balance_name, bank_no, balance_account, id_card_no, create_at, update_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s);""", (
                    mch_id, random.choice([1, 2]), content, '001100001509', random_str(
                        10), id_card_no, create_at,
                    update_at))
                cur.connection.commit()


# 6. 生成微信对平台固定费率 千分之三
def gen_wx_fixed_rate():
    for i in range(1, 4):
        db.executeSQL("""INSERT INTO wx_fixed_rate(rate,create_at,payment_type) VALUES (20,now(),%s)""", (i,))


# 往uline_trade插入数据，先清零再插入
def get_mch_id():
    ret = db.selectSQL("""select mch_id from mch_user""", fetchone=False)
    mch_id_l = [str(i[0]) for i in ret]
    return mch_id_l


def gen_random_num_str():
    return str(random.randint(10000000000000000000, 99999999999999999999))


def get_random_trade_type():
    return random.choice(['JSAPI', 'NATIVE', 'APP', 'MICROPAY'])


def get_random_trade_state():
    return random.choice(['SUCCESS', 'REFUND', 'NOTPAY', 'CLOSED', 'REVOKED', 'USERPAYING', 'PAYERROR'])


def del_trade_info():
    query = """delete from orders where ul_mch_id <> '100010'"""
    tdb.executeSQL(query)


def gen_trade_info():
    mch_id_l = get_mch_id()
    query = """insert into orders (
    channel, appid, sub_appid, mch_id, sub_mch_id, device_info, body, detail, attach, out_trade_no, total_fee,
    fee_type,spbill_create_ip, goods_tag, limit_pay, auth_code, bank_type, cash_fee_type, cash_fee,
    settlement_total_fee, coupon_fee, wx_transaction_id, time_end, trade_type, created_at, complete_at, trade_state, ul_mch_id
    ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"""
    trade_info = [('weixin', 'wxdace645e0bc2c424', '', '1900008951', '15048267', 'n1', 'test', 'testdetaill',
                   'heheheheheheeheh', gen_random_num_str(), '2000', 'CNY', '127.0.0.1', 'nnnn', '',
                   gen_random_num_str(),
                   '', 'CNY', '2000', '0', '0', gen_random_num_str(), '201610171212', get_random_trade_type(),
                   random_timestramp(), random_timestramp(), get_random_trade_state(), mch_id) for mch_id in mch_id_l]
    tdb.executeSQL(query, trade_info)


if __name__ == '__main__':
    gen_industry()
    gen_bank_code()
    gen_bk_user()
    # gen_dt_user()
    # gen_mch_user()
    gen_ub_user()
    gen_wx_fixed_rate()
    # del_trade_info()
    # gen_trade_info()
