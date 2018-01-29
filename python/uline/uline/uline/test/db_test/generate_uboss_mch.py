# -*- coding: utf-8 -*-
from __future__ import division
from os import path, makedirs
import time
from xlwt import Workbook
from uline.public.baseDB import DbClient
db = DbClient()
from uline.public.constants import PAYMENT, AUTH_STATUS, BALANCE_TYPE, BALANCE_WAY

cur_dir = path.dirname(path.abspath(__file__))


def generate_xls(dt_id=None, mch_name=None, create_at_start=None, create_at_end=None, activated_status=None, auth_status=None):
    wb = Workbook(encoding='utf-8')
    inlet_info_ws = wb.add_sheet(u'商户基本信息')
    inlet_info_data = db_inlet_info(dt_id, mch_name, create_at_start,
                                    create_at_end, activated_status, auth_status)
    id_to_name = {data[0]: data[1] for data in inlet_info_data}

    gen_inlet_info(inlet_info_ws, inlet_info_data)

    payment_info_data = db_mch_payment_info(id_to_name)
    payment_info_ws = wb.add_sheet(u'支付类型')
    gen_mch_payment_info(payment_info_ws, payment_info_data)

    file_path, static_path = general_filename(dt_id)
    wb.save(file_path)
    return static_path


def db_inlet_info(dt_id=None, mch_name=None, create_at_start=None, create_at_end=None, activated_status=None, auth_status=None):
    query = """SELECT
                  mch_inlet_info.mch_id,
                  mch_inlet_info.mch_name,
                  mch_inlet_info.mch_shortname,
                  mch_inlet_info.u_ind_code,
                  mch_inlet_info.province,
                  mch_inlet_info.city,
                  mch_inlet_info.address,
                  mch_inlet_info.service_phone,
                  mch_inlet_info.contact,
                  mch_inlet_info.mobile,
                  mch_inlet_info.email,
                  mch_balance.balance_way,
                  mch_balance.balance_type,
                  mch_balance.balance_name,
                  balance_bank_info.bank_name,
                  balance_bank_info.bank_name,
                  balance_bank_info.bank_no,
                  mch_balance.balance_account,
                  mch_balance.id_card_no,
                  mch_inlet_info.id_card_img_f,
                  mch_inlet_info.id_card_img_b,
                  mch_inlet_info.auth_status,
                  mch_user.mch_pay_key,
                  mch_user.wx_sub_mch_id
                FROM mch_inlet_info
                INNER JOIN mch_user on mch_inlet_info.mch_id = mch_user.mch_id
                  INNER JOIN mch_balance ON mch_inlet_info.mch_id = mch_balance.mch_id
                  INNER JOIN balance_bank_info on mch_balance.bank_no = balance_bank_info.bank_no
                WHERE mch_inlet_info.dt_id=%(dt_id)s
                AND (mch_inlet_info.activated_status=%(activated_status)s OR %(activated_status)s IS NULL )
                  AND (mch_inlet_info.auth_status=%(auth_status)s OR %(auth_status)s IS NULL )
                  AND (mch_inlet_info.mch_name ~ %(mch_name)s OR %(mch_name)s IS NULL )
                  AND (mch_inlet_info.create_at BETWEEN %(create_at_start)s::TIMESTAMP AND %(create_at_end)s::TIMESTAMP
                  OR %(create_at_start)s IS NULL OR %(create_at_end)s IS NULL )
                ORDER BY mch_inlet_info.create_at
                """

    ret = db.selectSQL(query, {
        'dt_id': dt_id,
        'activated_status': activated_status,
        'auth_status': auth_status,
        'mch_name': mch_name,
        'create_at_start': create_at_start,
        'create_at_end': create_at_end,
    }, fetchone=False)
    return ret


def db_mch_payment_info(mch_id_to_name):
    if not mch_id_to_name:
        return
    query = """SELECT mch_id,payment_type,payment_rate,activated_status
            FROM mch_payment WHERE mch_id = ANY(%s);
            """

    ret = db.selectSQL(query, (list(mch_id_to_name),), fetchone=False)
    return ret


def gen_inlet_info(ws, datas):
    fields = [u'商户编号', u'商户名称', u'商户简称', u'经营类目ID', u'省份', u'城市', u'联系地址', u'客服电话', u'联系人', u'联系电话',
              u'电子邮箱', u'结算方式', u'结算账号类型', u'结算户名', u'结算银行', u'支行名称', u'支行联行号', u'结算账号', u'身份证号码',
              u'身份证正面', u'身份证反面', u'审核状态（1-未审核，2-通过，3-驳回）', u'支付密钥', u'微信子商户号']
    # 渠道基本信息表
    for index, col_name in enumerate(fields):
        ws.write(0, index, col_name)

    if datas:
        inlet_data = [list(data) for data in datas]

        inlet_info = list()
        for index, data in enumerate(inlet_data):
            data[11], data[12] = BALANCE_WAY[str(data[11])], BALANCE_TYPE[str(data[12])]
            inlet_info.append(data)
        for index, data in enumerate(inlet_info, start=1):
            for col in range(len(data)):
                ws.write(index, col, data[col])


def gen_mch_payment_info(ws, datas):
    fields = [u'商户名称', u'支付类型', u'结算费率(‰)', u'激活状态']
    for index, col_name in enumerate(fields):
        ws.write(0, index, col_name)

    if datas:
        _tmp = [list(data) for data in datas]
        mch_payment_info = list()
        for data in _tmp:
            data[1], data[2], data[3] = PAYMENT[str(data[1])], data[2] / 10, AUTH_STATUS[str(data[3])]
            mch_payment_info.append(data)
        for index, data in enumerate(mch_payment_info, start=1):
            for col in range(4):
                ws.write(index, col, data[col])


def general_filename(dt_id):
    _ts = str(time.time())
    filename = "mch_inlet_export_" + _ts + ".xls"
    user_dl_path = path.join(cur_dir, str(dt_id))
    if not path.exists(user_dl_path):
        makedirs(user_dl_path)
    file_path = path.join(user_dl_path, filename)
    static_path = path.join("/static/downloads/", str(dt_id), filename)
    return [file_path, static_path]

if __name__ == '__main__':
    generate_xls(dt_id=10000000830)
