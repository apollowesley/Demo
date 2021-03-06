"""mch_paymnet dt_payment table add column

Revision ID: 07bd153f9dbb
Revises: 724cd912228b
Create Date: 2017-08-25 10:05:13.073744

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '07bd153f9dbb'
down_revision = '724cd912228b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dt_payment', sa.Column('withdraw_rate', sa.Integer(), nullable=True))
    op.add_column('mch_payment', sa.Column('withdraw_rate', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('mch_payment', 'withdraw_rate')
    op.drop_column('dt_payment', 'withdraw_rate')
    # ### end Alembic commands ###
