#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uline_risk.handlers.baseHandlers import RESTfulHandler
from uline_risk.model.uline.info import MchBalance
from uline_risk.utils import db


class GetAllFreezeMerchant(RESTfulHandler):

    def prepare(self):
        pass

    def get(self):
        freeze_mch_ids = []
        with db.uline_session_scope() as session:
            db_freeze_account = session.query(MchBalance).filter(MchBalance.status == 1).all()
            if db_freeze_account:
                freeze_mch_ids = [each_account.mch_id for each_account in db_freeze_account]
        response = self.generate_response_msg(**{"freeze_mch_ids": freeze_mch_ids})
        self.write(response)
        self.finish()
