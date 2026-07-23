"""Add manager hierarchy to users

Revision ID: d85ea82e1558
Revises: 54ee320c1a3c
Create Date: 2026-07-23 22:45:17.881612

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd85ea82e1558'
down_revision: Union[str, Sequence[str], None] = '54ee320c1a3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add self-referencing manager hierarchy."""

    with op.batch_alter_table(
        "users",
        schema=None,
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "manager_id",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.create_index(
            "ix_users_manager_id",
            ["manager_id"],
            unique=False,
        )

        batch_op.create_foreign_key(
            "fk_users_manager_id_users",
            "users",
            ["manager_id"],
            ["id"],
        )


def downgrade() -> None:
    """Remove self-referencing manager hierarchy."""

    with op.batch_alter_table(
        "users",
        schema=None,
    ) as batch_op:

        batch_op.drop_constraint(
            "fk_users_manager_id_users",
            type_="foreignkey",
        )

        batch_op.drop_index(
            "ix_users_manager_id"
        )

        batch_op.drop_column(
            "manager_id"
        )
