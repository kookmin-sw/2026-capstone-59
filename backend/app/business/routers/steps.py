from fastapi import Depends, Query
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.business.services import step_service
from app.business.dependencies import get_owned_project, get_owned_step
from app.core.api.route import EnvelopeRouter
from app.core.models.project import Project as ProjectModel
from app.core.models.step import Step as StepModel
from app.core.models.step import StepContent as StepContentModel
from app.core.schemas.step import (
    RequiredStepListResponse,
    SidePanelContentResponse,
    StepKeepResponse,
    StepKeepUpdateRequest,
    StepTreeResponse,
)
from uuid import UUID

router = EnvelopeRouter()


@router.get("/tree", status_code=http_status.HTTP_200_OK)
def get_step_tree(
    stage_id: UUID | None = Query(default=None),
    stage_sequence: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    project: ProjectModel = Depends(get_owned_project),
) -> StepTreeResponse:
    """project_id + (stage_id 또는 stage_sequence) 기준 Step 트리 + Footprint 경로 반환.

    stage_id 와 stage_sequence 중 정확히 하나를 제공해야 한다.
    프로젝트 목록의 썸네일 미리보기처럼 stage_id 를 모를 때는 stage_sequence 로 호출한다.
    """
    return step_service.get_step_tree(
        db, project.id, stage_id=stage_id, stage_sequence=stage_sequence
    )


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


@router.get(
    "/{step_id}/sidepanel-content",
    status_code=http_status.HTTP_200_OK,
)
def get_side_panel_content(
    db: Session = Depends(get_db),
    step: StepModel = Depends(get_owned_step),
) -> SidePanelContentResponse:
    """Side panel 생성 진행 상태 폴링.

    POST /steps/{step_id}/sidepanel-start 로 시작된 작업의 누적 raw text 와
    상태를 반환. 매 호출 200 OK + body 의 status 필드로 상태 전달.
    """
    content = db.get(StepContentModel, step.id)
    if content is None:
        return SidePanelContentResponse(status="idle", content="", is_complete=False)
    return SidePanelContentResponse(
        status=content.streaming_status,
        content=content.streaming_raw or "",
        is_complete=content.streaming_status in ("done", "error"),
    )
