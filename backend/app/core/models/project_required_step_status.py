import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProjectRequiredStepStatus(Base):
    """프로젝트별 필수 Step 충족 상태 추적 테이블."""

    __tablename__ = "project_required_step_status"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("project.id", ondelete="CASCADE"), primary_key=True
    )
    required_step_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("required_step.id", ondelete="CASCADE"), primary_key=True
    )
    is_fulfilled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    fulfilled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped["Project"] = relationship()  # noqa: F821
    required_step: Mapped["RequiredStep"] = relationship()  # noqa: F821
