from uuid import UUID

from fastapi import Depends, Query
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.business.services import project_service
from app.business.dependencies import get_owned_project
from app.core.api.route import EnvelopeRouter
from app.core.auth.dependencies import get_current_user
from app.core.models.app_user import AppUser as AppUserModel
from app.core.models.project import Project as ProjectModel
from app.core.schemas.project import (
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
)

router = EnvelopeRouter()


@router.post("", status_code=http_status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreateRequest,
    db: Session = Depends(get_db),
    current_user: AppUserModel = Depends(get_current_user),
) -> ProjectResponse:
    return project_service.create_project(db, payload, current_user.id)


@router.get("", status_code=http_status.HTTP_200_OK)
def list_projects(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    keyword: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: AppUserModel = Depends(get_current_user),
) -> ProjectListResponse:
    return project_service.list_projects(db, page, size, sort_by, sort_order, keyword, current_user.id)


@router.patch("/{project_id}", status_code=http_status.HTTP_200_OK)
def update_project(
    payload: ProjectUpdateRequest,
    db: Session = Depends(get_db),
    project: ProjectModel = Depends(get_owned_project),
) -> ProjectResponse:
    return project_service.update_project(db, project.id, payload)


@router.delete("/{project_id}", status_code=http_status.HTTP_200_OK)
def delete_project(
    db: Session = Depends(get_db),
    project: ProjectModel = Depends(get_owned_project),
) -> None:
    project_service.delete_project(db, project.id)
    return None
