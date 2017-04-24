"""Use gid in alias

Revision ID: 50aa2dc987c4
Revises: 81a858b4f7f4
Create Date: 2017-04-25 00:01:51.547257

"""

# revision identifiers, used by Alembic.
revision = '50aa2dc987c4'
down_revision = '81a858b4f7f4'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(u'alias', sa.Column('gid', sa.Text(), nullable=True))
    op.execute("""
                    UPDATE
                       "alias"
                    SET
                        gid = 0
                """)


def downgrade():
    op.drop_column(u'alias', 'gid')
