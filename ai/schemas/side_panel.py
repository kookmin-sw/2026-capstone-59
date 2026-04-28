"""side_panel 시나리오 입출력 스키마 — AI Dataset Spec v3.1 기반.

일반 Step 사이드패널 콘텐츠 동적 생성:
description + recommended_methods + common_mistakes + one_line_tip.
"""

from typing import Any, Optional

from pydantic import BaseModel

from ai.schemas.common import (
    CommonMistake,
    DecisionHistoryItem,
    ProjectInfo,
    RecommendedMethod,
    RequiredStepInfo,
    StageInfo,
    StepInfo,
)


class SidePanelInput(BaseModel):
    """side_panel 시나리오 입력."""

    project_info: ProjectInfo
    current_stage: StageInfo
    target_step: StepInfo
    decision_history: list[DecisionHistoryItem]
    current_required_step: Optional[RequiredStepInfo] = None
    rag_context: Optional[dict[str, Any]] = None


class SidePanelOutput(BaseModel):
    """side_panel 시나리오 출력 — 일반 Step용."""

    description: str
    recommended_methods: list[RecommendedMethod]
    common_mistakes: list[CommonMistake]
    one_line_tip: str
