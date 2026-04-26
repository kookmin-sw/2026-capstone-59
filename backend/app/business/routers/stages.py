from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.business.dependency import get_db
from app.business.services import stage_service

router = APIRouter()


def _ok(data):
    return {"status": "success", "data": data}


@router.get("", status_code=http_status.HTTP_200_OK)
def list_stages(project_id: UUID, db: Session = Depends(get_db)):
    return _ok(stage_service.list_stages(db, project_id).model_dump())
