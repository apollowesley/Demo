"""merchant risk info

Revision ID: f778e84acab3
Revises: a289c147dc64
Create Date: 2017-09-20 15:10:45.919383

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f778e84acab3'
down_revision = 'a289c147dc64'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('merchant_risk',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('sys_id', sa.BigInteger(), nullable=True),
                    sa.Column('sys_type_id', sa.String(length=64), nullable=False),
                    sa.Column('source', sa.String(length=64), nullable=False),
                    sa.Column('has_risk', sa.Integer(), nullable=True),
                    sa.Column('status', sa.Integer(), nullable=False),
                    sa.Column('create_at', sa.DateTime(), nullable=False),
                    sa.Column('update_at', sa.DateTime(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('merchant_risk_item',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('merchant_risk_id', sa.Integer(), nullable=True),
                    sa.Column('risk_type', sa.String(length=64), nullable=False),
                    sa.Column('description', sa.String(length=100), nullable=True),
                    sa.Column('content', sa.String(length=500), nullable=True),
                    sa.Column('status', sa.Integer(), nullable=False),
                    sa.Column('create_at', sa.DateTime(), nullable=False),
                    sa.Column('update_at', sa.DateTime(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('trade_risk',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('sys_id', sa.BigInteger(), nullable=True),
                    sa.Column('sys_type_id', sa.String(length=64), nullable=True),
                    sa.Column('dt_id', sa.BigInteger(), nullable=True),
                    sa.Column('out_trade_no', sa.String(length=64), nullable=False),
                    sa.Column('transaction_id', sa.String(length=64), nullable=True),
                    sa.Column('platfrom', sa.String(length=64), nullable=False),
                    sa.Column('platform_pid', sa.String(length=64), nullable=True),
                    sa.Column('channel_code', sa.String(length=64), nullable=True),
                    sa.Column('sub_mch_id', sa.String(length=64), nullable=True),
                    sa.Column('risk_type', sa.String(length=64), nullable=True),
                    sa.Column('description', sa.String(length=64), nullable=True),
                    sa.Column('content', sa.String(length=500), nullable=True),
                    sa.Column('status', sa.Integer(), nullable=True),
                    sa.Column('handle_result', sa.String(length=500), nullable=True),
                    sa.Column('handler_message', sa.String(length=200), nullable=True),
                    sa.Column('create_at', sa.DateTime(), nullable=False),
                    sa.Column('update_at', sa.DateTime(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.add_column('discount',
                  sa.Column('promoter_id', sa.BigInteger(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('discount', 'promoter_id')
    op.drop_table('trade_risk')
    op.drop_table('merchant_risk_item')
    op.drop_table('merchant_risk')
    # ### end Alembic commands ###