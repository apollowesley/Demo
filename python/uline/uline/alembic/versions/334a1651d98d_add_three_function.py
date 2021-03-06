# -*- coding: utf-8 -*-
"""add three function

Revision ID: 334a1651d98d
Revises: 01cac522cc32
Create Date: 2017-03-17 15:21:01.197514

"""

# 添加功能：
# 1） 渠道进件添加客服电话
# 2） 商户添加二维码支付回调
# 3） 渠道商开通子帐号
# 4） 增加异常信息报告到errbit
# 5） 修改商户渠道商进件时审核中不能支付的问题
# 解决bug:
# 1) 修改商户和渠道商信息中有空格时会引发修改错误的问题

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '334a1651d98d'
down_revision = '01cac522cc32'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('change_record',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('mch_id', sa.BigInteger(), nullable=True),
                    sa.Column('bk_id', sa.BigInteger(), nullable=True),
                    sa.Column('dt_id', sa.BigInteger(), nullable=True),
                    sa.Column('change_type', sa.Integer(), nullable=True),
                    sa.Column('create_at', sa.DateTime(), server_default=sa.text(u'now()'), nullable=False),
                    sa.Column('status', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('bk_subuser',
                    sa.Column('bk_sub_id', sa.Integer(), nullable=False),
                    sa.Column('bk_user_bk_id', sa.Integer(), nullable=True),
                    sa.Column('bk_sub_name', sa.String(length=64), nullable=False),
                    sa.Column('email', sa.String(length=64), nullable=False),
                    sa.Column('password', sa.String(length=256), nullable=False),
                    sa.Column('api_key', sa.String(length=64), nullable=True),
                    sa.Column('create_at', sa.DateTime(), server_default=sa.text(u'now()'), nullable=False),
                    sa.Column('update_at', sa.DateTime(), server_default=sa.text(u'now()'), nullable=False),
                    sa.ForeignKeyConstraint(['bk_user_bk_id'], ['bk_user.bk_id'], ),
                    sa.PrimaryKeyConstraint('bk_sub_id')
                    )
    op.create_index('bk_subuser_email_uindex', 'bk_subuser', ['email'], unique=True)
    op.create_index('bk_subuser_index', 'bk_subuser', ['bk_sub_id'], unique=True)
    op.create_table('dt_subuser',
                    sa.Column('dt_sub_id', sa.BigInteger(), nullable=False),
                    sa.Column('dt_user_dt_id', sa.BigInteger(), nullable=True),
                    sa.Column('dt_sub_name', sa.String(length=64), nullable=False),
                    sa.Column('email', sa.String(length=64), nullable=False),
                    sa.Column('password', sa.String(length=256), nullable=False),
                    sa.Column('api_key', sa.String(length=64), nullable=True),
                    sa.Column('status', sa.Integer(), server_default=sa.text(u'0'), nullable=False),
                    sa.Column('create_at', sa.DateTime(), server_default=sa.text(u'now()'), nullable=False),
                    sa.Column('update_at', sa.DateTime(), server_default=sa.text(u'now()'), nullable=False),
                    sa.Column('wx_sub_mch_id', sa.String(length=64), nullable=True),
                    sa.Column('mch_pay_key', sa.String(length=64), nullable=True),
                    sa.Column('rate', sa.SmallInteger(), nullable=True),
                    sa.ForeignKeyConstraint(['dt_user_dt_id'], ['dt_user.dt_id'], ),
                    sa.PrimaryKeyConstraint('dt_sub_id')
                    )
    op.create_index('dt_subuser_email_uindex', 'dt_subuser', ['email'], unique=True)
    op.create_index('dt_subuser_index', 'dt_subuser', ['dt_sub_id'], unique=True)
    op.alter_column(u'auth_dt_info', 'comment',
                    existing_type=sa.TEXT(),
                    type_=sa.String(length=64),
                    existing_nullable=False)
    op.alter_column(u'auth_mch_info', 'comment',
                    existing_type=sa.TEXT(),
                    type_=sa.String(length=64),
                    existing_nullable=False)
    op.add_column(u'dt_inlet_info', sa.Column('service_phone', sa.String(length=15), nullable=True))
    op.add_column(u'mch_inlet_info', sa.Column('pay_notify_url', sa.String(length=200), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'mch_inlet_info', 'pay_notify_url')
    op.drop_column(u'dt_inlet_info', 'service_phone')
    op.alter_column(u'auth_mch_info', 'comment',
                    existing_type=sa.String(length=64),
                    type_=sa.TEXT(),
                    existing_nullable=False)
    op.alter_column(u'auth_dt_info', 'comment',
                    existing_type=sa.String(length=64),
                    type_=sa.TEXT(),
                    existing_nullable=False)
    op.drop_index('dt_subuser_index', table_name='dt_subuser')
    op.drop_index('dt_subuser_email_uindex', table_name='dt_subuser')
    op.drop_table('dt_subuser')
    op.drop_index('bk_subuser_index', table_name='bk_subuser')
    op.drop_index('bk_subuser_email_uindex', table_name='bk_subuser')
    op.drop_table('bk_subuser')
    op.drop_table('change_record')
    # ### end Alembic commands ###
