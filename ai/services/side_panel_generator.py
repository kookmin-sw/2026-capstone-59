"""사이드패널 콘텐츠 생성 서비스 (side_panel 시나리오, 일반 Step 전용).

LLMClient + RAGClient를 조합하여, DOJ KB와 Custom KB 검색 결과를 합쳐
프롬프트로 조립하고 Claude를 호출해 일반 Step 사이드패널 콘텐츠를 생성한다.
필수 Step의 사이드패널은 DB 사전 제작이므로 이 서비스는 호출되지 않는다.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, AsyncIterator, Optional

from ai.clients.llm import LLMClient
from ai.clients.rag import RAGClient
from ai.prompts.template import PromptTemplate
from ai.schemas.common import RetrievedChunk
from ai.schemas.side_panel import SidePanelInput, SidePanelOutput
from ai.services.position_label import resolve_position_label

logger = logging.getLogger(__name__)

_SCENARIO = "side_panel"
_NONE_LABEL = "없음"


def _format_rag_context(
    doj_chunks: list[RetrievedChunk],
    custom_chunks: list[RetrievedChunk],
) -> str:
    """DOJ + Custom 검색 결과를 프롬프트용 텍스트로 합쳐 포맷팅."""
    sections: list[str] = []

    if doj_chunks:
        sections.append("[DOJ SDLC]")
        sections.extend(chunk.text for chunk in doj_chunks)

    if custom_chunks:
        sections.append("[자체 문서]")
        sections.extend(chunk.text for chunk in custom_chunks)

    if not sections:
        return _NONE_LABEL

    return "\n".join(sections)


def _coerce(value: Any, default: str = _NONE_LABEL) -> str:
    """None을 default 라벨로 변환."""
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


class SidePanelGenerator:
    """side_panel 시나리오 — 일반 Step 사이드패널 콘텐츠 동적 생성."""

    def __init__(
        self,
        llm: LLMClient,
        rag: RAGClient,
        doj_data_source_id: Optional[str] = None,
        custom_data_source_id: Optional[str] = None,
    ) -> None:
        self.llm = llm
        self.rag = rag
        self.doj_data_source_id = doj_data_source_id
        self.custom_data_source_id = custom_data_source_id

    def _build_prompt(
        self,
        input_data: SidePanelInput,
        doj_chunks: list[RetrievedChunk],
        custom_chunks: list[RetrievedChunk],
    ) -> str:
        stage = input_data.current_stage
        project = input_data.project_info
        target = input_data.target_step

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

        rag_context_text = _format_rag_context(doj_chunks, custom_chunks)

        # position_label은 LLM 참고용 (강제 X). description 첫 문장에 활용해도 좋음.
        position_label = resolve_position_label(
            stage_sequence=stage.stage_sequence,
            current_required_step=input_data.current_required_step,
        )

        return PromptTemplate.load_and_render(
            _SCENARIO,
            project_name=_coerce(project.name),
            duration_months=str(project.duration_months),
            member_count=str(project.member_count),
            description=_coerce(project.description),
            constraints=_format_constraints(project.constraints),
            initial_prompt=project.initial_prompt,
            stage_sequence=str(stage.stage_sequence),
            stage_name=stage.name,
            target_step_name=target.name,
            decision_history=decision_history_json,
            current_required_step_info=required_step_info,
            rag_context=rag_context_text,
            position_label=position_label,
        )

    async def generate_side_panel(self, input_data: SidePanelInput) -> SidePanelOutput:
        """입력을 받아 Claude로 사이드패널 콘텐츠를 생성한다.

        흐름:
            1) RAG 병렬 검색 (DOJ + Custom)
            2) 프롬프트 조립
            3) LLM 호출 → SidePanelOutput 검증
        """
        stage = input_data.current_stage
        project = input_data.project_info
        target = input_data.target_step

        doj_query = f"Stage {stage.stage_sequence} {stage.name} {target.name}"
        custom_query = target.name

        doj_chunks, custom_chunks = await asyncio.gather(
            self.rag.search_doj(
                doj_query,
                num_results=3,
                data_source_id=self.doj_data_source_id,
            ),
            self.rag.search_custom(
                custom_query,
                num_results=2,
                data_source_id=self.custom_data_source_id,
            ),
        )

        prompt = self._build_prompt(input_data, doj_chunks, custom_chunks)

        logger.info(
            json.dumps(
                {
                    "event": "side_panel_generator_invoke",
                    "project_id": str(project.project_id),
                    "stage_sequence": stage.stage_sequence,
                    "target_step_name": target.name,
                    "doj_chunks": len(doj_chunks),
                    "custom_chunks": len(custom_chunks),
                    "has_required_step": input_data.current_required_step is not None,
                    "prompt_len": len(prompt),
                },
                ensure_ascii=False,
                default=str,
            )
        )

        return await self.llm.invoke(prompt, SidePanelOutput, max_tokens=2048)

    async def generate_stream(
        self, input_data: SidePanelInput
    ) -> AsyncIterator[str]:
        """사이드패널 콘텐츠를 Bedrock 스트리밍으로 yield.

        프롬프트 조립은 sync 경로(_build_prompt)와 공유하여 byte-identical.
        LLM 호출은 invoke_stream으로 대체하며 청크는 변형 없이 그대로 yield.
        """
        stage = input_data.current_stage
        project = input_data.project_info
        target = input_data.target_step

        doj_query = f"Stage {stage.stage_sequence} {stage.name} {target.name}"
        custom_query = target.name

        doj_chunks, custom_chunks = await asyncio.gather(
            self.rag.search_doj(
                doj_query,
                num_results=3,
                data_source_id=self.doj_data_source_id,
            ),
            self.rag.search_custom(
                custom_query,
                num_results=2,
                data_source_id=self.custom_data_source_id,
            ),
        )

        prompt = self._build_prompt(input_data, doj_chunks, custom_chunks)

        logger.info(
            json.dumps(
                {
                    "event": "side_panel_stream_start",
                    "project_id": str(project.project_id),
                    "stage_sequence": stage.stage_sequence,
                    "target_step_name": target.name,
                    "doj_chunks": len(doj_chunks),
                    "custom_chunks": len(custom_chunks),
                    "has_required_step": input_data.current_required_step is not None,
                    "prompt_len": len(prompt),
                },
                ensure_ascii=False,
                default=str,
            )
        )

        async for chunk in self.llm.invoke_stream(prompt, max_tokens=2048):
            yield chunk
