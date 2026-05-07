from fastapi import Depends
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.business.services import stage_service
from app.business.dependencies import get_owned_project
from app.core.api.route import EnvelopeRouter
from app.core.models.project import Project as ProjectModel
from app.core.schemas.stage import StageListResponse

router = EnvelopeRouter()


@router.get("", status_code=http_status.HTTP_200_OK)
def list_stages(
    db: Session = Depends(get_db),
    project: ProjectModel = Depends(get_owned_project),
) -> StageListResponse:
    return stage_service.list_stages(db, project.id)
