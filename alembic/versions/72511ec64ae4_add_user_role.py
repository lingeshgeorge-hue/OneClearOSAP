"""Add user role

Revision ID: 72511ec64ae4
Revises: 9fb2b6b150b4
Create Date: 2026-07-08 00:49:02.190243

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72511ec64ae4'
down_revision: Union[str, Sequence[str], None] = '9fb2b6b150b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "role",
            existing_type=sa.String(),
            nullable=False,
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "role",
            existing_type=sa.String(),
            nullable=True,
        )