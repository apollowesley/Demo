#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 1.mch_user中状态变为1，密码修改为随机数,邮箱前面加上888
# 2.mch_inlet_info中审核状态修改为1，激活状态修改为1,手机号第一位修改为8
# 3.支付表中支付状态全部关闭

from datetime import datetime
from uline.public.db import initdb
from uline.model.uline.user import MchUser
from uline.model.uline.info import MchInletInfo
from uline.model.uline.info import MchPayment
from uline.public.db import uline_session_scope

MCH = ['100000690222', '100000691112', '100000705353', '100000689785', '100000732382', '100000715998']


def close_mch(session, MCH):
    for mch in MCH:
        m = session.query(MchUser).filter(MchUser.mch_id == int(mch)).first()
        m.password = '8' * 32
        m.email = '8' * 3 + m.email
        m.status = 1
        m.update_at = datetime.now()

        m_inlet_info = session.query(MchInletInfo).filter(MchInletInfo.mch_id == int(mch)).first()
        m_inlet_info.mobile = '8' + m_inlet_info.mobile[1:]
        # m_inlet_info.auth_status = 1
        m_inlet_info.activated_status = 1
        m_inlet_info.update_at = datetime.now()

        for m_payment in session.query(MchPayment).filter(MchPayment.mch_id == int(mch)):
            m_payment.activated_status = 1
            m_payment.update_at = datetime.now()


if __name__ == '__main__':
    initdb()
    with uline_session_scope() as session:
        close_mch(session, MCH)
