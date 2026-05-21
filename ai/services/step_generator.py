"""Step 동적 생성 서비스 (generate 시나리오).

LLMClient + RAGClient를 조합하여, 사용자 맥락 + DOJ KB 검색 결과를
프롬프트로 조립하고 Claude를 호출해 일반 Step 3개를 생성한다.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from ai.clients.llm import LLMClient
from ai.clients.rag import RAGClient
from ai.prompts.activity_guides import get_blocklist, resolve_activity_guide
from ai.prompts.template import PromptTemplate
from ai.schemas.common import RequiredStepInfo, RetrievedChunk
from ai.schemas.generate import GenerateInput, GenerateOutput

logger = logging.getLogger(__name__)

_SCENARIO = "generate"
_NONE_LABEL = "없음"


def _normalize_step_name(name: str) -> str:
    """이름 정규화: 공백 모두 제거 + 소문자화. literal 중복 비교용."""
    return "".join(name.lower().split())


def _collect_forbidden_names(input_data: "GenerateInput") -> "set[str]":
    """금지 이름 집합: 직전 부모 + decision_history 모든 항목."""
    forbidden = {_normalize_step_name(input_data.current_step.name)}
    for item in input_data.decision_history:
        forbidden.add(_normalize_step_name(item.name))
    return forbidden


_INTERCHANGEABLE_SUFFIXES = frozenset({
    "검토", "정리", "분석", "작성", "정의", "도출", "수립",
    "명세", "명세화", "결정", "선정", "선택", "정립", "진행",
    "평가", "점검", "식별", "매핑", "비교", "조사", "파악",
    "확인", "구성", "설정", "수행", "구축",
    "계획", "방안", "전략", "방향",
})


def _extract_content_tokens(name: str) -> "set[str]":
    """이름에서 핵심 명사 토큰만 추출 (동사형 접미사 stopword 제외)."""
    tokens = name.lower().split()
    return {t for t in tokens if t not in _INTERCHANGEABLE_SUFFIXES}


def _is_semantic_duplicate(new_name: str, forbidden_name: str) -> bool:
    """핵심 명사 2개 이상 겹치면 의미 중복으로 판정."""
    a = _extract_content_tokens(new_name)
    b = _extract_content_tokens(forbidden_name)
    return len(a & b) >= 2


def _has_duplicate(
    step_name: str,
    forbidden_normalized: "set[str]",
    forbidden_raw_names: "list[str]",
    current_required_step: Optional[RequiredStepInfo],
) -> bool:
    """literal·semantic·blocklist 3단계 중복 검사."""
    normalized = _normalize_step_name(step_name)
    if normalized in forbidden_normalized:
        return True
    if any(_is_semantic_duplicate(step_name, f) for f in forbidden_raw_names):
        return True
    if current_required_step is not None:
        if normalized in get_blocklist(current_required_step.name):
            return True
    return False


def _format_rag_context(chunks: list[RetrievedChunk]) -> str:
    """RAG 검색 결과를 프롬프트용 텍스트로 포맷팅."""
    if not chunks:
        return _NONE_LABEL
    return "\n".join(chunk.text for chunk in chunks)


def _coerce(value: Any, default: str = "") -> str:
    """None을 빈 문자열로 변환 (Optional 필드용)."""
    if value is None:
        return default
    return str(value)


def _format_constraints(constraints: Optional[list[str]]) -> str:
    """list[str] 제약사항을 프롬프트용 들여쓰기 리스트로 포맷팅.

    선두에 줄바꿈을 두어 템플릿의 라벨(`- 제약사항: {constraints}`) 뒤에
    첫 항목이 한 줄로 붙는 것을 방지한다. 모든 항목이 동일하게
    `  - {item}` 형태로 들여쓰기되어 시각적·LLM 인식 일관성을 갖는다.
    """
    if not constraints:
        return _NONE_LABEL
    return "\n" + "\n".join(f"  - {c}" for c in constraints)


class StepGenerator:
    """generate 시나리오 — 일반 Step 3개 동적 생성."""

    def __init__(
        self,
        llm: LLMClient,
        rag: RAGClient,
        doj_data_source_id: Optional[str] = None,
    ) -> None:
        self.llm = llm
        self.rag = rag
        self.doj_data_source_id = doj_data_source_id

    async def generate_steps(self, input_data: GenerateInput) -> GenerateOutput:
        """입력을 받아 Claude로 일반 Step 3개를 생성한다.

        흐름:
            1) RAG: 현재 Stage의 DOJ 활동 범위 검색
            2) 프롬프트 조립 (PromptTemplate.load_and_render)
            3) LLM 호출 → GenerateOutput 검증
        """
        stage = input_data.current_stage
        project = input_data.project_info

        rag_query = f"Stage {stage.stage_sequence} {stage.name} activities"
        chunks = await self.rag.search_doj(
            rag_query,
            num_results=3,
            data_source_id=self.doj_data_source_id,
        )

        decision_history_json = json.dumps(
            [item.model_dump(mode='json') for item in input_data.decision_history],
            ensure_ascii=False,
        )

        if input_data.current_required_step is not None:
            required_step_info = json.dumps(
                input_data.current_required_step.model_dump(mode='json'),
                ensure_ascii=False,
            )
        else:
            required_step_info = _NONE_LABEL

        rag_context_text = _format_rag_context(chunks)

        prompt = PromptTemplate.load_and_render(
            _SCENARIO,
            project_name=_coerce(project.name, _NONE_LABEL),
            duration_months=str(project.duration_months),
            member_count=str(project.member_count),
            description=_coerce(project.description, _NONE_LABEL),
            constraints=_format_constraints(project.constraints),
            initial_prompt=project.initial_prompt,
            stage_sequence=str(stage.stage_sequence),
            stage_name=stage.name,
            decision_history=decision_history_json,
            current_step_name=input_data.current_step.name,
            current_required_step_info=required_step_info,
            rag_context=rag_context_text,
            r_specific_activity_guide=resolve_activity_guide(input_data.current_required_step),
        )

        logger.info(
            json.dumps(
                {
                    "event": "step_generator_invoke",
                    "project_id": str(project.project_id),
                    "stage_sequence": stage.stage_sequence,
                    "rag_chunks": len(chunks),
                    "has_required_step": input_data.current_required_step is not None,
                    "prompt_len": len(prompt),
                },
                ensure_ascii=False,
                default=str,
            )
        )

        output = await self.llm.invoke(prompt, GenerateOutput, max_tokens=1024)

        forbidden_normalized = _collect_forbidden_names(input_data)
        forbidden_raw_names: list[str] = [input_data.current_step.name] + [
            item.name for item in input_data.decision_history
        ]
        req_step = input_data.current_required_step

        def _check(step_name: str) -> bool:
            return _has_duplicate(step_name, forbidden_normalized, forbidden_raw_names, req_step)

        duplicates = [s.name for s in output.generated_steps if _check(s.name)]
        if duplicates:
            blocklist = get_blocklist(req_step.name) if req_step is not None else frozenset()
            blocklist_matches = [d for d in duplicates if _normalize_step_name(d) in blocklist]
            if blocklist_matches:
                logger.warning(
                    json.dumps(
                        {
                            "event": "step_generator_blocklist_match",
                            "matches": blocklist_matches,
                            "required_step": req_step.name if req_step is not None else None,
                        },
                        ensure_ascii=False,
                    )
                )
            logger.warning(
                json.dumps(
                    {
                        "event": "step_generator_literal_duplicate_detected",
                        "duplicates": duplicates,
                        "retrying": True,
                    },
                    ensure_ascii=False,
                )
            )
            retry_prompt = prompt + (
                "\n\n# ★★ 재시도 — 절대 금지 ★★\n"
                "이전 시도에서 다음 이름이 동어 반복으로 폐기되었다.\n"
                "이번 응답에서는 아래 이름과 literal 동일하거나 의미 동일한 Step을\n"
                "**절대** 생성하지 마라:\n"
                + "\n".join(f"  - {name}" for name in duplicates)
                + "\n\n금지 이름 목록 (참고):\n"
                + "\n".join(f"  - {item.name}" for item in input_data.decision_history)
                + f"\n  - {input_data.current_step.name}\n"
            )
            output = await self.llm.invoke(retry_prompt, GenerateOutput, max_tokens=1024)
            still_duplicates = [s.name for s in output.generated_steps if _check(s.name)]
            if still_duplicates:
                logger.error(
                    json.dumps(
                        {
                            "event": "step_generator_literal_duplicate_after_retry",
                            "duplicates": still_duplicates,
                        },
                        ensure_ascii=False,
                    )
                )

        return output
