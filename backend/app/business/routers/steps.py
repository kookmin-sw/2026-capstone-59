from uuid import UUID

from fastapi import Depends
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.business.dependency import get_db
from app.business.services import step_service
from app.core.api.route import EnvelopeRouter
from app.core.schemas.step import RequiredStepListResponse, StepTreeResponse

router = EnvelopeRouter()


@router.get("/tree", status_code=http_status.HTTP_200_OK)
def get_step_tree(
    project_id: UUID, stage_id: UUID, db: Session = Depends(get_db)
) -> StepTreeResponse:
    """project_id + stage_id 기준 Step 트리 + Footprint 경로 반환."""
    return step_service.get_step_tree(db, project_id, stage_id)


@router.get("/{stage_id}/required", status_code=http_status.HTTP_200_OK)
def get_required_steps(
    stage_id: UUID, db: Session = Depends(get_db)
) -> RequiredStepListResponse:
    """특정 Stage의 Required Step 목록 조회."""
    return step_service.get_required_steps(db, stage_id)
