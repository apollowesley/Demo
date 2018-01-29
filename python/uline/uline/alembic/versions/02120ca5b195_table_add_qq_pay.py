#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""table add qq pay

Revision ID: 02120ca5b195
Revises: 27d9edda20c3
Create Date: 2017-11-28 12:01:32.694510

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '02120ca5b195'
down_revision = '27d9edda20c3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('industry_qq_info',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('industry_code', sa.String(length=40), nullable=False),
                    sa.Column('industry_name', sa.String(length=200), nullable=False),
                    sa.Column('status', sa.Integer(), server_default=sa.text(u'1'), nullable=False),
                    sa.Column('create_at', sa.DateTime(), server_default=sa.text(u'now()'), nullable=False),
                    sa.Column('update_at', sa.DateTime(), server_default=sa.text(u'now()'), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('industry_qq_info_index', 'industry_qq_info', ['industry_code'], unique=True)
    op.add_column('industry_uline_info', sa.Column('qq_ind_code', sa.String(length=40), nullable=True))
    op.add_column('dt_user', sa.Column('qq_sub_mch_id', sa.String(length=32), nullable=True))
    op.add_column('dt_inlet_info', sa.Column('qq_ind_code', sa.String(length=40), nullable=True))
    op.add_column('mch_user', sa.Column('qq_sub_mch_id', sa.String(length=32), nullable=True))
    op.add_column('mch_inlet_info', sa.Column('qq_ind_code', sa.String(length=40), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('industry_uline_info', 'qq_ind_code')
    op.drop_column('mch_user', 'qq_sub_mch_id')
    op.drop_column('dt_inlet_info', 'qq_ind_code')
    op.drop_column('industry_uline_info', 'qq_ind_code')
    op.drop_column('dt_user', 'qq_sub_mch_id')
    op.drop_column('mch_inlet_info', 'qq_ind_code')
    op.drop_index('industry_qq_info_index', table_name='industry_qq_info')
    op.drop_table('industry_qq_info')
    # ### end Alembic commands ###