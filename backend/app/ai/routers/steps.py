from uuid import UUID

from fastapi import Depends
from fastapi import status as http_status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.ai.services import step_service
from app.core.api.route import EnvelopeRouter
from app.core.database import get_db
from app.core.models.step import StepContent as StepContentModel
from app.core.schemas.response import SuccessResponse
from app.core.schemas.step import (
    SidePanelStartResponse,
    StepAcceptResponse,
    StepDetailResponse,
)

router = EnvelopeRouter()


@router.post("/{step_id}/accept", status_code=http_status.HTTP_200_OK)
async def accept_step(
    step_id: UUID, db: Session = Depends(get_db)
) -> StepAcceptResponse:
    return await step_service.accept_step(db, step_id)


@router.get("/{step_id}", status_code=http_status.HTTP_200_OK)
def get_step_detail(step_id: UUID, db: Session = Depends(get_db)) -> StepDetailResponse:
    return step_service.get_step_detail(db, step_id)


@router.post(
    "/{step_id}/sidepanel-start",
    status_code=http_status.HTTP_202_ACCEPTED,
)
async def start_side_panel(step_id: UUID, db: Session = Depends(get_db)):
    """Side panel 생성을 시작한다 (비동기 폴링 방식).

    - 새로 시작 / 이미 진행 중 → 202 Accepted
    - 이미 완료 (status=done) → 200 OK (재생성 안 함, 멱등)

    클라이언트는 응답을 기다리지 않고 즉시 `/sidepanel-content` 를 폴링.
    Lambda 는 클라이언트 끊김과 무관하게 자체 timeout 까지 실행되며
    chunk 도착마다 DB 에 누적 저장한다.
    """
    # 존재 확인 + 사전조건 검사
    step = step_service.get_step_for_stream(db, step_id)
    content = db.get(StepContentModel, step_id)

    # 이미 완료 — 재생성 없이 200
    if content is not None and content.streaming_status == "done":
        body = SuccessResponse(
            data=SidePanelStartResponse(step_id=step.id, status="done")
        ).model_dump(mode="json")
        return JSONResponse(status_code=http_status.HTTP_200_OK, content=body)

    # 이미 진행 중 — 새 작업 시작하지 않고 202 만 반환
    if content is not None and content.streaming_status in ("pending", "streaming"):
        return SidePanelStartResponse(
            step_id=step.id, status=content.streaming_status
        )

    # 새로 시작 — 같은 invocation 에서 LLM 실행. Lambda timeout 까지 계속 진행.
    await step_service.run_side_panel_generation(db, step_id)
    return SidePanelStartResponse(step_id=step.id, status="done")
