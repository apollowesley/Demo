"""create download table

Revision ID: 9f1490e96904
Revises: d2945f5f4abf
Create Date: 2017-02-15 17:08:44.538898

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9f1490e96904'
down_revision = 'd2945f5f4abf'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('order_download_info',
                    sa.Column('order_id', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('user_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('file', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
                    sa.Column('type', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('status', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('platform', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('create_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('update_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('order_id', name=u'order_download_info_pkey')
                    )


def downgrade():
    op.drop_table('order_download_info')
