"""2

Revision ID: 65d55c624798
Revises: 60f2eb9b87ba
Create Date: 2021-03-14 23:22:44.915894

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65d55c624798'
down_revision = '60f2eb9b87ba'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('description', sa.String(length=250), nullable=True))


def downgrade():
    pass
