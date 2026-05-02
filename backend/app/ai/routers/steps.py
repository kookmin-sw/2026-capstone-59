from uuid import UUID

from fastapi import Depends
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.ai.services import step_service
from app.core.api.route import EnvelopeRouter
from app.core.database import get_db

router = EnvelopeRouter()


# AI 서비스 함수들은 현재 plain dict를 반환한다.
# 추후 응답 스키마(Pydantic)가 정의되면 dict → 해당 스키마로 어노테이션을 좁힐 것.


@router.post("/steps/{step_id}/generate", status_code=http_status.HTTP_201_CREATED)
def generate_steps(step_id: UUID, db: Session = Depends(get_db)) -> dict:
    """현재 Step 기반으로 다음 후보 Step 3개를 AI로 생성."""
    return step_service.generate_steps(db, step_id)


@router.post("/steps/{step_id}/accept", status_code=http_status.HTTP_200_OK)
def accept_step(step_id: UUID, db: Session = Depends(get_db)) -> dict:
    return step_service.accept_step(db, step_id)


@router.get("/steps/{step_id}", status_code=http_status.HTTP_200_OK)
def get_step_detail(step_id: UUID, db: Session = Depends(get_db)) -> dict:
    return step_service.get_step_detail(db, step_id)


@router.post(
    "/steps/{step_id}/notion-template", status_code=http_status.HTTP_201_CREATED
)
def create_notion_template(step_id: UUID) -> dict:
    """Required Step의 Notion 템플릿 페이지 생성 — TODO: Notion API 연동."""
    return {
        "notion_page_id": "placeholder",
        "notion_page_url": "https://notion.so/placeholder",
    }
