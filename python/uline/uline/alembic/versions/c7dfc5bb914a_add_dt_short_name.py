"""Add dt_short_name

Revision ID: c7dfc5bb914a
Revises: fd36934be52d
Create Date: 2017-03-23 17:21:49.036240

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7dfc5bb914a'
down_revision = 'fd36934be52d'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('dt_inlet_info', sa.Column('dt_short_name', sa.String(length=64), nullable=True))


def downgrade():
    op.drop_column('dt_inlet_info', 'dt_short_name')
