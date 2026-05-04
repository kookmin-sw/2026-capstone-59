from uuid import UUID

from fastapi import Depends
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.business.services import stage_service
from app.core.api.route import EnvelopeRouter
from app.core.schemas.stage import StageListResponse

router = EnvelopeRouter()


@router.get("", status_code=http_status.HTTP_200_OK)
def list_stages(project_id: UUID, db: Session = Depends(get_db)) -> StageListResponse:
    return stage_service.list_stages(db, project_id)
