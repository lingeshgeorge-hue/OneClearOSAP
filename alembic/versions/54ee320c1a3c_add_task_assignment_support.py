"""Add task assignment support

Revision ID: 54ee320c1a3c
Revises: e1460c03e197
Create Date: 2026-07-21 23:11:16.352004
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "54ee320c1a3c"
down_revision: Union[str, Sequence[str], None] = "e1460c03e197"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    with op.batch_alter_table("tasks") as batch_op:
        batch_op.add_column(
            sa.Column("assigned_to", sa.Integer(), nullable=True)
        )

        batch_op.add_column(
            sa.Column("completed_at", sa.DateTime(), nullable=True)
        )

        batch_op.create_foreign_key(
            "fk_tasks_assigned_to_users",
            "users",
            ["assigned_to"],
            ["id"],
        )


def downgrade() -> None:
    """Downgrade schema."""

    with op.batch_alter_table("tasks") as batch_op:
        batch_op.drop_constraint(
            "fk_tasks_assigned_to_users",
            type_="foreignkey",
        )

        batch_op.drop_column("completed_at")

        batch_op.drop_column("assigned_to")