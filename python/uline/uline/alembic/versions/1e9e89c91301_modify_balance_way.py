"""modify balance_way

Revision ID: 1e9e89c91301
Revises: 902d28b76374
Create Date: 2017-01-09 18:09:57.080376

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
Session = sessionmaker()


# revision identifiers, used by Alembic.
revision = '1e9e89c91301'
down_revision = '902d28b76374'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('mch_balance', 'balance_way', server_default='1',
                    existing_type=sa.Integer(), existing_nullable=False, existing_server_default='0')
    op.alter_column('dt_balance', 'balance_way', server_default='1', existing_type=sa.Integer(),
                    existing_nullable=False, existing_server_default='0')
    # ### end Alembic commands ###
    bind = op.get_bind()
    session = Session(bind=bind)
    session.commit()


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
