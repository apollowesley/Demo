#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""mch_user add unionpay_sub_mch_id

Revision ID: c05009d6e96e
Revises: 246a728e54d3
Create Date: 2017-11-22 10:57:37.540900

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c05009d6e96e'
down_revision = '246a728e54d3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # op.add_column('mch_user', sa.Column('unionpay_sub_mch_id', sa.VARCHAR(length=32), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # op.drop_column('mch_user', 'unionpay_sub_mch_id')
    # ### end Alembic commands ###