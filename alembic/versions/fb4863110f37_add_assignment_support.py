"""Add assignment support

Revision ID: fb4863110f37
Revises: 72511ec64ae4
Create Date: 2026-07-08 01:12:18.661808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb4863110f37'
down_revision: Union[str, Sequence[str], None] = '72511ec64ae4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("leads") as batch_op:
        batch_op.alter_column(
            "assigned_to",
            existing_type=sa.String(),
            type_=sa.Integer(),
            existing_nullable=True,
        )

        batch_op.create_foreign_key(
            "fk_leads_assigned_to_users",
            "users",
            ["assigned_to"],
            ["id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("leads") as batch_op:
        batch_op.drop_constraint(
            "fk_leads_assigned_to_users",
            type_="foreignkey"
        )

        batch_op.alter_column(
            "assigned_to",
            existing_type=sa.Integer(),
            type_=sa.String(),
            existing_nullable=True,
        )