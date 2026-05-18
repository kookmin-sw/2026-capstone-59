"""Design Export 비동기 폴링 시작 엔드포인트."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))
from uuid import UUID

from fastapi import Depends
from fastapi import status as http_status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ai.exceptions import (
    AIGenerationFailedError,
    BedrockAPIError,
    OutputViolatesHonestyGuardError,
)
from app.ai.services import design_export_renderer, design_export_service, orchestrator
from app.core.api.route import EnvelopeRouter
from app.core.database import get_db
from app.core.exceptions import ProjectNotFoundError
from app.core.repositories import project as project_repo
from app.core.schemas.project import (
    DesignExportStartRequest,
    DesignExportStartResponse,
)
from app.core.schemas.response import SuccessResponse

router = EnvelopeRouter()


@router.post(
    "/{project_id}/design-export-start",
    status_code=http_status.HTTP_202_ACCEPTED,
)
async def start_design_export(
    project_id: UUID,
    payload: DesignExportStartRequest,
    db: Session = Depends(get_db),
):
    """Design Export 생성을 시작한다 (비동기 폴링 방식).

    - 새로 시작: 202 Accepted + { job_id, status: 'pending' or 'done' or 'error' }
      (실제로는 같은 invocation 내에서 LLM 까지 끝까지 실행하므로
       응답 시점에 이미 done 또는 error 일 수 있음)
    - 이미 완료된 job_id 재호출: 200 OK + { job_id, status: 'done' or 'error' }
      (멱등 — 재실행 없이 기존 결과 신호)

    클라이언트는 응답을 기다리지 않고 즉시 폴링을 시작하는 fire-and-forget 패턴.
    """
    # 사전 검증 — 잘못된 입력은 즉시 4xx
    project = project_repo.get_active_project_by_id(db, project_id)
    if not project:
        raise ProjectNotFoundError()
    design_export_service.check_rate_limit(project_id)
    input_data = design_export_service.build_input(
        db, project_id, payload.selected_step_ids
    )

    # 이미 종료된 job_id 가 들어오면 멱등 응답 (재실행 X)
    from app.core.models.design_export_job import DesignExportJob

    existing = db.get(DesignExportJob, payload.job_id)
    if existing is not None and existing.status in ("done", "error"):
        body = SuccessResponse(
            data=DesignExportStartResponse(
                job_id=payload.job_id, status=existing.status
            )
        ).model_dump(mode="json")
        return JSONResponse(status_code=http_status.HTTP_200_OK, content=body)

    # job row 생성 (status=pending)
    design_export_service.create_job(db, payload.job_id, project_id)

    # LLM 실행 — 같은 invocation 에서 끝까지 진행. Lambda timeout 까지 계속 실행.
    try:
        ai_output = await orchestrator.call_design_export(input_data)
    except (BedrockAPIError, AIGenerationFailedError):
        design_export_service.mark_job_error(
            db, payload.job_id, "DESIGN_EXPORT_AI_FAILED"
        )
        return DesignExportStartResponse(job_id=payload.job_id, status="error")
    except OutputViolatesHonestyGuardError:
        design_export_service.mark_job_error(
            db, payload.job_id, "DESIGN_EXPORT_INVALID_OUTPUT"
        )
        return DesignExportStartResponse(job_id=payload.job_id, status="error")

    now_kst = datetime.now(KST)
    md = design_export_renderer.render(input_data, ai_output)
    filename = f"design_{now_kst:%Y-%m-%d_%H-%M}.md"
    design_export_service.mark_job_done(db, payload.job_id, md, filename)

    return DesignExportStartResponse(job_id=payload.job_id, status="done")
