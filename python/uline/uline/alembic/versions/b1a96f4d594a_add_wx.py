"""add wx

Revision ID: b1a96f4d594a
Revises: 04bef4af514a
Create Date: 2017-05-02 19:16:54.869456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1a96f4d594a'
down_revision = '04bef4af514a'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mch_subuser',
    sa.Column('mch_sub_id', sa.BigInteger(), nullable=False),
    sa.Column('mch_id', sa.BigInteger(), nullable=True),
    sa.Column('scene_id', sa.String(length=256), nullable=True),
    sa.Column('mch_sub_name', sa.String(length=64), nullable=False),
    sa.Column('login_name', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=False),
    sa.Column('phone', sa.String(length=64), nullable=False),
    sa.Column('password', sa.String(length=256), nullable=False),
    sa.Column('wx_id', sa.String(length=64), nullable=True),
    sa.Column('wx_open_id', sa.String(length=64), nullable=True),
    sa.Column('status', sa.Integer(), server_default=sa.text(u'1'), nullable=False),
    sa.Column('create_at', sa.DateTime(), server_default=sa.text(u'now()'), nullable=False),
    sa.Column('update_at', sa.DateTime(), server_default=sa.text(u'now()'), nullable=False),
    sa.PrimaryKeyConstraint('mch_sub_id'),
    sa.UniqueConstraint('login_name'),
    sa.UniqueConstraint('scene_id')
    )

    op.add_column(u'mch_inlet_info', sa.Column('open_or_close', sa.Integer(), server_default=sa.text(u'1'), nullable=True))
    op.add_column(u'mch_payment', sa.Column('open_status', sa.Integer(), server_default=sa.text(u'3'), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'mch_payment', 'open_status')
    op.drop_column(u'mch_inlet_info', 'open_or_close')
    op.drop_index('mch_subuser_index', table_name='mch_subuser')
    op.drop_table('mch_subuser')
    # ### end Alembic commands ###