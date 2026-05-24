"""ai/services/__init__.py 오케스트레이터 단위 테스트 — Anthropic Direct API (이슈 #232).

3개 public async 함수가 AsyncAnthropic + bedrock-agent-runtime 클라이언트를 받아
올바른 LLM/RAG 와이어링을 수행하고 적절한 Pydantic 출력을 반환하는지 검증한다.
"""

from __future__ import annotations

import json
from typing import Any, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

from ai.schemas.accept import AcceptInput, AcceptOutput
from ai.schemas.common import (
    DecisionHistoryItem,
    ProjectInfo,
    RequiredStepInfo,
    RequiredStepStatus,
    StageInfo,
    StepInfo,
)
from ai.schemas.generate import GenerateInput, GenerateOutput
from ai.schemas.side_panel import SidePanelInput, SidePanelOutput
from ai.services import (
    generate_side_panel,
    generate_steps,
    judge_required_step,
)


_MODEL_ID = "test-model-id"
_KB_ID = "test-kb-id"


# ---------------------------------------------------------------------------
# 입력 fixtures
# ---------------------------------------------------------------------------


def _project() -> ProjectInfo:
    return ProjectInfo(
        project_id="proj-1",
        name="테스트 프로젝트",
        duration_months=3,
        member_count=4,
        description="설명",
        constraints=["React + FastAPI"],
        initial_prompt="초기 아이디어",
    )


def _stage() -> StageInfo:
    return StageInfo(stage_id="stage-1", stage_sequence=1, name="아이디어 구체화")


def _required_step() -> RequiredStepInfo:
    return RequiredStepInfo(
        step_id="rs-1",
        name="문제/기회 정의",
        is_completed=False,
        goal="문제를 명확히 정의",
        entry_criteria="초기 프롬프트만으로 진입 가능",
        fulfillment_criteria=[
            "문제 서술",
            "중요도 분석",
            "발생 배경",
            "기존 대안 한계",
        ],
        minimum_fulfillment_count=2,
    )


def _generate_input() -> GenerateInput:
    return GenerateInput(
        project_info=_project(),
        current_stage=_stage(),
        decision_history=[
            DecisionHistoryItem(step_id="s0", name="시작", status="ACCEPTED"),
        ],
        current_step=StepInfo(step_id="s0", name="시작"),
        current_required_step=_required_step(),
    )


def _accept_input() -> AcceptInput:
    return AcceptInput(
        project_info=_project(),
        current_stage=_stage(),
        required_steps_status=[
            RequiredStepStatus(name="문제/기회 정의", order=1, is_completed=False),
        ],
        current_required_step=_required_step(),
        accepted_steps_in_required=[
            StepInfo(step_id="s1", name="문제 정리"),
        ],
        accepted_step=StepInfo(step_id="s1", name="문제 정리"),
    )


def _side_panel_input() -> SidePanelInput:
    return SidePanelInput(
        project_info=_project(),
        current_stage=_stage(),
        target_step=StepInfo(step_id="ts-1", name="경쟁 서비스 조사"),
        decision_history=[],
        current_required_step=_required_step(),
    )


# ---------------------------------------------------------------------------
# Mock factories
# ---------------------------------------------------------------------------


def _anthropic_mock(payload: dict) -> MagicMock:
    """messages.create가 주어진 payload를 Claude 응답 형식으로 반환하는 mock."""
    text_payload = json.dumps(payload, ensure_ascii=False)

    def _response(**_):
        msg = MagicMock()
        msg.content = [MagicMock(text=text_payload)]
        return msg

    mock = MagicMock()
    mock.messages = MagicMock()
    mock.messages.create = AsyncMock(side_effect=_response)
    return mock


def _bedrock_agent_mock(chunks: Optional[list[dict[str, Any]]] = None) -> MagicMock:
    """retrieve가 주어진 청크를 반환하는 mock."""
    chunks = chunks or []
    retrieval_results = [
        {"content": {"text": chunk["text"]}, "score": chunk.get("score", 0.9)}
        for chunk in chunks
    ]
    mock = MagicMock()
    mock.retrieve.return_value = {"retrievalResults": retrieval_results}
    return mock


def _valid_generate_payload() -> dict:
    return {
        "generated_steps": [
            {"name": "Step 1", "description": "활동 1"},
            {"name": "Step 2", "description": "활동 2"},
            {"name": "Step 3", "description": "활동 3"},
        ]
    }


def _valid_side_panel_payload() -> dict:
    return {
        "mentoring": {
            "description": "이 Step에서는 ...",
            "recommended_methods": [
                {"title": "방법 1", "content": "내용 1"},
                {"title": "방법 2", "content": "내용 2"},
            ],
            "common_mistakes": [
                {
                    "mistake": "흔한 실수 1",
                    "bad_example": "나쁜 예",
                    "good_example": "좋은 예",
                },
            ],
            "one_line_tip": "핵심을 한 줄로.",
        },
        "dictionary": [
            {"term": "페르소나", "definition": "타겟 사용자 모델"},
            {"term": "MVP", "definition": "최소 기능 제품"},
        ],
    }


# ---------------------------------------------------------------------------
# generate_steps
# ---------------------------------------------------------------------------


class TestGenerateSteps:
    @pytest.mark.asyncio
    async def test_returns_generate_output(self):
        runtime = _anthropic_mock(_valid_generate_payload())
        agent = _bedrock_agent_mock([{"text": "DOJ 청크", "score": 0.9}])

        result = await generate_steps(
            input_data=_generate_input(),
            anthropic_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )

        assert isinstance(result, GenerateOutput)
        assert len(result.generated_steps) == 3
        assert result.generated_steps[0].name == "Step 1"

    @pytest.mark.asyncio
    async def test_uses_provided_model_id(self):
        runtime = _anthropic_mock(_valid_generate_payload())
        agent = _bedrock_agent_mock()

        await generate_steps(
            input_data=_generate_input(),
            anthropic_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )

        kwargs = runtime.messages.create.call_args.kwargs
        assert kwargs["model"] == _MODEL_ID

    @pytest.mark.asyncio
    async def test_uses_provided_kb_id_in_retrieve(self):
        runtime = _anthropic_mock(_valid_generate_payload())
        agent = _bedrock_agent_mock()

        await generate_steps(
            input_data=_generate_input(),
            anthropic_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )

        agent.retrieve.assert_called_once()
        kwargs = agent.retrieve.call_args.kwargs
        assert kwargs["knowledgeBaseId"] == _KB_ID

    @pytest.mark.asyncio
    async def test_rag_failure_is_non_fatal(self):
        # RAG가 예외를 던져도 LLM 호출은 진행되어야 한다 (RAGClient가 [] 반환)
        runtime = _anthropic_mock(_valid_generate_payload())
        agent = MagicMock()
        agent.retrieve.side_effect = RuntimeError("KB 다운")

        result = await generate_steps(
            input_data=_generate_input(),
            anthropic_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )

        assert isinstance(result, GenerateOutput)
        runtime.messages.create.assert_called_once()


# ---------------------------------------------------------------------------
# judge_required_step
# ---------------------------------------------------------------------------


class TestJudgeRequiredStep:
    @pytest.mark.asyncio
    async def test_returns_accept_output_true(self):
        runtime = _anthropic_mock({"is_current_required_step_completed": True})

        result = await judge_required_step(
            input_data=_accept_input(),
            anthropic_client=runtime,
            model_id=_MODEL_ID,
        )

        assert isinstance(result, AcceptOutput)
        assert result.is_current_required_step_completed is True

    @pytest.mark.asyncio
    async def test_returns_accept_output_false(self):
        runtime = _anthropic_mock({"is_current_required_step_completed": False})

        result = await judge_required_step(
            input_data=_accept_input(),
            anthropic_client=runtime,
            model_id=_MODEL_ID,
        )

        assert isinstance(result, AcceptOutput)
        assert result.is_current_required_step_completed is False

    @pytest.mark.asyncio
    async def test_uses_provided_model_id(self):
        runtime = _anthropic_mock({"is_current_required_step_completed": True})

        await judge_required_step(
            input_data=_accept_input(),
            anthropic_client=runtime,
            model_id=_MODEL_ID,
        )

        kwargs = runtime.messages.create.call_args.kwargs
        assert kwargs["model"] == _MODEL_ID

    @pytest.mark.asyncio
    async def test_skip_when_current_required_step_is_none(self):
        # current_required_step=None → LLM 호출 없이 즉시 False 반환
        runtime = MagicMock()
        # (auto-created via MagicMock attribute access)

        input_data = AcceptInput(
            project_info=_project(),
            current_stage=_stage(),
            required_steps_status=[],
            current_required_step=None,
            accepted_steps_in_required=[],
            accepted_step=StepInfo(step_id="s0", name="아무거나"),
        )

        result = await judge_required_step(
            input_data=input_data,
            anthropic_client=runtime,
            model_id=_MODEL_ID,
        )

        assert isinstance(result, AcceptOutput)
        assert result.is_current_required_step_completed is False
        runtime.messages.create.assert_not_called()


# ---------------------------------------------------------------------------
# generate_side_panel
# ---------------------------------------------------------------------------


class TestGenerateSidePanel:
    @pytest.mark.asyncio
    async def test_returns_side_panel_output(self):
        runtime = _anthropic_mock(_valid_side_panel_payload())
        agent = _bedrock_agent_mock([{"text": "DOJ 청크", "score": 0.9}])

        result = await generate_side_panel(
            input_data=_side_panel_input(),
            anthropic_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )

        assert isinstance(result, SidePanelOutput)
        assert result.mentoring.one_line_tip == "핵심을 한 줄로."
        assert len(result.mentoring.recommended_methods) == 2
        assert len(result.dictionary) == 2

    @pytest.mark.asyncio
    async def test_uses_provided_model_id_and_kb_id(self):
        runtime = _anthropic_mock(_valid_side_panel_payload())
        agent = _bedrock_agent_mock()

        await generate_side_panel(
            input_data=_side_panel_input(),
            anthropic_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )

        assert runtime.messages.create.call_args.kwargs["model"] == _MODEL_ID
        # search_doj + search_custom 모두 같은 KB ID 사용
        for call in agent.retrieve.call_args_list:
            assert call.kwargs["knowledgeBaseId"] == _KB_ID

    @pytest.mark.asyncio
    async def test_calls_both_doj_and_custom_kb(self):
        runtime = _anthropic_mock(_valid_side_panel_payload())
        agent = _bedrock_agent_mock()

        await generate_side_panel(
            input_data=_side_panel_input(),
            anthropic_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )

        # SidePanelGenerator가 search_doj + search_custom을 호출 → retrieve 2회
        assert agent.retrieve.call_count == 2


# ---------------------------------------------------------------------------
# Top-level re-export 검증
# ---------------------------------------------------------------------------


class TestTopLevelReexport:
    def test_three_functions_reexported(self):
        import ai

        assert ai.generate_steps is generate_steps
        assert ai.judge_required_step is judge_required_step
        assert ai.generate_side_panel is generate_side_panel


# ---------------------------------------------------------------------------
# 납품 인터페이스 검증
# ---------------------------------------------------------------------------


class TestDeliveryInterface:
    @pytest.mark.asyncio
    async def test_all_three_functions_return_correct_output_types(self):
        """3개 public 함수의 입출력 스키마 검증."""
        runtime_gen = _anthropic_mock(_valid_generate_payload())
        agent_gen = _bedrock_agent_mock()
        gen_result = await generate_steps(
            input_data=_generate_input(),
            anthropic_client=runtime_gen,
            bedrock_agent_client=agent_gen,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )
        assert isinstance(gen_result, GenerateOutput)

        runtime_acc = _anthropic_mock({"is_current_required_step_completed": True})
        acc_result = await judge_required_step(
            input_data=_accept_input(),
            anthropic_client=runtime_acc,
            model_id=_MODEL_ID,
        )
        assert isinstance(acc_result, AcceptOutput)

        runtime_sp = _anthropic_mock(_valid_side_panel_payload())
        agent_sp = _bedrock_agent_mock()
        sp_result = await generate_side_panel(
            input_data=_side_panel_input(),
            anthropic_client=runtime_sp,
            bedrock_agent_client=agent_sp,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )
        assert isinstance(sp_result, SidePanelOutput)

    @pytest.mark.asyncio
    async def test_injected_mock_clients_are_actually_called(self):
        """의존성 주입 패턴 동작 확인 — 주입한 mock의 messages.create/retrieve가 호출되어야 한다."""
        runtime = _anthropic_mock(_valid_generate_payload())
        agent = _bedrock_agent_mock()

        await generate_steps(
            input_data=_generate_input(),
            anthropic_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )

        runtime.messages.create.assert_called_once()
        agent.retrieve.assert_called_once()

    def test_orchestrator_files_no_backend_imports(self):
        """ai/services/__init__.py와 ai/__init__.py에 백엔드 전용 패키지가 없는지 AST로 검증."""
        import ast
        from pathlib import Path

        banned = {"fastapi", "sqlalchemy", "uvicorn", "alembic", "starlette", "mangum"}
        targets = [
            Path("ai/services/__init__.py"),
            Path("ai/__init__.py"),
        ]
        for path in targets:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imported: set = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".")[0])
            violations = imported & banned
            assert not violations, f"{path}: 백엔드 전용 패키지 import 발견 — {violations}"


# ---------------------------------------------------------------------------
# Data Source ID propagation — public orchestrator functions
# ---------------------------------------------------------------------------


_SYS_KEY = "x-amz-bedrock-kb-data-source-id"


class TestDataSourceIdPropagation:
    """3개 public 함수가 Data Source ID를 retrieve 호출 filter까지 전달."""

    @pytest.mark.asyncio
    async def test_generate_steps_passes_doj_id_to_retrieve(self):
        runtime = _anthropic_mock(_valid_generate_payload())
        agent = _bedrock_agent_mock([{"text": "DOJ 청크", "score": 0.9}])

        await generate_steps(
            input_data=_generate_input(),
            anthropic_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
            doj_data_source_id="POGP6P0D6Q",
        )

        agent.retrieve.assert_called_once()
        kwargs = agent.retrieve.call_args.kwargs
        vector_config = kwargs["retrievalConfiguration"]["vectorSearchConfiguration"]
        assert vector_config["filter"] == {
            "equals": {"key": _SYS_KEY, "value": "POGP6P0D6Q"}
        }

    @pytest.mark.asyncio
    async def test_generate_steps_without_id_omits_filter(self):
        runtime = _anthropic_mock(_valid_generate_payload())
        agent = _bedrock_agent_mock()

        await generate_steps(
            input_data=_generate_input(),
            anthropic_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )

        kwargs = agent.retrieve.call_args.kwargs
        vector_config = kwargs["retrievalConfiguration"]["vectorSearchConfiguration"]
        assert "filter" not in vector_config

    @pytest.mark.asyncio
    async def test_generate_side_panel_passes_both_ids(self):
        runtime = _anthropic_mock(_valid_side_panel_payload())
        agent = _bedrock_agent_mock()

        await generate_side_panel(
            input_data=_side_panel_input(),
            anthropic_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
            doj_data_source_id="POGP6P0D6Q",
            custom_data_source_id="VILRYZZZWG",
        )

        # SidePanelGenerator는 search_doj, search_custom 둘 다 호출 → retrieve 2회
        assert agent.retrieve.call_count == 2
        filters = [
            call.kwargs["retrievalConfiguration"]["vectorSearchConfiguration"][
                "filter"
            ]
            for call in agent.retrieve.call_args_list
        ]
        values = {f["equals"]["value"] for f in filters}
        assert values == {"POGP6P0D6Q", "VILRYZZZWG"}

    @pytest.mark.asyncio
    async def test_generate_side_panel_without_ids_omits_filters(self):
        runtime = _anthropic_mock(_valid_side_panel_payload())
        agent = _bedrock_agent_mock()

        await generate_side_panel(
            input_data=_side_panel_input(),
            anthropic_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )

        for call in agent.retrieve.call_args_list:
            vector_config = call.kwargs["retrievalConfiguration"][
                "vectorSearchConfiguration"
            ]
            assert "filter" not in vector_config
