from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import status as http_status

from app.ai.services import step_service
from app.core.database import get_db
from app.core.schemas.step import GeneratedStep, StepGenerateResponse

router = APIRouter()


def _ok(data):
    return {"status": "success", "data": data}


@router.post("/steps/{step_id}/generate", status_code=http_status.HTTP_201_CREATED)
def generate_steps(step_id: UUID, db: Session = Depends(get_db)) -> dict:
    """현재 Step 기반으로 다음 후보 Step 3개를 AI로 생성."""
    steps = step_service.generate_steps(db, step_id)
    response = StepGenerateResponse(
        generated_steps=[
            GeneratedStep(
                step_id=s.id,
                name=s.name,
                status=s.status,
                is_required=s.required_step_id is not None,
                parent_step_id=s.parent_step_id,
            )
            for s in steps
        ]
    )
    return _ok(response.model_dump())


@router.post("/steps/{step_id}/accept")
def accept_step(step_id: UUID) -> dict:
    """Step Accept (상태 판정) — TODO: AI 충족 판단 구현."""
    return _ok({
        "step_id": str(step_id),
        "status": "ACCEPTED",
        "is_current_required_step_completed": False,
    })


@router.post("/steps/{step_id}/notion-template", status_code=http_status.HTTP_201_CREATED)
def create_notion_template(step_id: UUID) -> dict:
    """Required Step의 Notion 템플릿 페이지 생성 — TODO: Notion API 연동."""
    return _ok({
        "notion_page_id": "placeholder",
        "notion_page_url": "https://notion.so/placeholder",
    })
