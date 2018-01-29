"""Edit email is not unique in dt_inlet_info table

Revision ID: 9041f2ffdbbb
Revises: c7dfc5bb914a
Create Date: 2017-04-05 16:27:59.393286

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9041f2ffdbbb'
down_revision = 'c7dfc5bb914a'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index('dt_inlet_info_email_uindex', table_name='dt_inlet_info')
    op.create_index('dt_inlet_info_email_uindex',
                    'dt_inlet_info', ['email'], unique=False)


def downgrade():
    op.drop_index('dt_inlet_info_email_uindex', table_name='dt_inlet_info')
    op.create_index('dt_inlet_info_email_uindex',
                    'dt_inlet_info', ['email'], unique=True)
