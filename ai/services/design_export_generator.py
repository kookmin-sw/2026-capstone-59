"""design-export 시나리오 서비스 — Poco 사고 궤적 .md 본문 생성.

박제: Poco_Design_Export_Spec_v1.md v1.3 + design.md §3-4, §3-6, §3-7, §6.
RAG 없음 (Req 15.5). Bedrock 동기 호출 1회 (Req 10.2, 10.3).
출력 검증 위반 시 즉시 raise — 재시도 없음 (design.md §6-2).
"""

from __future__ import annotations

import json
import logging
import re
from typing import Optional

from ai.clients.llm import LLMClient
from ai.exceptions import OutputViolatesHonestyGuardError, OutputViolatesTemplateError
from ai.prompts.template import PromptTemplate
from ai.schemas.common import ProjectInfo
from ai.schemas.design_export import (
    AcceptedStepData,
    DesignExportInput,
    DesignExportOutput,
    ProjectStateForExport,
    RequiredStepExportData,
    StageExportData,
)

logger = logging.getLogger(__name__)

_SCENARIO = "design_export"
_NONE_LABEL = "(미입력)"

# ---------------------------------------------------------------------------
# 출력 검증 상수 (design.md §3-6-2)
# ---------------------------------------------------------------------------

_REQUIRED_MARKERS: list[str] = [
    # 자기소개 블록쿼터 핵심 문구 (Req 7.1, 7.3)
    "이 문서는 Poco가 생성한 What·Why 사고 궤적 문서입니다.",
    "이 문서를 받은 외부 AI에게",
    "답 디테일이 필요하면 사용자에게 직접 보충 질문하세요",
    # 6단계 흐름 어휘 (Req 7.2) — 블록쿼터 안에 한 줄로 들어있음
    "아이디어 구체화",
    "프로젝트 계획",
    "요구사항 정의",
    "설계",
    "개발",
    "테스트 및 검증",
    # 섹션 헤더 (Req 7.4, 7.5, 7.8)
    "## 프로젝트 컨텍스트",
    "## 사용자가 거쳐온 사고 궤적",
    "## 핵심 What·Why 정리",
    # Required_Step 블록 5개 하위 항목 라벨 (Req 7.6)
    "**목표**:",
    "**충족 기준**:",
    "**진행한 결정**",
    "**이 단계에서 인지한 What·Why 질문**:",
    "**사고 흐름 요약**",
    # 푸터 (Req 7.9)
    "도구: Poco",
]

_BANNED_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"답한\s*질문"),
    re.compile(r"검토한\s*질문"),
    re.compile(r"사고가\s*정리된\s*상태"),
    re.compile(r"결론을\s*내린\s*영역"),
    re.compile(r"답했다"),
    re.compile(r"답한\s+상태"),
]


def _validate_markdown(markdown: str) -> None:
    """출력 .md 가 고정 템플릿 마커 + 정직성 가드를 만족하는지 검증.

    위반 시 즉시 raise. 호출 측은 재시도하지 않는다 (design.md §6-2).
    """
    for marker in _REQUIRED_MARKERS:
        if marker not in markdown:
            raise OutputViolatesTemplateError(
                message=f"출력 .md 에 필수 마커 누락: {marker!r}",
                details={"missing_marker": marker},
            )
    for pattern in _BANNED_PATTERNS:
        match = pattern.search(markdown)
        if match:
            raise OutputViolatesHonestyGuardError(
                message=f"출력 .md 에 금지 표현 등장: {match.group(0)!r}",
                details={"banned_phrase": match.group(0)},
            )


# ---------------------------------------------------------------------------
# 입력 직렬화 헬퍼
# ---------------------------------------------------------------------------


def _coerce(value: object, default: str = _NONE_LABEL) -> str:
    if value is None:
        return default
    return str(value)


def _format_constraints(constraints: Optional[list[str]]) -> str:
    if not constraints:
        return _NONE_LABEL
    return ", ".join(constraints)


def _format_project_info(project_info: ProjectInfo) -> str:
    return "\n".join([
        f"- 이름: {_coerce(project_info.name)}",
        f"- 인원·기간: {project_info.member_count}명 / {project_info.duration_months}개월",
        f"- 설명: {_coerce(project_info.description)}",
        f"- 제약사항: {_format_constraints(project_info.constraints)}",
        f"- 초기 아이디어: {project_info.initial_prompt}",
    ])


def _format_accepted_step(step: AcceptedStepData) -> str:
    """일반 Step 1개를 마크다운 컨텍스트 라인들로 직렬화."""
    lines = [
        f"  - [{step.accepted_at.strftime('%Y-%m-%d %H:%M')}] {step.name} — {step.description}"
    ]
    mentoring = step.sidepanel_mentoring
    if mentoring is None:
        lines.append("    사이드패널 멘토링: 없음")
    else:
        lines.append("    사이드패널 멘토링:")
        if mentoring.recommended_methods:
            lines.append("      recommended_methods:")
            for rm in mentoring.recommended_methods:
                lines.append(f"        - {rm.title}: {rm.content}")
        if mentoring.common_mistakes:
            lines.append("      common_mistakes:")
            for cm in mentoring.common_mistakes:
                lines.append(f"        - {cm.mistake} (bad: {cm.bad_example} / good: {cm.good_example})")
        if mentoring.one_line_tip:
            lines.append(f"      one_line_tip: {mentoring.one_line_tip}")
    return "\n".join(lines)


def _format_required_step(rs: RequiredStepExportData) -> str:
    """RequiredStepExportData 1개를 마크다운 컨텍스트 블록으로 직렬화."""
    lines = [
        f"#### {rs.required_step_id} {rs.required_step_name}",
        f"- 목표: {rs.goal}",
        f"- 진입 기준: {rs.entry_criteria}",
        "- 충족 기준:",
    ]
    for criterion in rs.fulfillment_criteria:
        lines.append(f"  - {criterion}")

    if rs.accepted_general_steps:
        lines.append("- Accept된 일반 Step:")
        for step in rs.accepted_general_steps:
            lines.append(_format_accepted_step(step))
    else:
        lines.append("- Accept된 일반 Step: 없음 (이 영역에 막 진입한 상태)")

    return "\n".join(lines)


def _format_stage(stage: StageExportData) -> str:
    parts = [f"### Stage {stage.stage_sequence} — {stage.stage_name}"]
    for rs in stage.required_steps:
        parts.append(_format_required_step(rs))
    return "\n\n".join(parts)


def _format_project_state(project_state: ProjectStateForExport) -> str:
    return "\n\n".join(_format_stage(s) for s in project_state.stages)


# ---------------------------------------------------------------------------
# 서비스 클래스
# ---------------------------------------------------------------------------


class DesignExportGenerator:
    """design-export 시나리오 — Poco 사고 궤적 .md 본문 생성.

    RAG 없음 (Req 15.5). 시그니처: DesignExportGenerator(llm=LLMClient).
    """

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def generate_design_export(
        self, input_data: DesignExportInput
    ) -> DesignExportOutput:
        """사고 궤적 .md 본문을 생성한다.

        흐름:
            1) 입력을 마크다운 컨텍스트 블록으로 직렬화
            2) 프롬프트 렌더 (PromptTemplate.load_and_render)
            3) LLM 동기 호출 max_tokens=8192 — 한국어 markdown은 1글자당
               약 1.5~2 토큰이라 큰 입력(Stage 다수 선택)에서 4096으로는
               truncation 발생. CloudShell 실측에서 Stage ≥2 모두 잘림 확인.
            4) 출력 markdown 검증 → 위반 시 즉시 raise (재시도 금지 §6-2)
        """
        project_info_block = _format_project_info(input_data.project_info)
        project_state_block = _format_project_state(input_data.project_state)
        generated_at_str = input_data.generated_at.strftime("%Y-%m-%d %H:%M") + " (KST)"

        prompt = PromptTemplate.load_and_render(
            _SCENARIO,
            project_info_block=project_info_block,
            project_state_block=project_state_block,
            generated_at=generated_at_str,
        )

        logger.info(
            json.dumps(
                {
                    "event": "design_export_generator_invoke",
                    "project_id": str(input_data.project_info.project_id),
                    "num_stages": len(input_data.project_state.stages),
                    "num_required_steps": sum(
                        len(s.required_steps) for s in input_data.project_state.stages
                    ),
                    "prompt_len": len(prompt),
                },
                ensure_ascii=False,
                default=str,
            )
        )

        result: DesignExportOutput = await self.llm.invoke(
            prompt,
            DesignExportOutput,
            max_tokens=8192,
        )

        _validate_markdown(result.markdown)

        logger.info(
            json.dumps(
                {
                    "event": "design_export_generator_success",
                    "project_id": str(input_data.project_info.project_id),
                    "markdown_len": len(result.markdown),
                },
                ensure_ascii=False,
                default=str,
            )
        )

        return result
