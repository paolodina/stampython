# coding=utf-8
"""Add gid to karma

Revision ID: 355236948ec7
Revises: 50aa2dc987c4
Create Date: 2017-04-25 09:50:51.991796

"""

# revision identifiers, used by Alembic.
revision = '355236948ec7'
down_revision = '50aa2dc987c4'
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    """
    Performs upgrade of database
    """

    op.add_column(u'karma', sa.Column('gid', sa.Text(), nullable=True))
    op.execute("""
                UPDATE
                   "karma"
                SET
                    gid = 0
            """)


def downgrade():
    """
    Performs database downgrade
    """

    op.drop_column(u'karma', 'gid')
