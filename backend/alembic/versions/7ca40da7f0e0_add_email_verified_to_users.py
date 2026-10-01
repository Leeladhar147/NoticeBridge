"""add_email_verified_to_users

Revision ID: 7ca40da7f0e0
Revises: 85cc652a30ff
Create Date: 2026-10-01 16:54:13.616335

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ca40da7f0e0'
down_revision: Union[str, Sequence[str], None] = '85cc652a30ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), server_default='false', nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'email_verified')
