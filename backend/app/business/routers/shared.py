"""공유 링크 읽기 전용 API — 인증 불필요."""

from uuid import UUID

from fastapi import Depends, Query
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.business.services import project_service, stage_service, step_service
from app.core.api.route import EnvelopeRouter
from app.core.database import get_db
from app.core.models.project import Project as ProjectModel
from app.core.schemas.project import ProjectResponse
from app.core.schemas.stage import StageListResponse
from app.core.schemas.step import StepDetailResponse, StepTreeResponse

router = EnvelopeRouter()


def _get_shared_project(
    share_token: str, db: Session = Depends(get_db)
) -> ProjectModel:
    """share_token으로 프로젝트를 조회하는 의존성."""
    return project_service.get_project_by_share_token(db, share_token)


@router.get("/{share_token}", status_code=http_status.HTTP_200_OK)
def get_shared_project(
    db: Session = Depends(get_db),
    project: ProjectModel = Depends(_get_shared_project),
) -> ProjectResponse:
    """공유 프로젝트 정보 조회."""
    return project_service.to_project_response(db, project)


@router.get("/{share_token}/stages", status_code=http_status.HTTP_200_OK)
def get_shared_stages(
    db: Session = Depends(get_db),
    project: ProjectModel = Depends(_get_shared_project),
) -> StageListResponse:
    """공유 프로젝트 Stage 목록 조회."""
    return stage_service.list_stages(db, project.id)


@router.get("/{share_token}/steps/tree", status_code=http_status.HTTP_200_OK)
def get_shared_step_tree(
    stage_id: UUID = Query(...),
    db: Session = Depends(get_db),
    project: ProjectModel = Depends(_get_shared_project),
) -> StepTreeResponse:
    """공유 프로젝트 Step 트리 조회."""
    return step_service.get_step_tree(db, project.id, stage_id)


@router.get("/{share_token}/steps/{step_id}", status_code=http_status.HTTP_200_OK)
def get_shared_step_content(
    step_id: UUID,
    db: Session = Depends(get_db),
    project: ProjectModel = Depends(_get_shared_project),
) -> StepDetailResponse:
    """공유 프로젝트의 Step Content 조회 (DB read-only)."""
    return step_service.get_step_content(db, project.id, step_id)
