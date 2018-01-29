#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""mch_trand_id_uindex

Revision ID: 31f6bc04631c
Revises: 84e003fd7f44
Create Date: 2017-05-12 18:34:44.833664

"""
from alembic import op

# 将mch_id和mch_d0_trand_id进行联合唯一索引

# revision identifiers, used by Alembic.
revision = '31f6bc04631c'
down_revision = '84e003fd7f44'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('COMMIT')
    op.execute(
        'CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS d0_withdraw_mch_id_mch_d0_trand_id_uindex ON public.d0_withdraw (mch_id, mch_d0_trand_id)')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('COMMIT')
    op.execute('DROP INDEX CONCURRENTLY IF EXISTS d0_withdraw_mch_id_mch_d0_trand_id_uindex')
    # ### end Alembic commands ###