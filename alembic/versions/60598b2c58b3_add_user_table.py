"""Add user table

Revision ID: 60598b2c58b3
Revises: 1bf34ea5889b
Create Date: 2023-05-14 14:34:26.615147

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60598b2c58b3'
down_revision = '1bf34ea5889b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('email', sa.String(255), nullable=False),
                    sa.Column('password', sa.String(255), nullable=False),
                    sa.Column('time', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('email')
                    )
    pass


def downgrade() -> None:
    op.drop_table('users')
    pass
