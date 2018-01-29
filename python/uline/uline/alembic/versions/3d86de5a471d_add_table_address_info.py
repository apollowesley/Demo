"""add table address_info

Revision ID: 3d86de5a471d
Revises: ca91215f8717
Create Date: 2017-06-15 11:46:31.187691

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3d86de5a471d'
down_revision = 'ca91215f8717'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('address_info',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('short_name', sa.String(length=128), nullable=False),
                    sa.Column('area_code', sa.String(length=16), nullable=False),
                    sa.Column('area_name', sa.String(length=128), nullable=False),
                    sa.Column('upper_code', sa.String(length=16), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('address_info')
    # ### end Alembic commands ###