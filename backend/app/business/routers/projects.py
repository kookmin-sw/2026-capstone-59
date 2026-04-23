from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.business.dependency import get_db
from app.business.services import project_service

router = APIRouter()


def _ok(data):
    return {"status": "success", "data": data}


@router.post("", status_code=201)
def create_project(payload: dict, db: Session = Depends(get_db)):
    return _ok(project_service.create_project(db, payload))


@router.get("")
def list_projects(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
):
    return _ok(project_service.list_projects(db, page, size, sort_by, sort_order))


@router.patch("/{project_id}")
def update_project(project_id: UUID, payload: dict, db: Session = Depends(get_db)):
    return _ok(project_service.update_project(db, project_id, payload))


@router.delete("/{project_id}")
def delete_project(project_id: UUID, db: Session = Depends(get_db)):
    project_service.delete_project(db, project_id)
    return _ok(None)