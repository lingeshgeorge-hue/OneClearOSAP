"""synchronize contacts foreign key and lead status constraint

Revision ID: e1460c03e197
Revises: 520c1009d06b
Create Date: 2026-07-19
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e1460c03e197"
down_revision: Union[str, Sequence[str], None] = "520c1009d06b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite cannot directly ALTER existing constraints.
    # Batch mode safely recreates the affected tables.

    with op.batch_alter_table(
        "contacts",
        schema=None,
    ) as batch_op:
        batch_op.create_foreign_key(
            "fk_contacts_assigned_to_users",
            "users",
            ["assigned_to"],
            ["id"],
        )

    with op.batch_alter_table(
        "leads",
        schema=None,
    ) as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.String(),
            nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table(
        "leads",
        schema=None,
    ) as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.String(),
            nullable=True,
        )

    with op.batch_alter_table(
        "contacts",
        schema=None,
    ) as batch_op:
        batch_op.drop_constraint(
            "fk_contacts_assigned_to_users",
            type_="foreignkey",
        )