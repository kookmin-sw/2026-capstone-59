"""rename required_step fulfillment columns

Revision ID: d2b8f4c6e1a3
Revises: 59036a725c7c
Create Date: 2026-05-07 00:00:00.000000

required_step 테이블 컬럼 명 변경:
- fulfillment_aspects   → fulfillment_criteria
- fulfillment_threshold → minimum_fulfillment_count
"""
from typing import Sequence, Union

from alembic import op


revision: str = "d2b8f4c6e1a3"
down_revision: Union[str, Sequence[str], None] = "59036a725c7c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "required_step", "fulfillment_aspects", new_column_name="fulfillment_criteria"
    )
    op.alter_column(
        "required_step",
        "fulfillment_threshold",
        new_column_name="minimum_fulfillment_count",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "required_step",
        "minimum_fulfillment_count",
        new_column_name="fulfillment_threshold",
    )
    op.alter_column(
        "required_step", "fulfillment_criteria", new_column_name="fulfillment_aspects"
    )
