"""design_export 시나리오 입출력 스키마 (v1.4 Z+).

박제: Poco_Design_Export_Spec_v1.md v1.4 §7 + design.md §3-2.

v1.4 Z+ 결정 (옵션 B-단일 + 변환 풍부도):
- AI 출력은 .md 본문 통째가 아니라 RS별 What·Why 질문 list + 영역 전체 핵심
  정리 list. .md 골격(자기소개 블록쿼터·헤더·정적 텍스트·푸터)은 백엔드
  Design_Export_Renderer 책임.
- AI 입력에 RS DB 정의(goal·fulfillment_criteria)와 ProjectContext 풍부 필드
  (description·constraints) 포함 — 같은 데이터가 백엔드 .md 골격에도 박히지만
  AI도 받아서 변환 풍부도를 향상시킨다 (입력 토큰은 출력에 비해 속도·비용
  영향이 작아 부담 미미).
- entry_criteria 는 사용자 궤적과 무관하므로 입력에서 제외.
- accepted_at 은 백엔드 정렬 책임이라 AI 입력에서는 생략.
- dictionary 필드는 외부 AI에 무가치 노이즈라 절대 포함하지 않는다.
- "사고 흐름 요약" 항목 폐기 (CloudShell 사람 검수에서 멘토링 출력 톤이라는
  지적 + 출력 토큰 압박 해소).

v1.0~v1.3 폐기 모델: AcceptedStepData, RequiredStepExportData, StageExportData,
ProjectStateForExport, (옵션 A 형태의) DesignExportInput,
(markdown: str 형태의) DesignExportOutput.
"""

from typing import Optional

from pydantic import BaseModel, Field

from ai.schemas.common import MentoringContent

# SidePanelMentoring 은 MentoringContent 를 그대로 재사용한다.
# dictionary 필드는 본 시나리오에서 입력에 포함되지 않으므로 (Req 6.7),
# 별도 Optional 필드로 추가하지 않는다.
SidePanelMentoring = MentoringContent


# -- 입력 ---------------------------------------------------------------------


class AcceptedStepForAI(BaseModel):
    """필수 Step 영역 안 Accept된 일반 Step의 데이터 (Req 6.5).

    accepted_at 은 백엔드 정렬 책임이라 AI 입력에서는 생략한다.
    """

    name: str
    description: str
    sidepanel_mentoring: Optional[SidePanelMentoring] = None


class RequiredStepForAI(BaseModel):
    """선택된 Required_Step 1개의 변환 컨텍스트 (Req 6.4, Z+).

    goal·fulfillment_criteria 는 같은 데이터가 백엔드 .md 골격에도 박히지만,
    AI 도 받아서 변환 톤을 풍부하게 잡는다 (Z+ 결정).
    entry_criteria 는 사용자 궤적과 무관하므로 입력에서 제외 (Req 6.9).
    accepted_general_steps 가 0개인 폴백 케이스에서는 RS 메타(name·goal·
    fulfillment_criteria) 만으로 *"막 진입한 상태에서 떠오를 만한 질문"* 을
    생성한다 (Req 4.3).
    """

    required_step_id: str  # "1-R1" 형식, 출력 매칭 키
    required_step_name: str  # "문제·기회 정의" (DB 정의)
    goal: str  # DB 정의
    fulfillment_criteria: list[str]  # DB 정의
    accepted_general_steps: list[AcceptedStepForAI]  # 비어있을 수 있음


class ProjectContextForAI(BaseModel):
    """변환 톤 일관성·풍부도용 프로젝트 맥락 (Req 6.2, Z+).

    Z+ 옵션: description·constraints 포함하여 변환 풍부도 향상.
    백엔드가 .md 골격의 "프로젝트 컨텍스트" 섹션을 별도로 렌더하므로 AI는
    project_id 같은 식별 필드는 받지 않는다.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    duration_months: int = Field(..., ge=1, le=12)
    member_count: int = Field(..., ge=1, le=20)
    constraints: Optional[list[str]] = None
    initial_prompt: str


class DesignExportInput(BaseModel):
    """generate_design_export 입력 (v1.4 Z+).

    .md 골격 데이터(자기소개 블록쿼터·정적 텍스트·푸터·generated_at)는
    포함하지 않는다 — 백엔드 Design_Export_Renderer 책임.
    """

    project_context: ProjectContextForAI
    selected_required_steps: list[RequiredStepForAI] = Field(..., min_length=1)


# -- 출력 ---------------------------------------------------------------------


class RSQuestions(BaseModel):
    """RS 1개분 변환 결과 — What·Why 질문 list (v1.4 Z+).

    Z+ 풍부도: questions 상한 5 → 6 으로 살짝 상향.
    """

    required_step_id: str  # 입력 매칭 키 (Req 17.3)
    questions: list[str] = Field(
        ...,
        min_length=3,
        max_length=6,
        description=(
            "이 단계에서 사용자가 인지한 What·Why 질문 3~6개. "
            "사용자 결정으로 오인하지 않는 인지형 진술 또는 의문문."
        ),
    )


class DesignExportOutput(BaseModel):
    """generate_design_export 출력 (v1.4 Z+).

    AI는 .md 본문 통째를 만들지 않는다. 백엔드 Design_Export_Renderer 가
    골격을 렌더하고 본 출력의 questions·core_summary 를 끼워넣는다.

    Z+ 풍부도: core_summary 상한 5 → 6.
    """

    questions_per_rs: list[RSQuestions] = Field(
        ...,
        description=(
            "selected_required_steps 와 동일 길이·순서. 각 항목은 그 RS 의 "
            "What·Why 질문 list."
        ),
    )
    core_summary: list[str] = Field(
        ...,
        min_length=3,
        max_length=6,
        description=(
            "선택된 영역 전체에 걸친 핵심 What·Why 글머리 3~6개. "
            "외부 AI 가 이 항목만 보아도 사용자 사고의 중심을 파악할 수 "
            "있어야 함."
        ),
    )
