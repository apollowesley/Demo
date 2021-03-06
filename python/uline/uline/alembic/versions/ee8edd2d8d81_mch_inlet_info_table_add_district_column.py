"""mch_inlet_info table add district column

Revision ID: ee8edd2d8d81
Revises: bb1621aeadd0
Create Date: 2017-06-15 19:58:44.422283

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ee8edd2d8d81'
down_revision = 'bb1621aeadd0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mch_inlet_info', sa.Column('district', sa.String(length=32), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('mch_inlet_info', 'district')
    # ### end Alembic commands ###
