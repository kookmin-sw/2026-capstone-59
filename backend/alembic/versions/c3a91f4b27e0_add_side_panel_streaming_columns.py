"""add side panel streaming columns to step_content

비동기 폴링 방식의 side panel 생성 — chunk 도착마다 streaming_raw 누적,
폴링 endpoint 가 streaming_status 와 함께 노출.

Revision ID: c3a91f4b27e0
Revises: 8d7474fd5838
Create Date: 2026-05-18 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c3a91f4b27e0"
down_revision: Union[str, None] = "8d7474fd5838"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "step_content",
        sa.Column(
            "streaming_status",
            sa.String(length=16),
            nullable=False,
            server_default="idle",
        ),
    )
    op.add_column(
        "step_content",
        sa.Column(
            "streaming_raw",
            sa.Text(),
            nullable=False,
            server_default="",
        ),
    )


def downgrade() -> None:
    op.drop_column("step_content", "streaming_raw")
    op.drop_column("step_content", "streaming_status")
