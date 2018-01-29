#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 1.dt_user中状态变为1，密码修改为随机数,邮箱前面加上888
# 2.dt_inlet_info中审核状态修改为1，激活状态修改为1,手机号第一位修改为8
# 3.支付表中支付状态全部关闭
# 4.处理旗下所有商户

from datetime import datetime
from uline.public.db import initdb
from uline.model.uline.user import DtUser
from uline.model.uline.info import DtInletInfo, MchInletInfo
from uline.model.uline.info import DtPayment
from emergency.close_mch import close_mch
from uline.public.db import uline_session_scope

DT = ['']


def close_dt(session, DT):
    for dt in DT:
        d = session.query(DtUser).filter(DtUser.dt_id == int(dt)).first()
        d.password = '8' * 32
        d.email = '8' * 3 + d.email
        d.status = 1
        d.update_at = datetime.now()

        dt_inlet_info = session.query(DtInletInfo).filter(DtInletInfo.dt_id == int(dt)).first()
        dt_inlet_info.mobile = '8' + dt_inlet_info.mobile[1:]
        # m_inlet_info.auth_status = 1
        dt_inlet_info.activated_status = 1
        dt_inlet_info.update_at = datetime.now()

        for dt_payment in session.query(DtPayment).filter(DtPayment.dt_id == int(dt)):
            dt_payment.activated_status = 1
            dt_payment.update_at = datetime.now()

        mch = session.query(MchInletInfo.mch_id).filter(MchInletInfo.dt_id == int(dt)).all()
        mch = [i[0] for i in mch]
        if mch:
            close_mch(session, mch)


if __name__ == '__main__':
    initdb()
    with uline_session_scope() as sessioon:
        close_dt(sessioon, DT)
