"""add content column to posts table

Revision ID: 1bf34ea5889b
Revises: d9c7efe0888e
Create Date: 2023-05-14 14:30:05.088679

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1bf34ea5889b'
down_revision = 'd9c7efe0888e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts',
                  sa.Column('content', sa.String(255), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
