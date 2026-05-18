"""add design_export_job table

비동기 폴링 방식의 design-export — 작업별 row 생성 후 폴링으로 결과 조회.

Revision ID: d8e2c1a04b91
Revises: c3a91f4b27e0
Create Date: 2026-05-18 00:01:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "d8e2c1a04b91"
down_revision: Union[str, None] = "c3a91f4b27e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "design_export_job",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            UUID(as_uuid=True),
            sa.ForeignKey("project.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=16),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("markdown", sa.Text(), nullable=True),
        sa.Column("filename", sa.String(length=255), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_design_export_job_project_id",
        "design_export_job",
        ["project_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_design_export_job_project_id", table_name="design_export_job")
    op.drop_table("design_export_job")
