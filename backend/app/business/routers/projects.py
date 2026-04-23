from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.business.dependency import get_db
from app.business.services import project_service
from app.core.schemas.project import ProjectCreateRequest, ProjectUpdateRequest

router = APIRouter()


def _ok(data):
    return {"status": "success", "data": data}

def _err(code: str, message: str):
    return {"status": "error", "error": {"code": code, "message": message}}

# Project 생성
@router.post("", status_code=201)
def create_project(payload: ProjectCreateRequest, db: Session = Depends(get_db)):
    result = project_service.create_project(db, payload)
    return _ok(result)

# Project 목록 조회
@router.get("")
def list_projects(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    keyword: str | None = Query(None),
    db: Session = Depends(get_db),
):
    result = project_service.list_projects(db, page, size, sort_by, sort_order, keyword)
    return _ok(result)

# Project 수정
@router.patch("/{project_id}")
def update_project(project_id: UUID, payload: ProjectUpdateRequest, db: Session = Depends(get_db)):
    result = project_service.update_project(db, project_id, payload)
    if result is None:
        return _err("PROJECT_NOT_FOUND", "프로젝트 없음")
    return _ok(result)

# Project 삭제
@router.delete("/{project_id}")
def delete_project(project_id: UUID, db: Session = Depends(get_db)):
    result = project_service.delete_project(db, project_id)
    if result is None:
        return _err("PROJECT_NOT_FOUND", "프로젝트 없음")
    return _ok(None)