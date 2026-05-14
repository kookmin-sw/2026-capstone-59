from fastapi import Depends
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.business.services import step_service
from app.business.dependencies import get_owned_project, get_owned_step
from app.core.api.route import EnvelopeRouter
from app.core.models.project import Project as ProjectModel
from app.core.models.step import Step as StepModel
from app.core.schemas.step import (
    RequiredStepListResponse,
    StepKeepResponse,
    StepKeepUpdateRequest,
    StepTreeResponse,
)
from uuid import UUID

router = EnvelopeRouter()


@router.get("/tree", status_code=http_status.HTTP_200_OK)
def get_step_tree(
    stage_id: UUID,
    db: Session = Depends(get_db),
    project: ProjectModel = Depends(get_owned_project),
) -> StepTreeResponse:
    """project_id + stage_id 기준 Step 트리 + Footprint 경로 반환."""
    return step_service.get_step_tree(db, project.id, stage_id)


@router.get("/{stage_id}/required", status_code=http_status.HTTP_200_OK)
def get_required_steps(
    stage_id: UUID, db: Session = Depends(get_db)
) -> RequiredStepListResponse:
    """특정 Stage의 Required Step 목록 조회."""
    return step_service.get_required_steps(db, stage_id)


@router.post("/{step_id}/rollback", status_code=http_status.HTTP_200_OK)
def rollback_step(
    db: Session = Depends(get_db),
    step: StepModel = Depends(get_owned_step),
) -> None:
    return step_service.rollback_step(db, step.id)


@router.post("/{step_id}/keep", status_code=http_status.HTTP_200_OK)
def update_step_keep(
    payload: StepKeepUpdateRequest,
    db: Session = Depends(get_db),
    step: StepModel = Depends(get_owned_step),
) -> StepKeepResponse:
    """Step.is_keep 값을 변경한다."""
    return step_service.update_step_keep(db, step.id, payload.is_keep)
