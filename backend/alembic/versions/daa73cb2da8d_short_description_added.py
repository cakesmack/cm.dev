"""Short description added

Revision ID: daa73cb2da8d
Revises: a1b2c3d4e5f6
Create Date: 2025-11-17 23:31:54.400376

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'daa73cb2da8d'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add short_description column to projects table
    op.add_column('projects', sa.Column('short_description', sa.String(length=200), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove short_description column from projects table
    op.drop_column('projects', 'short_description')
