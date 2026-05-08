from uuid import UUID

from sqlalchemy.orm import Session

from app.business.services import project_service
from app.core.repositories import project as project_repo
from app.core.schemas.stage import StageListItem, StageListResponse


def list_stages(db: Session, project_id: UUID) -> StageListResponse:
    project_service.get_project_or_raise(db, project_id)

    rows = project_repo.get_project_stages_with_stage(db, project_id)

    return StageListResponse(
        stages=[
            StageListItem(
                stage_id=stage.id,
                stage_sequence=stage.sequence,
                stage_name=stage.name,
                is_active=ps.is_active,
            )
            for ps, stage in rows
        ]
    )
