import json
from uuid import UUID

from fastapi import Depends
from fastapi import status as http_status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.ai.services import orchestrator, step_service
from app.core.api.route import EnvelopeRouter
from app.core.database import get_db
from app.core.schemas.step import (
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


@router.get("/steps/{step_id}/sidepanel-stream")
async def sidepanel_stream(step_id: UUID, db: Session = Depends(get_db)):
    """사이드패널 콘텐츠를 SSE 스트림으로 반환.

    Accept 직후 프론트가 노드별로 연결하며, 토큰이 도착할 때마다
    data 이벤트로 push된다. 스트리밍 완료 시 DB 저장 후 done 이벤트 전송.
    """
    step = step_service.get_step_for_stream(db, step_id)
    request = step_service.build_side_panel_request(db, step)

    async def event_generator():
        accumulated: list[str] = []
        try:
            async for chunk in orchestrator.call_side_panel_stream(request):
                accumulated.append(chunk)
                yield f"data: {json.dumps({'delta': chunk}, ensure_ascii=False)}\n\n"
            step_service.save_side_panel_content(db, step_id, "".join(accumulated))
            yield "event: done\ndata: {}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
