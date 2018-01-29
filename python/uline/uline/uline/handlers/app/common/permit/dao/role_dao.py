#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Liufei
# Create: 2017-09-22 14:53:28

from uline.public import log
from uline.public.baseDB import DbClient
from uline.public.baseTradeDB import TradeDbClient


class RoleDao:
    def __init__(self):
        self.db = DbClient()
        self.tdb = TradeDbClient()

    def verify_sys_permit(self, role_id, sys_id, sys_type_id, permits):
        """
        验证一个用户是否拥有某些权限
        :param role_id:
        :param sys_id:
        :param sys_type_id:
        :param permits:
        :return:
        """
        sql = """
        select count(1) from role_permit as rp
         inner join employee_role_permit as erp on erp.role_id = rp.role_id
         inner join employee as e on e.id = erp.employee_id
         inner join permit as p on p.id = rp.permit_id
        """

    def create_role(self, role_id, name, sys_type_id, sys_id, permits, isunion=0, is_boss=0, is_admin=0):
        sql = """
            
        """
