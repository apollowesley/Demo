"""add rate columns

Revision ID: 55a0d7cac997
Revises: 9f1490e96904
Create Date: 2017-02-16 15:20:02.835748

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from uline.public.db import initdb
# from model.uline.user import DtUser, MchUser

initdb()
Session = sessionmaker()


# revision identifiers, used by Alembic.
revision = '55a0d7cac997'
down_revision = '9f1490e96904'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'dt_user', sa.Column('rate', sa.SmallInteger)
    )
    op.add_column(
        'mch_user', sa.Column('rate', sa.SmallInteger)
    )

    bind = op.get_bind()
    session = Session(bind=bind)

    # session.query(DtUser).update({'rate': 3})
    # session.query(MchUser).update({'rate': 3})
    session.execute('update dt_user set rate=3;')
    session.execute('update mch_user set rate=3;')
    session.commit()


def downgrade():
    op.drop_column('dt_user', 'rate')
    op.drop_column('mch_user', 'rate')
