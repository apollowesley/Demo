"""Edit email not unique in dt_subuser and dt_user tables

Revision ID: c209ce9aef79
Revises: 7f9441cd6b8e
Create Date: 2017-04-05 17:48:53.315027

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c209ce9aef79'
down_revision = '7f9441cd6b8e'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP INDEX IF EXISTS dt_subuser_email_uindex")
    op.create_index('dt_subuser_email_uindex',
                    'dt_subuser', ['email'], unique=False)
    op.drop_index('dt_user_email_uindex', table_name='dt_user')
    op.create_index('dt_user_email_uindex', 'dt_user', ['email'], unique=False)


def downgrade():
    op.drop_index('dt_user_email_uindex', table_name='dt_user')
    op.create_index('dt_user_email_uindex', 'dt_user', ['email'], unique=True)
    op.drop_index('dt_subuser_email_uindex', table_name='dt_subuser')
