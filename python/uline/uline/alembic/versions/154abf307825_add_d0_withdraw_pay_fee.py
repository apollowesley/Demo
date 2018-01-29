"""add d0_withdraw_fee table

Revision ID: 154abf307825
Revises: 79cecbbb4f69
Create Date: 2017-04-18 17:09:30.131057

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '154abf307825'
down_revision = 'b1a96f4d594a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('d0_withdraw_fee',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('role', sa.BigInteger(), nullable=False),
                    sa.Column('role_type', sa.String(
                        length=10), nullable=False),
                    sa.Column('wx', sa.Integer(), nullable=True),
                    sa.Column('alipay', sa.Integer(), nullable=True),
                    sa.Column('create_at', sa.DateTime(),
                              server_default=sa.text(u'now()'), nullable=False),
                    sa.Column('update_at', sa.DateTime(),
                              server_default=sa.text(u'now()'), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('d0_withdraw_fee')
