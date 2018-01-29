"""add dist license

Revision ID: 20e682fe2cc8
Revises: 1e9e89c91301
Create Date: 2017-02-05 10:22:01.992198

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from uline.public.db import initdb

initdb()
Session = sessionmaker()


# revision identifiers, used by Alembic.
revision = '20e682fe2cc8'
down_revision = '1e9e89c91301'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'dt_inlet_info', sa.Column('license_num', sa.String(32))
    )
    op.add_column(
        'dt_inlet_info', sa.Column('license_start_date', sa.Date)
    )
    op.add_column(
        'dt_inlet_info', sa.Column('license_end_date', sa.Date, nullable=True)
    )
    op.add_column(
        'dt_inlet_info', sa.Column('license_period', sa.SmallInteger, nullable=True)
    )
    op.add_column(
        'dt_inlet_info', sa.Column('license_scope', sa.String(500), nullable=True)
    )
    op.add_column(
        'dt_inlet_info', sa.Column('license_img', sa.String(200))
    )

    op.add_column(
        'mch_inlet_info', sa.Column('license_num', sa.String(32))
    )
    op.add_column(
        'mch_inlet_info', sa.Column('license_start_date', sa.Date)
    )
    op.add_column(
        'mch_inlet_info', sa.Column('license_end_date', sa.Date, nullable=True)
    )
    op.add_column(
        'mch_inlet_info', sa.Column('license_period', sa.SmallInteger, nullable=True)
    )
    op.add_column(
        'mch_inlet_info', sa.Column('license_scope', sa.String(500), nullable=True)
    )
    op.add_column(
        'mch_inlet_info', sa.Column('license_img', sa.String(200))
    )


def downgrade():
    op.drop_column(
        'dt_inlet_info', sa.Column('license_num', sa.String(32))
    )
    op.drop_column(
        'dt_inlet_info', sa.Column('license_start_date', sa.Date)
    )
    op.drop_column(
        'dt_inlet_info', sa.Column('license_end_date', sa.Date, nullable=True)
    )
    op.drop_column(
        'dt_inlet_info', sa.Column('license_period', sa.SmallInteger, nullable=True)
    )
    op.drop_column(
        'dt_inlet_info', sa.Column('license_scope', sa.String(500), nullable=True)
    )
    op.drop_column(
        'dt_inlet_info', sa.Column('license_img', sa.String(200))
    )

    op.drop_column(
        'mch_inlet_info', sa.Column('license_num', sa.String(32))
    )
    op.drop_column(
        'mch_inlet_info', sa.Column('license_start_date', sa.Date)
    )
    op.drop_column(
        'mch_inlet_info', sa.Column('license_end_date', sa.Date, nullable=True)
    )
    op.drop_column(
        'mch_inlet_info', sa.Column('license_period', sa.SmallInteger, nullable=True)
    )
    op.drop_column(
        'mch_inlet_info', sa.Column('license_scope', sa.String(500), nullable=True)
    )
    op.drop_column(
        'mch_inlet_info', sa.Column('license_img', sa.String(200))
    )
