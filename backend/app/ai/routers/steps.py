from uuid import UUID

from fastapi import Depends
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.ai.services import step_service
from app.core.api.route import EnvelopeRouter
from app.core.database import get_db
from app.core.schemas.step import (
    NotionTemplateResponse,
    StepAcceptResponse,
    StepDetailResponse,
)

router = EnvelopeRouter()


@router.post("/steps/{step_id}/accept", status_code=http_status.HTTP_200_OK)
async def accept_step(
    step_id: UUID, db: Session = Depends(get_db)
) -> StepAcceptResponse:
    return await step_service.accept_step(db, step_id)


@router.get("/steps/{step_id}", status_code=http_status.HTTP_200_OK)
def get_step_detail(step_id: UUID, db: Session = Depends(get_db)) -> StepDetailResponse:
    return step_service.get_step_detail(db, step_id)


@router.post(
    "/steps/{step_id}/notion-template", status_code=http_status.HTTP_201_CREATED
)
def create_notion_template(step_id: UUID) -> NotionTemplateResponse:
    """Required Step의 Notion 템플릿 페이지 생성 — TODO: Notion API 연동."""
    return NotionTemplateResponse(
        notion_page_id="placeholder",
        notion_page_url="https://notion.so/placeholder",
    )
