"""design-export 서비스 — DB 데이터 조립 + 검증 + rate limit."""

from __future__ import annotations

import json
import time
from uuid import UUID

from sqlalchemy.orm import Session

from ai.schemas.common import MentoringContent
from ai.schemas.design_export import (
    AcceptedStepForAI,
    DesignExportInput,
    ProjectContextForAI,
    RequiredStepForAI,
)
from app.core.exceptions import (
    DesignExportEmptySelectionError,
    DesignExportInactiveStepError,
    DesignExportInvalidStepIdError,
    DesignExportRateLimitError,
    ProjectNotFoundError,
)
from app.core.repositories import project as project_repo
from app.core.repositories import step as step_repo

_rate_limit_store: dict[str, float] = {}
_RATE_LIMIT_SECONDS = 10


def check_rate_limit(project_id: UUID) -> None:
    key = str(project_id)
    now = time.time()
    if now - _rate_limit_store.get(key, 0) < _RATE_LIMIT_SECONDS:
        raise DesignExportRateLimitError()
    _rate_limit_store[key] = now


def build_input(
    db: Session,
    project_id: UUID,
    selected_step_ids: list[UUID],
) -> DesignExportInput:

    if not selected_step_ids:
        raise DesignExportEmptySelectionError()

    project = project_repo.get_active_project_by_id(db, project_id)
    if not project:
        raise ProjectNotFoundError()

    steps = step_repo.get_steps_by_ids(db, selected_step_ids)
    if len(steps) != len(selected_step_ids):
        raise DesignExportInvalidStepIdError()

    for s in steps:
        if s.project_id != project_id or s.required_step_id is None:
            raise DesignExportInvalidStepIdError()

    active_stage_ids = {
        ps.stage_id
        for ps, _ in project_repo.get_project_stages_with_stage(db, project_id)
        if ps.is_active
    }
    for s in steps:
        if s.stage_id not in active_stage_ids:
            raise DesignExportInactiveStepError()

    steps_sorted = sorted(
        steps,
        key=lambda s: (s.stage.sequence, s.required_step.sequence),
    )

    project_context = ProjectContextForAI(
        name=project.name,
        description=project.description,
        duration_months=project.duration_month or 1,
        member_count=project.member_count or 1,
        constraints=project.constraints,
        initial_prompt=project.prompt or "",
    )

    selected_required_steps: list[RequiredStepForAI] = []
    for s in steps_sorted:
        rs = s.required_step

        accepted_steps = step_repo.get_accepted_steps_in_required(
            db, project_id, rs.id
        )
        accepted_steps_sorted = sorted(accepted_steps, key=lambda a: a.created_at)

        accepted_for_ai: list[AcceptedStepForAI] = []
        for a in accepted_steps_sorted:
            mentoring = None
            if a.content and a.content.mentoring:
                raw = json.loads(a.content.mentoring)
                description = raw["description"]
                try:
                    mentoring = MentoringContent(**raw)
                except Exception:
                    mentoring = None
            else:
                description = a.name

            accepted_for_ai.append(
                AcceptedStepForAI(
                    name=a.name,
                    description=description,
                    sidepanel_mentoring=mentoring,
                )
            )

        rs_id_str = f"{s.stage.sequence}-R{rs.sequence}"

        selected_required_steps.append(
            RequiredStepForAI(
                required_step_id=rs_id_str,
                required_step_name=rs.name,
                goal=rs.goal,
                fulfillment_criteria=rs.fulfillment_criteria,
                accepted_general_steps=accepted_for_ai,
            )
        )

    return DesignExportInput(
        project_context=project_context,
        selected_required_steps=selected_required_steps,
    )