#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""add column dt_type for table dt_inlet_info

Revision ID: 36728edc9201
Revises: c7dfc5bb914a
Create Date: 2017-04-06 17:01:12.551079

"""


# 添加渠道商为银行渠道商

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from uline.public.db import initdb
from uline.model.uline.info import DtInletInfo

initdb()
Session = sessionmaker()

# revision identifiers, used by Alembic.
revision = '36728edc9201'
down_revision = 'c7dfc5bb914a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('dt_inlet_info',
                  sa.Column('dt_type', sa.SmallInteger, nullable=False, server_default=sa.text('1')))

    # 将历史的dt_type全部修改为1// 2为银行内部渠道商
    bind = op.get_bind()
    session = Session(bind=bind)

    for i in session.query(DtInletInfo):
        i.dt_type = 1

    session.commit()


def downgrade():
    op.drop_column('dt_inlet_info', 'dt_type')
