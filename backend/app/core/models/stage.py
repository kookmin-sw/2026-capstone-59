import uuid

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Stage(Base):
    __tablename__ = "stage"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)

    project_stages: Mapped[list["ProjectStage"]] = relationship(  # noqa: F821
        back_populates="stage"
    )
    steps: Mapped[list["Step"]] = relationship(back_populates="stage")  # noqa: F821
