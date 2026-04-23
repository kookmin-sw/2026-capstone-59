import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RequiredStep(Base):
    __tablename__ = "required_step"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stage_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stage.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    toast_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    template_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    stage: Mapped["Stage"] = relationship(back_populates="required_steps")  # noqa: F821
