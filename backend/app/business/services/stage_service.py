from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import ProjectNotFoundError
from app.core.models.project import Project as ProjectModel
from app.core.models.project import ProjectStage as ProjectStageModel
from app.core.models.stage import Stage as StageModel
from app.core.schemas.stage import StageListItem, StageListResponse


def list_stages(db: Session, project_id: UUID) -> StageListResponse:
    project = (
        db.query(ProjectModel)
        .filter(
            ProjectModel.id == project_id,
            ProjectModel.is_deleted.is_(False),
        )
        .first()
    )
    if not project:
        raise ProjectNotFoundError()

    rows = (
        db.query(ProjectStageModel, StageModel)
        .join(StageModel, StageModel.id == ProjectStageModel.stage_id)
        .filter(ProjectStageModel.project_id == project_id)
        .order_by(StageModel.sequence)
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

    return StageListResponse(stages=stages)
