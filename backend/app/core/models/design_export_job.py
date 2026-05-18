import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DesignExportJob(Base):
    """Design Export 비동기 폴링용 job 레코드.

    POST /projects/{project_id}/design-export-start 에서 row 생성 후
    AI Lambda 가 LLM 작업을 수행하며 status / markdown / filename 을 채운다.
    프론트는 GET /projects/{project_id}/design-export-jobs/{job_id} 로 폴링.

    클라이언트 끊김 시 결과는 휘발성으로 처리 — 별도 cleanup 정책으로 오래된 row 정리.
    """

    __tablename__ = "design_export_job"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # pending / done / error
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, server_default="pending"
    )
    markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
