"""Stage repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.models.stage import Stage
from app.core.models.project import ProjectStage
from app.core.models.required_step import RequiredStep
from app.core.models.project_required_step_status import ProjectRequiredStepStatus


def get_all_stages_ordered(db: Session) -> list[Stage]:
    return db.query(Stage).order_by(Stage.sequence).all()


def get_stage_by_sequence(db: Session, sequence: int) -> Stage | None:
    return db.query(Stage).filter(Stage.sequence == sequence).first()


def get_stage_ids_after_sequence(db: Session, sequence: int) -> list[UUID]:
    return [
        sid for (sid,) in db.query(Stage.id).filter(Stage.sequence > sequence).all()
    ]


def get_project_stages_with_completion(
    db: Session, project_id: UUID
) -> list[tuple[ProjectStage, Stage, bool]]:

    unfulfilled_exists = (
        db.query(RequiredStep.id)
        .outerjoin(
            ProjectRequiredStepStatus,
            and_(
                ProjectRequiredStepStatus.required_step_id == RequiredStep.id,
                ProjectRequiredStepStatus.project_id == project_id,
            ),
        )
        .filter(
            RequiredStep.stage_id == Stage.id,
            or_(
                ProjectRequiredStepStatus.is_fulfilled.is_(None),
                ProjectRequiredStepStatus.is_fulfilled == False,
            ),
        )
        .exists()
    )

    return (
        db.query(ProjectStage, Stage, (~unfulfilled_exists).label("is_completed"))
        .join(Stage, Stage.id == ProjectStage.stage_id)
        .filter(ProjectStage.project_id == project_id)
        .order_by(Stage.sequence)
        .all()
    )
