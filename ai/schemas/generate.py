"""generate 시나리오 입출력 스키마 — AI Dataset Spec v3 기반.

Step 동적 생성: 일반 Step 3개를 생성하여 반환.
"""

from typing import Any, Optional

from pydantic import BaseModel, field_validator

from ai.schemas.common import (
    DecisionHistoryItem,
    GeneratedStep,
    ProjectInfo,
    RequiredStepInfo,
    StageInfo,
    StepInfo,
)


class GenerateInput(BaseModel):
    """generate 시나리오 입력."""

    project_info: ProjectInfo
    current_stage: StageInfo
    decision_history: list[DecisionHistoryItem]
    current_step: StepInfo
    current_required_step: Optional[RequiredStepInfo] = None
    rag_context: Optional[dict[str, Any]] = None


class GenerateOutput(BaseModel):
    """generate 시나리오 출력 — 정확히 3개의 GeneratedStep."""

    generated_steps: list[GeneratedStep]

    @field_validator("generated_steps")
    @classmethod
    def exactly_three(cls, v: list[GeneratedStep]) -> list[GeneratedStep]:
        if len(v) != 3:
            raise ValueError("generated_steps must contain exactly 3 items")
        return v
