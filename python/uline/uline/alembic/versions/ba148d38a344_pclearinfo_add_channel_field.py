#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""pclearinfo add channel field

Revision ID: ba148d38a344
Revises: e755421a8eaa
Create Date: 2017-05-25 10:57:02.463282

"""
from alembic import op
import sqlalchemy as sa

# 和商户清分渠道清分保持一致,将平台清分表也添加channel字段

# revision identifiers, used by Alembic.
revision = 'ba148d38a344'
down_revision = 'cce26eb41ab9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(u'p_clear_info', sa.Column('channel', sa.String(length=32), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'p_clear_info', 'channel')
    # ### end Alembic commands ###