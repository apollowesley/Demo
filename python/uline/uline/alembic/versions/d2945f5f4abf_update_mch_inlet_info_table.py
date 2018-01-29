"""update mch_inlet_info table

Revision ID: d2945f5f4abf
Revises: 00d3a0303f0c
Create Date: 2017-03-13 15:13:13.898386

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2945f5f4abf'
down_revision = '00d3a0303f0c'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column(
        'mch_inlet_info', sa.Column('pay_notify_url', sa.String(200), nullable=True)
    )


def downgrade():
    pass
