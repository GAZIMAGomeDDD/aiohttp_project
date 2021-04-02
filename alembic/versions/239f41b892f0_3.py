"""3

Revision ID: 239f41b892f0
Revises: 65d55c624798
Create Date: 2021-03-20 22:05:05.011853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '239f41b892f0'
down_revision = '65d55c624798'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('avatar', sa.String()))


def downgrade():
    pass
