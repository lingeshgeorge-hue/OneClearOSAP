"""add client module and synchronize crm schema

Revision ID: 520c1009d06b
Revises: 31d8db5393a1
Create Date: 2026-07-18 23:11:08.106645
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "520c1009d06b"
down_revision: Union[str, Sequence[str], None] = "31d8db5393a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # =========================================================
    # OPPORTUNITIES
    # Rename opportunity_name -> name without losing data
    # =========================================================

    with op.batch_alter_table("opportunities") as batch_op:
        batch_op.alter_column(
            "opportunity_name",
            new_column_name="name",
            existing_type=sa.String(),
            existing_nullable=False,
        )

    # =========================================================
    # PROPOSALS
    # Upgrade existing proposal structure while preserving data
    # =========================================================

    with op.batch_alter_table("proposals") as batch_op:

        # Preserve existing proposed_value data by renaming it
        batch_op.alter_column(
            "proposed_value",
            new_column_name="pricing_value",
            existing_type=sa.Float(),
            existing_nullable=False,
        )

        # Add new columns temporarily nullable where necessary
        batch_op.add_column(
            sa.Column(
                "proposal_number",
                sa.String(),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "version",
                sa.Integer(),
                nullable=True,
                server_default="1",
            )
        )

        batch_op.add_column(
            sa.Column(
                "services",
                sa.Text(),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "monthly_revenue",
                sa.Float(),
                nullable=True,
                server_default="0",
            )
        )

        batch_op.add_column(
            sa.Column(
                "annual_revenue",
                sa.Float(),
                nullable=True,
                server_default="0",
            )
        )

        batch_op.add_column(
            sa.Column(
                "assigned_to",
                sa.Integer(),
                nullable=True,
            )
        )

    # Generate proposal numbers for any existing proposal rows
    op.execute(
        """
        UPDATE proposals
        SET proposal_number =
            'OCP-2026-' || printf('%04d', id)
        WHERE proposal_number IS NULL
        """
    )

    # Now enforce proposal_number NOT NULL,
    # add unique constraint and assigned_to foreign key
    with op.batch_alter_table("proposals") as batch_op:

        batch_op.alter_column(
            "proposal_number",
            existing_type=sa.String(),
            nullable=False,
        )

        batch_op.create_unique_constraint(
            "uq_proposals_proposal_number",
            ["proposal_number"],
        )

        batch_op.create_foreign_key(
            "fk_proposals_assigned_to_users",
            "users",
            ["assigned_to"],
            ["id"],
        )

    # =========================================================
    # CLIENTS
    # Extend existing clients table
    # =========================================================

    with op.batch_alter_table("clients") as batch_op:

        batch_op.add_column(
            sa.Column(
                "lead_id",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "opportunity_id",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "notes",
                sa.Text(),
                nullable=True,
            )
        )

        batch_op.create_foreign_key(
            "fk_clients_lead_id_leads",
            "leads",
            ["lead_id"],
            ["id"],
        )

        batch_op.create_foreign_key(
            "fk_clients_opportunity_id_opportunities",
            "opportunities",
            ["opportunity_id"],
            ["id"],
        )

    # clients table is currently empty, so these can safely
    # become NOT NULL after the columns have been created.

    with op.batch_alter_table("clients") as batch_op:

        batch_op.alter_column(
            "lead_id",
            existing_type=sa.Integer(),
            nullable=False,
        )

        batch_op.alter_column(
            "opportunity_id",
            existing_type=sa.Integer(),
            nullable=False,
        )


def downgrade() -> None:

    # =========================================================
    # CLIENTS
    # =========================================================

    with op.batch_alter_table("clients") as batch_op:

        batch_op.drop_constraint(
            "fk_clients_opportunity_id_opportunities",
            type_="foreignkey",
        )

        batch_op.drop_constraint(
            "fk_clients_lead_id_leads",
            type_="foreignkey",
        )

        batch_op.drop_column("notes")
        batch_op.drop_column("opportunity_id")
        batch_op.drop_column("lead_id")

    # =========================================================
    # PROPOSALS
    # =========================================================

    with op.batch_alter_table("proposals") as batch_op:

        batch_op.drop_constraint(
            "fk_proposals_assigned_to_users",
            type_="foreignkey",
        )

        batch_op.drop_constraint(
            "uq_proposals_proposal_number",
            type_="unique",
        )

        batch_op.drop_column("assigned_to")
        batch_op.drop_column("annual_revenue")
        batch_op.drop_column("monthly_revenue")
        batch_op.drop_column("services")
        batch_op.drop_column("version")
        batch_op.drop_column("proposal_number")

        batch_op.alter_column(
            "pricing_value",
            new_column_name="proposed_value",
            existing_type=sa.Float(),
            existing_nullable=False,
        )

    # =========================================================
    # OPPORTUNITIES
    # =========================================================

    with op.batch_alter_table("opportunities") as batch_op:

        batch_op.alter_column(
            "name",
            new_column_name="opportunity_name",
            existing_type=sa.String(),
            existing_nullable=False,
        )