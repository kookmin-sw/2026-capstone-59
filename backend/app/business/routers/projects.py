from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.business.dependency import get_db
from app.business.services import project_service
from app.core.schemas.project import ProjectCreateRequest, ProjectUpdateRequest

router = APIRouter()


def _ok(data):
    return {"status": "success", "data": data}


@router.post("", status_code=http_status.HTTP_201_CREATED)
def create_project(payload: ProjectCreateRequest, db: Session = Depends(get_db)):
    return _ok(project_service.create_project(db, payload).model_dump())


@router.get("", status_code=http_status.HTTP_200_OK)
def list_projects(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    keyword: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return _ok(
        project_service.list_projects(
            db, page, size, sort_by, sort_order, keyword
        ).model_dump()
    )


@router.patch("/{project_id}", status_code=http_status.HTTP_200_OK)
def update_project(
    project_id: UUID, payload: ProjectUpdateRequest, db: Session = Depends(get_db)
):
    return _ok(project_service.update_project(db, project_id, payload).model_dump())


@router.delete("/{project_id}", status_code=http_status.HTTP_200_OK)
def delete_project(project_id: UUID, db: Session = Depends(get_db)):
    project_service.delete_project(db, project_id)
    return _ok(None)
