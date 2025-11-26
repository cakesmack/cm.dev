"""Add is_featured to projects

Revision ID: a1b2c3d4e5f6
Revises: 008c9d9fcd91
Create Date: 2025-11-13 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '008c9d9fcd91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add is_featured column to projects table
    op.add_column('projects', sa.Column('is_featured', sa.Boolean(), nullable=True, server_default='0'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove is_featured column from projects table
    op.drop_column('projects', 'is_featured')
