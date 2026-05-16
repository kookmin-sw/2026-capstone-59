"""design-export SSE 엔드포인트."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from uuid import UUID

from fastapi import Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ai.exceptions import BedrockAPIError, AIGenerationFailedError, OutputViolatesHonestyGuardError
from app.ai.services import orchestrator
from app.ai.services import design_export_service, design_export_renderer
from app.core.api.route import EnvelopeRouter
from app.core.database import get_db
from app.core.exceptions import (
    DesignExportEmptySelectionError,
    DesignExportInactiveStepError,
    DesignExportInvalidStepIdError,
    DesignExportRateLimitError,
    ProjectNotFoundError,
)
from app.business.services import project_service

router = EnvelopeRouter()


class DesignExportRequest(BaseModel):
    selected_step_ids: list[UUID]


@router.post("/projects/{project_id}/design-export")
async def design_export_stream(
    project_id: UUID,
    payload: DesignExportRequest,
    db: Session = Depends(get_db),
):
    # SSE 시작 전 검증 — 여기서 raise하면 HTTP 상태코드 정상 반환
    project_service.get_project_or_raise(db, project_id)
    design_export_service.check_rate_limit(project_id)
    input_data, stage_seq_to_name = design_export_service.build_input(
        db, project_id, payload.selected_step_ids
    )

    async def event_generator():
        async def call_ai():
            return await orchestrator.call_design_export(input_data)

        ai_task = asyncio.create_task(call_ai())

        while not ai_task.done():
            yield "event: keepalive\ndata: {}\n\n"
            await asyncio.sleep(10)

        try:
            ai_output = ai_task.result()
        except (BedrockAPIError, AIGenerationFailedError):
            yield f"event: error\ndata: {json.dumps({'code': 'DESIGN_EXPORT_AI_FAILED'})}\n\n"
            return
        except OutputViolatesHonestyGuardError:
            yield f"event: error\ndata: {json.dumps({'code': 'DESIGN_EXPORT_INVALID_OUTPUT'})}\n\n"
            return

        md = design_export_renderer.render(input_data, ai_output, stage_seq_to_name)
        filename = f"design_{datetime.now(timezone.utc):%Y-%m-%d}.md"
        yield f"event: complete\ndata: {json.dumps({'markdown': md, 'filename': filename}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")