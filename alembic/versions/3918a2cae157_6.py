"""6

Revision ID: 3918a2cae157
Revises: faee179d52d4
Create Date: 2021-03-31 05:34:21.409362

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3918a2cae157'
down_revision = 'faee179d52d4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('slug', sa.String()))


def downgrade():
    pass
