"""modify dt_user

Revision ID: 00d3a0303f0c
Revises: 1ec9dd2313d6
Create Date: 2017-01-17 14:28:44.933520

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00d3a0303f0c'
down_revision = '1ec9dd2313d6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('dt_user', sa.Column('wx_app_sub_mch_id', sa.String(length=64), nullable=True))


def downgrade():
    pass
