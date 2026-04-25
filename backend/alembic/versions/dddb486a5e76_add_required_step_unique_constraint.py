"""add_required_step_unique_constraint

Revision ID: dddb486a5e76
Revises: b37190a455b1
Create Date: 2026-04-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "dddb486a5e76"
down_revision: Union[str, None] = "b37190a455b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_required_step_stage_seq",
        "required_step",
        ["stage_id", "sequence"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_required_step_stage_seq", "required_step", type_="unique")
