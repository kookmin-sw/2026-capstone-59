from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import ProjectNotFoundError
from app.core.models.project import Project, ProjectStage
from app.core.models.stage import Stage
from app.core.schemas.stage import StageListItem, StageListResponse


def list_stages(db: Session, project_id: UUID) -> dict:
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.is_deleted == False,  # noqa: E712
        )
        .first()
    )
    if not project:
        raise ProjectNotFoundError()

    rows = (
        db.query(ProjectStage, Stage)
        .join(Stage, Stage.id == ProjectStage.stage_id)
        .filter(ProjectStage.project_id == project_id)
        .order_by(Stage.sequence)
        .all()
    )

    stages = [
        StageListItem(
            stage_id=stage.id,
            stage_sequence=stage.sequence,
            stage_name=stage.name,
            is_active=ps.is_active,
        )
        for ps, stage in rows
    ]

    return StageListResponse(stages=stages).model_dump()
