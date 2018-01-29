"""modify mch_user

Revision ID: 1ec9dd2313d6
Revises: cf74689258c2
Create Date: 2017-01-17 11:31:14.304722

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1ec9dd2313d6'
down_revision = 'cf74689258c2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('mch_user', sa.Column('wx_app_sub_mch_id', sa.String(length=64), nullable=True))


def downgrade():
    pass
