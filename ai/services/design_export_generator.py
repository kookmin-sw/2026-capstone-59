"""design-export 시나리오 서비스 (v1.4 Z+, 옵션 B-단일).

AI는 RS별 What·Why 질문 list + 영역 전체 핵심 정리만 생성.
.md 골격은 백엔드 Design_Export_Renderer 책임 (v1.4).
RAG 없음 (Req 15.5). Bedrock 동기 호출 1회 (Req 10.2, 10.3).
금지 표현 위반 시 즉시 raise — 재시도 없음 (design.md §3-7-2).
"""

from __future__ import annotations

import json
import logging
import re
from typing import Optional

from ai.clients.llm import LLMClient
from ai.exceptions import OutputViolatesHonestyGuardError
from ai.prompts.template import PromptTemplate
from ai.schemas.design_export import (
    AcceptedStepForAI,
    DesignExportInput,
    DesignExportOutput,
    ProjectContextForAI,
    RequiredStepForAI,
)

logger = logging.getLogger(__name__)

_SCENARIO = "design_export"
_NONE_LABEL = "(미입력)"

_BANNED_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"답한\s*질문"),
    re.compile(r"검토한\s*질문"),
    re.compile(r"사고가\s*정리된\s*상태"),
    re.compile(r"결론을\s*내린\s*영역"),
    re.compile(r"답했다"),
    re.compile(r"답한\s+상태"),
]


def _scan_banned(texts: list[str]) -> Optional[tuple[str, str]]:
    """금지 표현이 포함된 첫 번째 문자열과 매칭 어구를 반환. 없으면 None."""
    for text in texts:
        for pattern in _BANNED_PATTERNS:
            match = pattern.search(text)
            if match:
                return text, match.group(0)
    return None


def _coerce(value: object, default: str = _NONE_LABEL) -> str:
    return default if value is None else str(value)


def _format_project_context(ctx: ProjectContextForAI) -> str:
    constraints_str = (
        " / ".join(ctx.constraints) if ctx.constraints else _NONE_LABEL
    )
    return "\n".join([
        f"- 이름: {_coerce(ctx.name)}",
        f"- 설명: {_coerce(ctx.description)}",
        f"- 인원·기간: {ctx.member_count}명 / {ctx.duration_months}개월",
        f"- 제약사항: {constraints_str}",
        f"- 초기 아이디어: {ctx.initial_prompt}",
    ])


def _format_accepted_step(step: AcceptedStepForAI) -> str:
    lines = [f"  - {step.name}: {step.description}"]
    mentoring = step.sidepanel_mentoring
    if mentoring is not None:
        if mentoring.recommended_methods:
            lines.append("    recommended_methods:")
            for rm in mentoring.recommended_methods:
                lines.append(f"      - {rm.title}: {rm.content}")
        if mentoring.common_mistakes:
            lines.append("    common_mistakes:")
            for cm in mentoring.common_mistakes:
                lines.append(f"      - {cm.mistake}")
        if mentoring.one_line_tip:
            lines.append(f"    one_line_tip: {mentoring.one_line_tip}")
    return "\n".join(lines)


def _format_required_step(rs: RequiredStepForAI) -> str:
    lines = [
        f"#### {rs.required_step_id} {rs.required_step_name}",
        f"- 목표: {rs.goal}",
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


def _format_selected_required_steps(rs_list: list[RequiredStepForAI]) -> str:
    return "\n\n".join(_format_required_step(rs) for rs in rs_list)


class DesignExportGenerator:
    """design-export 시나리오 — RS별 What·Why 질문 + 핵심 정리 생성 (v1.4 Z+).

    RAG 없음 (Req 15.5). 시그니처: DesignExportGenerator(llm=LLMClient).
    """

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def generate_design_export(
        self, input_data: DesignExportInput
    ) -> DesignExportOutput:
        """RS별 What·Why 질문 list + 핵심 정리를 생성한다.

        흐름:
            1) 입력을 텍스트 블록으로 직렬화
            2) 프롬프트 렌더 (PromptTemplate.load_and_render)
            3) LLM 동기 호출 max_tokens=6144
            4) 금지 표현 스캔 → 위반 시 즉시 raise (재시도 금지 §3-7-2)
            5) questions_per_rs ID 매칭 검증 → 불일치 시 즉시 raise
        """
        project_context_block = _format_project_context(input_data.project_context)
        selected_required_steps_block = _format_selected_required_steps(
            input_data.selected_required_steps
        )
        prompt = PromptTemplate.load_and_render(
            _SCENARIO,
            project_context_block=project_context_block,
            selected_required_steps_block=selected_required_steps_block,
        )

        logger.info(
            json.dumps(
                {
                    "event": "design_export_generator_invoke",
                    "num_selected_rs": len(input_data.selected_required_steps),
                    "prompt_len": len(prompt),
                },
                ensure_ascii=False,
            )
        )

        result: DesignExportOutput = await self.llm.invoke(
            prompt,
            DesignExportOutput,
            max_tokens=6144,
        )

        all_texts = [q for rs_q in result.questions_per_rs for q in rs_q.questions]
        all_texts.extend(result.core_summary)
        violation = _scan_banned(all_texts)
        if violation:
            violating_text, banned_phrase = violation
            raise OutputViolatesHonestyGuardError(
                details={"banned_phrase": banned_phrase, "violating_text": violating_text},
            )

        expected_ids = [rs.required_step_id for rs in input_data.selected_required_steps]
        actual_ids = [rs_q.required_step_id for rs_q in result.questions_per_rs]
        if actual_ids != expected_ids:
            raise OutputViolatesHonestyGuardError(
                message="questions_per_rs required_step_id 매칭 불일치",
                details={"expected": expected_ids, "actual": actual_ids},
            )

        logger.info(
            json.dumps(
                {
                    "event": "design_export_generator_success",
                    "num_rs_questions": len(result.questions_per_rs),
                    "num_core_summary": len(result.core_summary),
                },
                ensure_ascii=False,
            )
        )

        return result
