"""4

Revision ID: 1477193d9564
Revises: 239f41b892f0
Create Date: 2021-03-24 23:56:55.203473

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1477193d9564'
down_revision = '239f41b892f0'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('title_image', sa.String()))


def downgrade():
    pass
