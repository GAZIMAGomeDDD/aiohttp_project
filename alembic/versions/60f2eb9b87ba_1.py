"""1

Revision ID: 60f2eb9b87ba
Revises: 
Create Date: 2021-03-14 23:14:28.277059

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60f2eb9b87ba'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('user',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.Column('email', sa.String(), nullable=True),
                    sa.Column('password', sa.String(), nullable=True),
                    sa.Column('date', sa.DateTime(), nullable=True),
                    sa.Column('is_admin', sa.Boolean(), nullable=True),
                    sa.Column('disabled', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('email'),
                    sa.UniqueConstraint('name')
                    )
    op.create_table('posts',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('title', sa.String(length=250), nullable=True),
                    sa.Column('text', sa.String(), nullable=True),
                    sa.Column('date', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_posts_id'), 'posts', ['id'], unique=True)
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=True)
    op.add_column('posts', sa.Column('user', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'posts', 'user', ['user'], ['id'])


def downgrade():
    pass
