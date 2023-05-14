"""add last few columns to posts table

Revision ID: b96ded8d0052
Revises: e14f21b934ea
Create Date: 2023-05-14 14:46:22.865403

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b96ded8d0052'
down_revision = 'e14f21b934ea'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', 
                  sa.Column('published', sa.Boolean(), nullable=False, server_default='1', default=True)) 
    op.add_column('posts', 
                  sa.Column('time', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False)
                  )
    pass


def downgrade() -> None:
    op.drop_column('posts', 'published')
    op.drop_column('posts', 'time')
    pass
