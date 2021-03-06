"""password length and wx_inlet Null

Revision ID: 98b49652632b
Revises: 4c070deaec2e
Create Date: 2016-12-06 17:53:06.410406

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98b49652632b'
down_revision = '4c070deaec2e'
branch_labels = None
depends_on = None


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('bk_user', 'password',
                    existing_type=sa.VARCHAR(length=64),
                    type_=sa.String(length=256),
                    existing_nullable=False)
    op.alter_column('dt_user', 'password',
                    existing_type=sa.VARCHAR(length=64),
                    type_=sa.String(length=256),
                    existing_nullable=False)
    op.alter_column('mch_user', 'mch_pay_key',
                    existing_type=sa.VARCHAR(length=64),
                    nullable=True)
    op.alter_column('mch_user', 'password',
                    existing_type=sa.VARCHAR(length=64),
                    type_=sa.String(length=256),
                    existing_nullable=False)
    op.alter_column('mch_user', 'wx_sub_mch_id',
                    existing_type=sa.VARCHAR(length=64),
                    nullable=True)
    op.alter_column('ub_user', 'password',
                    existing_type=sa.VARCHAR(length=64),
                    type_=sa.String(length=256),
                    existing_nullable=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('ub_user', 'password',
                    existing_type=sa.String(length=256),
                    type_=sa.VARCHAR(length=64),
                    existing_nullable=False)
    op.alter_column('mch_user', 'wx_sub_mch_id',
                    existing_type=sa.VARCHAR(length=64),
                    nullable=False)
    op.alter_column('mch_user', 'password',
                    existing_type=sa.String(length=256),
                    type_=sa.VARCHAR(length=64),
                    existing_nullable=False)
    op.alter_column('mch_user', 'mch_pay_key',
                    existing_type=sa.VARCHAR(length=64),
                    nullable=False)
    op.alter_column('dt_user', 'password',
                    existing_type=sa.String(length=256),
                    type_=sa.VARCHAR(length=64),
                    existing_nullable=False)
    op.alter_column('bk_user', 'password',
                    existing_type=sa.String(length=256),
                    type_=sa.VARCHAR(length=64),
                    existing_nullable=False)
    ### end Alembic commands ###
