"""공통 Pydantic 모델 — AI Dataset Spec v3 기반.

모든 AI 시나리오(generate, accept, side_panel)에서 공유하는 데이터 모델.
"""

from typing import Optional

from pydantic import BaseModel


class ProjectInfo(BaseModel):
    """프로젝트 기본 정보."""

    project_id: str
    name: Optional[str] = None
    duration_months: int
    member_count: int
    description: Optional[str] = None
    constraints: Optional[str] = None
    initial_prompt: str


class StageInfo(BaseModel):
    """현재 Stage 정보."""

    stage_id: str
    stage_number: int
    name: str


class StepInfo(BaseModel):
    """Step 기본 정보 (current_step, target_step, accepted_step 등)."""

    step_id: str
    name: str


class DecisionHistoryItem(BaseModel):
    """사용자 의사결정 히스토리 항목."""

    step_id: str
    name: str
    status: str
    stage_number: Optional[int] = None


class RequiredStepInfo(BaseModel):
    """현재 진행 중인 필수 Step 상세 정보."""

    step_id: str
    name: str
    is_completed: bool
    goal: str
    entry_criteria: str
    fulfillment_criteria: list[str]
    minimum_fulfillment_count: int


class RequiredStepStatus(BaseModel):
    """Stage 내 필수 Step 완료 상태."""

    name: str
    order: int
    is_completed: bool


class GeneratedStep(BaseModel):
    """AI가 생성한 일반 Step."""

    name: str
    description: str


class RecommendedMethod(BaseModel):
    """사이드패널 추천 방법."""

    title: str
    content: str


class CommonMistake(BaseModel):
    """사이드패널 흔한 실수."""

    mistake: str
    bad_example: str
    good_example: str


class RetrievedChunk(BaseModel):
    """KB에서 검색된 청크."""

    text: str
    relevance_score: float
