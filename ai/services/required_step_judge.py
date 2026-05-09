"""필수 Step 충족 판단 서비스 (accept 시나리오).

LLMClient만 사용하여 (RAG 없음), 현재 진행 중인 필수 Step의 목표가
충족되었는지 boolean으로 판단한다. current_required_step이 null이면
Claude를 호출하지 않고 즉시 False를 반환한다.
"""

from __future__ import annotations

import json
import logging

from ai.clients.llm import LLMClient
from ai.prompts.template import PromptTemplate
from ai.schemas.accept import AcceptInput, AcceptOutput

logger = logging.getLogger(__name__)

_SCENARIO = "accept"


class RequiredStepJudge:
    """accept 시나리오 — 필수 Step 충족 여부 boolean 판단."""

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def judge_required_step(self, input_data: AcceptInput) -> AcceptOutput:
        """필수 Step 충족 여부를 판단한다.

        흐름:
            1) current_required_step이 None → False 즉시 반환 (LLM 호출 없음)
            2) 그 외 → 프롬프트 조립 후 LLM 호출
        """
        required_step = input_data.current_required_step

        if required_step is None:
            logger.info(
                json.dumps(
                    {
                        "event": "required_step_judge_skip",
                        "project_id": str(input_data.project_info.project_id),
                        "reason": "no_current_required_step",
                    },
                    ensure_ascii=False,
                    default=str,
                )
            )
            return AcceptOutput(is_current_required_step_completed=False)

        accepted_steps_json = json.dumps(
            [step.model_dump(mode='json') for step in input_data.accepted_steps_in_required],
            ensure_ascii=False,
        )
        fulfillment_criteria_json = json.dumps(
            required_step.fulfillment_criteria,
            ensure_ascii=False,
        )

        prompt = PromptTemplate.load_and_render(
            _SCENARIO,
            required_step_name=required_step.name,
            required_step_goal=required_step.goal,
            fulfillment_criteria=fulfillment_criteria_json,
            minimum_fulfillment_count=str(required_step.minimum_fulfillment_count),
            accepted_steps_in_required=accepted_steps_json,
            accepted_step_name=input_data.accepted_step.name,
        )

        logger.info(
            json.dumps(
                {
                    "event": "required_step_judge_invoke",
                    "project_id": str(input_data.project_info.project_id),
                    "required_step_id": required_step.step_id,
                    "required_step_name": required_step.name,
                    "num_accepted_steps": len(input_data.accepted_steps_in_required),
                    "num_aspects": len(required_step.fulfillment_criteria),
                    "threshold": required_step.minimum_fulfillment_count,
                    "prompt_len": len(prompt),
                },
                ensure_ascii=False,
                default=str,
            )
        )

        return await self.llm.invoke(prompt, AcceptOutput, max_tokens=256)
