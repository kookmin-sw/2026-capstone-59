from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.business.dependency import get_db
from app.business.services import step_service

router = APIRouter()


def _ok(data):
    return {"status": "success", "data": data}


@router.get("/tree")
def get_step_tree(project_id: UUID, stage_id: UUID, db: Session = Depends(get_db)) -> dict:
    """project_id + stage_id 기준 Step 트리 + Footprint 경로 반환."""
    response = step_service.get_step_tree(db, project_id, stage_id)
    return _ok(response.model_dump())


@router.get("/{stage_id}/required")
def get_required_steps(stage_id: UUID, db: Session = Depends(get_db)) -> dict:
    """특정 Stage의 Required Step 목록 조회."""
    response = step_service.get_required_steps(db, stage_id)
    return _ok(response.model_dump())
