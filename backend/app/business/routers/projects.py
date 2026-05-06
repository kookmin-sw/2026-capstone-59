from uuid import UUID

from fastapi import Depends, Query
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.business.services import project_service
from app.core.api.route import EnvelopeRouter
from app.core.schemas.project import (
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
)

router = EnvelopeRouter()


@router.post("", status_code=http_status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreateRequest, db: Session = Depends(get_db)
) -> ProjectResponse:
    return project_service.create_project(db, payload)


@router.get("", status_code=http_status.HTTP_200_OK)
def list_projects(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    keyword: str | None = Query(None),
    db: Session = Depends(get_db),
) -> ProjectListResponse:
    return project_service.list_projects(db, page, size, sort_by, sort_order, keyword)


@router.patch("/{project_id}", status_code=http_status.HTTP_200_OK)
def update_project(
    project_id: UUID,
    payload: ProjectUpdateRequest,
    db: Session = Depends(get_db),
) -> ProjectResponse:
    return project_service.update_project(db, project_id, payload)


@router.delete("/{project_id}", status_code=http_status.HTTP_200_OK)
def delete_project(project_id: UUID, db: Session = Depends(get_db)) -> None:
    project_service.delete_project(db, project_id)
    return None
