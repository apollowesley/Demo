"""modify comment column

Revision ID: 01cac522cc32
Revises: 55a0d7cac997
Create Date: 2017-02-16 11:00:30.242410

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01cac522cc32'
down_revision = '55a0d7cac997'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('auth_mch_info', 'comment', type_=sa.TEXT, existing_type=sa.VARCHAR)
    op.alter_column('auth_dt_info', 'comment', type_=sa.TEXT, existing_type=sa.VARCHAR)


def downgrade():
    pass
