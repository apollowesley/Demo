"""mch_user table add ali_level column

Revision ID: bb1621aeadd0
Revises: 4c3d23c10f6a
Create Date: 2017-06-15 17:16:15.106720

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'bb1621aeadd0'
down_revision = '4c3d23c10f6a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(u'mch_user', sa.Column('ali_level', sa.String(length=32), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'mch_user', 'ali_level')
    # ### end Alembic commands ###
