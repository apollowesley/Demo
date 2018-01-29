"""Add chain related fields

Revision ID: 301ce165cc36
Revises: 6ec19e689a73
Create Date: 2017-03-21 17:51:58.650079

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '301ce165cc36'
down_revision = '6ec19e689a73'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('dt_inlet_info', sa.Column('parent_id', sa.BigInteger(), nullable=True))
    op.add_column('mch_inlet_info', sa.Column('cs_id', sa.BigInteger(), nullable=True))


def downgrade():
    op.drop_column('mch_inlet_info', 'cs_id')
    op.drop_column('dt_inlet_info', 'parent_id')
