"""accept 시나리오 입출력 스키마 — AI Dataset Spec v3 기반.

필수 Step 충족 판단: is_current_required_step_completed를 반환.
"""

from typing import Any, Optional

from pydantic import BaseModel

from ai.schemas.common import (
    ProjectInfo,
    RequiredStepInfo,
    RequiredStepStatus,
    StageInfo,
    StepInfo,
)


class AcceptInput(BaseModel):
    """accept 시나리오 입력."""

    project_info: ProjectInfo
    current_stage: StageInfo
    required_steps_status: list[RequiredStepStatus]
    current_required_step: Optional[RequiredStepInfo] = None
    accepted_steps_in_required: list[StepInfo]
    accepted_step: StepInfo
    rag_context: Optional[dict[str, Any]] = None


class AcceptOutput(BaseModel):
    """accept 시나리오 출력."""

    is_current_required_step_completed: bool
