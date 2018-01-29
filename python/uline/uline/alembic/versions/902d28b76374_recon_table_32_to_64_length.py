#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""recon table 32 to 64 length

Revision ID: 902d28b76374
Revises: f94d40dfac19
Create Date: 2016-12-30 17:02:44.727501

"""
# 因为撤销订单的时候,退款单号是由第三方生成的,所以32位长度可能并不合适
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '902d28b76374'
down_revision = 'f94d40dfac19'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('recon_refund_error_info', 'out_refund_no',
                    existing_type=sa.VARCHAR(length=32),
                    type_=sa.String(length=64),
                    existing_nullable=False)
    op.alter_column('recon_tx_error_info', 'out_trade_no',
                    existing_type=sa.VARCHAR(length=32),
                    type_=sa.String(length=64),
                    existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('recon_tx_error_info', 'out_trade_no',
                    existing_type=sa.String(length=64),
                    type_=sa.VARCHAR(length=32),
                    existing_nullable=False)
    op.alter_column('recon_refund_error_info', 'out_refund_no',
                    existing_type=sa.String(length=64),
                    type_=sa.VARCHAR(length=32),
                    existing_nullable=False)
    # ### end Alembic commands ###