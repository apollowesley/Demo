#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""role_extension

Revision ID: 7cbf2dc530fb
Revises: 4972ce55e188
Create Date: 2017-07-13 18:46:55.073625

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '7cbf2dc530fb'
down_revision = '4972ce55e188'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('role_info_extension',
                    sa.Column('id', sa.BigInteger(), nullable=False),
                    sa.Column('role_id', sa.BigInteger(), nullable=True),
                    sa.Column('role_type', sa.String(length=20), nullable=False),
                    sa.Column('extension_name', sa.String(length=30), nullable=False),
                    sa.Column('extension_value', sa.String(length=200), nullable=False),
                    sa.Column('create_time', sa.DateTime(), server_default=sa.text(u'now()'), nullable=False),
                    sa.Column('update_time', sa.DateTime(), server_default=sa.text(u'now()'), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('role_info_extension')
    # ### end Alembic commands ###
