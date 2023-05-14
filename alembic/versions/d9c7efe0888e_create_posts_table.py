"""create posts table

Revision ID: d9c7efe0888e
Revises: 
Create Date: 2023-05-14 14:21:26.020973

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9c7efe0888e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('posts', 
                    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('title', sa.String(255), nullable=False))
    pass


def downgrade() -> None:
    op.drop_table('posts')
    pass
