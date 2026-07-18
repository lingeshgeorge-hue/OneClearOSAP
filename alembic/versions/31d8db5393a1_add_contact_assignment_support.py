"""add contact assignment support

Revision ID: 31d8db5393a1
Revises: fc4648ffd179
Create Date: 2026-07-17 22:09:20.703103

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '31d8db5393a1'
down_revision: Union[str, Sequence[str], None] = 'fc4648ffd179'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "contacts",
        sa.Column(
            "assigned_to",
            sa.Integer(),
            nullable=True
        )
    )

    op.create_foreign_key(
        "fk_contacts_assigned_to_users",
        "contacts",
        "users",
        ["assigned_to"],
        ["id"]
    )


def downgrade():
    op.drop_constraint(
        "fk_contacts_assigned_to_users",
        "contacts",
        type_="foreignkey"
    )

    op.drop_column(
        "contacts",
        "assigned_to"
    )