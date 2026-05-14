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
from ai.prompts.template import PromptTemplate
from ai.schemas.common import RetrievedChunk
from ai.schemas.generate import GenerateInput, GenerateOutput

logger = logging.getLogger(__name__)

_SCENARIO = "generate"
_NONE_LABEL = "없음"


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

        return await self.llm.invoke(prompt, GenerateOutput, max_tokens=1024)
