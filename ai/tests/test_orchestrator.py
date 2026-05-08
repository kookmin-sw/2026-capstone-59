"""ai/services/__init__.py 오케스트레이터 단위 테스트.

3개 public async 함수가 boto3 클라이언트를 받아 올바른 LLM/RAG 와이어링을
수행하고 적절한 Pydantic 출력을 반환하는지 검증한다.
"""

from __future__ import annotations

import io
import json
from typing import Any, Optional
from unittest.mock import MagicMock

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
    accept_and_generate,
    accept_and_generate_with_side_panels,
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
        constraints="React + FastAPI",
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
# Bedrock mock factories
# ---------------------------------------------------------------------------


def _bedrock_runtime_mock(payload: dict) -> MagicMock:
    """invoke_model이 주어진 payload를 Claude 응답 형식으로 반환하는 mock."""
    envelope = {"content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}]}
    raw = json.dumps(envelope, ensure_ascii=False).encode("utf-8")

    mock = MagicMock()
    mock.invoke_model.side_effect = lambda **_: {"body": io.BytesIO(raw)}
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
        runtime = _bedrock_runtime_mock(_valid_generate_payload())
        agent = _bedrock_agent_mock([{"text": "DOJ 청크", "score": 0.9}])

        result = await generate_steps(
            input_data=_generate_input(),
            bedrock_runtime_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )

        assert isinstance(result, GenerateOutput)
        assert len(result.generated_steps) == 3
        assert result.generated_steps[0].name == "Step 1"

    @pytest.mark.asyncio
    async def test_uses_provided_model_id_in_invoke_model(self):
        runtime = _bedrock_runtime_mock(_valid_generate_payload())
        agent = _bedrock_agent_mock()

        await generate_steps(
            input_data=_generate_input(),
            bedrock_runtime_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )

        kwargs = runtime.invoke_model.call_args.kwargs
        assert kwargs["modelId"] == _MODEL_ID

    @pytest.mark.asyncio
    async def test_uses_provided_kb_id_in_retrieve(self):
        runtime = _bedrock_runtime_mock(_valid_generate_payload())
        agent = _bedrock_agent_mock()

        await generate_steps(
            input_data=_generate_input(),
            bedrock_runtime_client=runtime,
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
        runtime = _bedrock_runtime_mock(_valid_generate_payload())
        agent = MagicMock()
        agent.retrieve.side_effect = RuntimeError("KB 다운")

        result = await generate_steps(
            input_data=_generate_input(),
            bedrock_runtime_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )

        assert isinstance(result, GenerateOutput)
        runtime.invoke_model.assert_called_once()


# ---------------------------------------------------------------------------
# judge_required_step
# ---------------------------------------------------------------------------


class TestJudgeRequiredStep:
    @pytest.mark.asyncio
    async def test_returns_accept_output_true(self):
        runtime = _bedrock_runtime_mock({"is_current_required_step_completed": True})

        result = await judge_required_step(
            input_data=_accept_input(),
            bedrock_runtime_client=runtime,
            model_id=_MODEL_ID,
        )

        assert isinstance(result, AcceptOutput)
        assert result.is_current_required_step_completed is True

    @pytest.mark.asyncio
    async def test_returns_accept_output_false(self):
        runtime = _bedrock_runtime_mock({"is_current_required_step_completed": False})

        result = await judge_required_step(
            input_data=_accept_input(),
            bedrock_runtime_client=runtime,
            model_id=_MODEL_ID,
        )

        assert isinstance(result, AcceptOutput)
        assert result.is_current_required_step_completed is False

    @pytest.mark.asyncio
    async def test_uses_provided_model_id(self):
        runtime = _bedrock_runtime_mock({"is_current_required_step_completed": True})

        await judge_required_step(
            input_data=_accept_input(),
            bedrock_runtime_client=runtime,
            model_id=_MODEL_ID,
        )

        kwargs = runtime.invoke_model.call_args.kwargs
        assert kwargs["modelId"] == _MODEL_ID

    @pytest.mark.asyncio
    async def test_skip_when_current_required_step_is_none(self):
        # current_required_step=None → LLM 호출 없이 즉시 False 반환
        runtime = MagicMock()
        runtime.invoke_model = MagicMock()

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
            bedrock_runtime_client=runtime,
            model_id=_MODEL_ID,
        )

        assert isinstance(result, AcceptOutput)
        assert result.is_current_required_step_completed is False
        runtime.invoke_model.assert_not_called()


# ---------------------------------------------------------------------------
# generate_side_panel
# ---------------------------------------------------------------------------


class TestGenerateSidePanel:
    @pytest.mark.asyncio
    async def test_returns_side_panel_output(self):
        runtime = _bedrock_runtime_mock(_valid_side_panel_payload())
        agent = _bedrock_agent_mock([{"text": "DOJ 청크", "score": 0.9}])

        result = await generate_side_panel(
            input_data=_side_panel_input(),
            bedrock_runtime_client=runtime,
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
        runtime = _bedrock_runtime_mock(_valid_side_panel_payload())
        agent = _bedrock_agent_mock()

        await generate_side_panel(
            input_data=_side_panel_input(),
            bedrock_runtime_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )

        assert runtime.invoke_model.call_args.kwargs["modelId"] == _MODEL_ID
        # search_doj + search_custom 모두 같은 KB ID 사용
        for call in agent.retrieve.call_args_list:
            assert call.kwargs["knowledgeBaseId"] == _KB_ID

    @pytest.mark.asyncio
    async def test_calls_both_doj_and_custom_kb(self):
        runtime = _bedrock_runtime_mock(_valid_side_panel_payload())
        agent = _bedrock_agent_mock()

        await generate_side_panel(
            input_data=_side_panel_input(),
            bedrock_runtime_client=runtime,
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
        runtime_gen = _bedrock_runtime_mock(_valid_generate_payload())
        agent_gen = _bedrock_agent_mock()
        gen_result = await generate_steps(
            input_data=_generate_input(),
            bedrock_runtime_client=runtime_gen,
            bedrock_agent_client=agent_gen,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )
        assert isinstance(gen_result, GenerateOutput)

        runtime_acc = _bedrock_runtime_mock({"is_current_required_step_completed": True})
        acc_result = await judge_required_step(
            input_data=_accept_input(),
            bedrock_runtime_client=runtime_acc,
            model_id=_MODEL_ID,
        )
        assert isinstance(acc_result, AcceptOutput)

        runtime_sp = _bedrock_runtime_mock(_valid_side_panel_payload())
        agent_sp = _bedrock_agent_mock()
        sp_result = await generate_side_panel(
            input_data=_side_panel_input(),
            bedrock_runtime_client=runtime_sp,
            bedrock_agent_client=agent_sp,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )
        assert isinstance(sp_result, SidePanelOutput)

    @pytest.mark.asyncio
    async def test_injected_mock_clients_are_actually_called(self):
        """의존성 주입 패턴 동작 확인 — 주입한 mock의 invoke_model/retrieve가 호출되어야 한다."""
        runtime = _bedrock_runtime_mock(_valid_generate_payload())
        agent = _bedrock_agent_mock()

        await generate_steps(
            input_data=_generate_input(),
            bedrock_runtime_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )

        runtime.invoke_model.assert_called_once()
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
# accept_and_generate
# ---------------------------------------------------------------------------


def _runtime_mock_for_accept_and_generate() -> MagicMock:
    """accept → generate 순으로 invoke_model이 두 번 호출될 때 각각 올바른 응답을 반환."""
    import io as _io
    import json as _json

    def _make_body(payload: dict) -> dict:
        envelope = {"content": [{"type": "text", "text": _json.dumps(payload, ensure_ascii=False)}]}
        return {"body": _io.BytesIO(_json.dumps(envelope, ensure_ascii=False).encode("utf-8"))}

    mock = MagicMock()
    mock.invoke_model.side_effect = [
        _make_body({"is_current_required_step_completed": True}),
        _make_body(_valid_generate_payload()),
    ]
    return mock


class TestAcceptAndGenerate:
    @pytest.mark.asyncio
    async def test_returns_tuple_of_correct_types(self):
        """병렬 실행 정상 흐름: (AcceptOutput, GenerateOutput) 튜플 반환."""
        runtime = _runtime_mock_for_accept_and_generate()
        agent = _bedrock_agent_mock()

        result = await accept_and_generate(
            accept_input=_accept_input(),
            generate_input=_generate_input(),
            bedrock_runtime_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )

        assert isinstance(result, tuple)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_each_element_has_correct_type(self):
        """반환 타입 검증: AcceptOutput과 GenerateOutput 각각."""
        runtime = _runtime_mock_for_accept_and_generate()
        agent = _bedrock_agent_mock()

        accept_result, generate_result = await accept_and_generate(
            accept_input=_accept_input(),
            generate_input=_generate_input(),
            bedrock_runtime_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )

        assert isinstance(accept_result, AcceptOutput)
        assert isinstance(generate_result, GenerateOutput)
        assert accept_result.is_current_required_step_completed is True
        assert len(generate_result.generated_steps) == 3

    @pytest.mark.asyncio
    async def test_both_clients_called(self):
        """병렬성 검증: runtime.invoke_model 2회, agent.retrieve 1회 호출."""
        runtime = _runtime_mock_for_accept_and_generate()
        agent = _bedrock_agent_mock()

        await accept_and_generate(
            accept_input=_accept_input(),
            generate_input=_generate_input(),
            bedrock_runtime_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )

        # accept(invoke) + generate(invoke) = 2회
        assert runtime.invoke_model.call_count == 2
        # generate만 RAG 사용 = 1회
        assert agent.retrieve.call_count == 1


# ---------------------------------------------------------------------------
# accept_and_generate_with_side_panels
# ---------------------------------------------------------------------------


def _runtime_mock_for_full_pipeline() -> MagicMock:
    """accept(1) + generate(1) + side_panel×3(3) = invoke_model 5회 응답."""
    import io as _io
    import json as _json

    def _make_body(payload: dict) -> dict:
        envelope = {"content": [{"type": "text", "text": _json.dumps(payload, ensure_ascii=False)}]}
        return {"body": _io.BytesIO(_json.dumps(envelope, ensure_ascii=False).encode("utf-8"))}

    mock = MagicMock()
    mock.invoke_model.side_effect = [
        _make_body({"is_current_required_step_completed": True}),   # accept
        _make_body(_valid_generate_payload()),                        # generate
        _make_body(_valid_side_panel_payload()),                     # side_panel Step 1
        _make_body(_valid_side_panel_payload()),                     # side_panel Step 2
        _make_body(_valid_side_panel_payload()),                     # side_panel Step 3
    ]
    return mock


class TestAcceptAndGenerateWithSidePanels:
    @pytest.mark.asyncio
    async def test_returns_correct_types(self):
        """반환 타입 검증: (AcceptOutput, GenerateOutput, list[SidePanelOutput])."""
        runtime = _runtime_mock_for_full_pipeline()
        agent = _bedrock_agent_mock()

        result = await accept_and_generate_with_side_panels(
            accept_input=_accept_input(),
            generate_input=_generate_input(),
            bedrock_runtime_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )

        accept_result, generate_result, sp_list = result
        assert isinstance(accept_result, AcceptOutput)
        assert isinstance(generate_result, GenerateOutput)
        assert isinstance(sp_list, list)
        assert all(isinstance(sp, SidePanelOutput) for sp in sp_list)

    @pytest.mark.asyncio
    async def test_side_panel_list_has_three_items(self):
        """list[SidePanelOutput] 길이가 정확히 3."""
        runtime = _runtime_mock_for_full_pipeline()
        agent = _bedrock_agent_mock()

        _, _, sp_list = await accept_and_generate_with_side_panels(
            accept_input=_accept_input(),
            generate_input=_generate_input(),
            bedrock_runtime_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )

        assert len(sp_list) == 3

    @pytest.mark.asyncio
    async def test_invoke_and_retrieve_call_counts(self):
        """invoke_model 5회 (accept 1 + generate 1 + side_panel 3), retrieve 7회 (generate 1 + side_panel 3×2)."""
        runtime = _runtime_mock_for_full_pipeline()
        agent = _bedrock_agent_mock()

        await accept_and_generate_with_side_panels(
            accept_input=_accept_input(),
            generate_input=_generate_input(),
            bedrock_runtime_client=runtime,
            bedrock_agent_client=agent,
            model_id=_MODEL_ID,
            kb_id=_KB_ID,
        )

        assert runtime.invoke_model.call_count == 5
        # generate: DOJ 1회 / side_panel 각 DOJ+Custom 2회 × 3 = 7회 합계
        assert agent.retrieve.call_count == 7
