"""add table mch_book dt_book bank_book p_book

Revision ID: 83c8b28a5cd0
Revises: 6863e951b279
Create Date: 2017-08-21 11:55:56.846494

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '83c8b28a5cd0'
down_revision = '6863e951b279'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bank_book',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('bank_id', sa.BigInteger(), server_default='0', nullable=False),
                    sa.Column('pay_channel', sa.String(length=64), server_default='', nullable=False),
                    sa.Column('profit_total', sa.BigInteger(), server_default='0', nullable=False),
                    sa.Column('cut_date', sa.Date(), server_default=sa.text(u'now()'), nullable=False),
                    sa.Column('create_at', sa.DateTime(), server_default=sa.text(u'now()'), nullable=False),
                    sa.Column('update_at', sa.DateTime(), server_default=sa.text(u'now()'), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('dt_book',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('dt_id', sa.BigInteger(), server_default='0', nullable=False),
                    sa.Column('pay_channel', sa.String(length=64), server_default='', nullable=False),
                    sa.Column('profit_total', sa.BigInteger(), server_default='0', nullable=False),
                    sa.Column('cut_date', sa.Date(), server_default=sa.text(u'now()'), nullable=False),
                    sa.Column('create_at', sa.DateTime(), server_default=sa.text(u'now()'), nullable=False),
                    sa.Column('update_at', sa.DateTime(), server_default=sa.text(u'now()'), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('mch_book',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('mch_id', sa.BigInteger(), server_default='0', nullable=False),
                    sa.Column('dt_id', sa.BigInteger(), server_default='0', nullable=False),
                    sa.Column('pay_channel', sa.String(length=64), server_default='', nullable=False),
                    sa.Column('profit_total', sa.BigInteger(), server_default='0', nullable=False),
                    sa.Column('trade_total', sa.BigInteger(), server_default='0', nullable=False),
                    sa.Column('refund_total', sa.BigInteger(), server_default='0', nullable=False),
                    sa.Column('refund_freeze', sa.BigInteger(), server_default='0', nullable=False),
                    sa.Column('d0_total', sa.BigInteger(), server_default='0', nullable=False),
                    sa.Column('d0_freeze', sa.BigInteger(), server_default='0', nullable=False),
                    sa.Column('cut_date', sa.Date(), server_default=sa.text(u'now()'), nullable=False),
                    sa.Column('create_at', sa.DateTime(), server_default=sa.text(u'now()'), nullable=False),
                    sa.Column('update_at', sa.DateTime(), server_default=sa.text(u'now()'), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('p_book',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('pay_channel', sa.String(length=64), server_default='', nullable=False),
                    sa.Column('profit_total', sa.BigInteger(), server_default='0', nullable=False),
                    sa.Column('cut_date', sa.Date(), server_default=sa.text(u'now()'), nullable=False),
                    sa.Column('create_at', sa.DateTime(), server_default=sa.text(u'now()'), nullable=False),
                    sa.Column('update_at', sa.DateTime(), server_default=sa.text(u'now()'), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('p_book')
    op.drop_table('mch_book')
    op.drop_table('dt_book')
    op.drop_table('bank_book')
    # ### end Alembic commands ###