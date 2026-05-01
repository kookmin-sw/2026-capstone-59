"""side_panel 시나리오 입출력 스키마 — AI Dataset Spec v3.1 기반.

일반 Step 사이드패널 콘텐츠 동적 생성:
mentoring 탭(description + recommended_methods + common_mistakes + one_line_tip)
+ dictionary 탭(term + definition 항목 목록).
"""

from typing import Any, Optional

from pydantic import BaseModel

from ai.schemas.common import (
    DecisionHistoryItem,
    DictionaryItem,
    MentoringContent,
    ProjectInfo,
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
    """side_panel 시나리오 출력 — 일반 Step용 (mentoring + dictionary 2탭 구조)."""

    mentoring: MentoringContent
    dictionary: list[DictionaryItem]
