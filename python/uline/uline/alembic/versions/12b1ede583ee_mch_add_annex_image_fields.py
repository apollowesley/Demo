"""mch add annex image fields

Revision ID: 12b1ede583ee
Revises: eff79cb040e9
Create Date: 2017-07-24 12:31:00.654777

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '12b1ede583ee'
down_revision = 'eff79cb040e9'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mch_inlet_info', sa.Column('annex_img1', sa.String(length=200), nullable=True))
    op.add_column('mch_inlet_info', sa.Column('annex_img2', sa.String(length=200), nullable=True))
    op.add_column('mch_inlet_info', sa.Column('annex_img3', sa.String(length=200), nullable=True))
    op.add_column('mch_inlet_info', sa.Column('annex_img4', sa.String(length=200), nullable=True))
    op.add_column('mch_inlet_info', sa.Column('annex_img5', sa.String(length=200), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('mch_inlet_info', 'annex_img5')
    op.drop_column('mch_inlet_info', 'annex_img4')
    op.drop_column('mch_inlet_info', 'annex_img3')
    op.drop_column('mch_inlet_info', 'annex_img2')
    op.drop_column('mch_inlet_info', 'annex_img1')
    # ### end Alembic commands ###