"""merge 3672 and c209

Revision ID: 4eb454bdb4e7
Revises: 36728edc9201, c209ce9aef79
Create Date: 2017-04-07 09:51:01.900890

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4eb454bdb4e7'
down_revision = ('36728edc9201', 'c209ce9aef79')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
