"""ai/services/design_export_generator.py 단위 테스트 (v1.4 Z+).

박제: design.md §7-1-1 example tests + 프롬프트 정적 검증 + PBT (Hypothesis).
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Optional

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from ai.exceptions import (
    AIGenerationFailedError,
    BedrockAPIError,
    OutputViolatesHonestyGuardError,
)
from ai.schemas.common import (
    CommonMistake,
    MentoringContent,
    RecommendedMethod,
)
from ai.schemas.design_export import (
    AcceptedStepForAI,
    DesignExportInput,
    DesignExportOutput,
    ProjectContextForAI,
    RequiredStepForAI,
    RSQuestions,
)
from ai.services.design_export_generator import (
    DesignExportGenerator,
    _BANNED_PATTERNS,
    _scan_banned,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _project_context() -> ProjectContextForAI:
    return ProjectContextForAI(
        name="스터디 매칭 앱",
        description="대학생용 스터디 매칭 플랫폼",
        duration_months=3,
        member_count=4,
        constraints=["React + FastAPI", "AWS 프리 티어"],
        initial_prompt="학과 선후배가 스터디를 쉽게 구성할 수 있는 앱을 만들고 싶음",
    )


def _project_context_minimal() -> ProjectContextForAI:
    return ProjectContextForAI(
        duration_months=2,
        member_count=1,
        initial_prompt="개인 프로젝트",
    )


def _mentoring() -> MentoringContent:
    return MentoringContent(
        description="타겟 사용자를 파악하는 자리예요.",
        recommended_methods=[
            RecommendedMethod(
                title="타겟 사용자 인터뷰",
                content="5~10명의 타겟 사용자를 만나 현재 행동·맥락을 들어요.",
            )
        ],
        common_mistakes=[
            CommonMistake(
                mistake="친한 사람만 인터뷰하기 — 편향이 강해요",
                bad_example="친구 3명에게 물어봤다.",
                good_example="다양한 상황의 사용자 5명을 인터뷰했다.",
            )
        ],
        one_line_tip="타겟 사용자의 '하루'를 알면 페르소나가 살아 있어요.",
    )


def _accepted_step(
    name: str = "타겟 사용자 인터뷰 계획",
    with_mentoring: bool = True,
) -> AcceptedStepForAI:
    return AcceptedStepForAI(
        name=name,
        description="1차 타겟 사용자군 특성 정의 활동",
        sidepanel_mentoring=_mentoring() if with_mentoring else None,
    )


def _required_step_with_steps() -> RequiredStepForAI:
    return RequiredStepForAI(
        required_step_id="1-R2",
        required_step_name="대상 사용자 파악",
        goal="정의된 문제로 불편을 겪는 구체적 사용자군을 식별한다.",
        fulfillment_criteria=[
            "1차 타겟 사용자군의 특성 정의",
            "사용자의 현재 행동·습관·맥락 파악",
            "사용자 검증 활동",
        ],
        accepted_general_steps=[_accepted_step()],
    )


def _required_step_empty() -> RequiredStepForAI:
    return RequiredStepForAI(
        required_step_id="1-R1",
        required_step_name="문제·기회 정의",
        goal="핵심 문제 또는 기회를 서술하고 명확화한다.",
        fulfillment_criteria=[
            "문제/기회 자체에 대한 서술·명확화",
            "문제의 중요도·임팩트 분석",
        ],
        accepted_general_steps=[],
    )


def _input_full() -> DesignExportInput:
    return DesignExportInput(
        project_context=_project_context(),
        selected_required_steps=[_required_step_with_steps()],
    )


def _input_empty_steps() -> DesignExportInput:
    return DesignExportInput(
        project_context=_project_context_minimal(),
        selected_required_steps=[_required_step_empty()],
    )


def _input_multi_rs() -> DesignExportInput:
    return DesignExportInput(
        project_context=_project_context(),
        selected_required_steps=[_required_step_with_steps(), _required_step_empty()],
    )


def _valid_output(input_data: Optional[DesignExportInput] = None) -> DesignExportOutput:
    """최소 유효 DesignExportOutput — honesty guard 통과, ID 순서 일치."""
    if input_data is not None:
        rs_ids = [rs.required_step_id for rs in input_data.selected_required_steps]
    else:
        rs_ids = ["1-R2"]
    return DesignExportOutput(
        questions_per_rs=[
            RSQuestions(
                required_step_id=rid,
                questions=[
                    "이 단계에서 무엇을 목표로 했는가?",
                    "어떤 기준으로 판단할 것인가?",
                    "다음 단계로 나아가기 위해 무엇이 필요한가?",
                ],
            )
            for rid in rs_ids
        ],
        core_summary=[
            "핵심 목표를 중심으로 사고를 진행했는가?",
            "각 단계에서 무엇을 인지하고자 했는가?",
            "전체 흐름에서 어떤 방향을 선택했는가?",
        ],
    )


# ---------------------------------------------------------------------------
# MockDesignExportLLM
# ---------------------------------------------------------------------------


class MockDesignExportLLM:
    """LLMClient 대역 — return_value 또는 raise_exception 기반 제어."""

    def __init__(
        self,
        return_value: Optional[DesignExportOutput] = None,
        raise_exception: Optional[Exception] = None,
    ) -> None:
        self.return_value = return_value
        self.raise_exception = raise_exception
        self.invoke_calls: list[dict] = []
        self.invoke_stream_calls: list = []

    async def invoke(
        self,
        prompt: str,
        expected_schema: Any,
        max_retries: int = 2,
        max_tokens: Optional[int] = None,
    ) -> DesignExportOutput:
        self.invoke_calls.append(
            {
                "prompt": prompt,
                "expected_schema": expected_schema,
                "max_retries": max_retries,
                "max_tokens": max_tokens,
            }
        )
        if self.raise_exception is not None:
            raise self.raise_exception
        return self.return_value  # type: ignore[return-value]

    async def invoke_stream(self, *args: Any, **kwargs: Any) -> None:
        self.invoke_stream_calls.append((args, kwargs))
        raise AssertionError("invoke_stream should not be called in design-export")


def _make_service(
    return_value: Optional[DesignExportOutput] = None,
    raise_exception: Optional[Exception] = None,
    input_data: Optional[DesignExportInput] = None,
) -> tuple[DesignExportGenerator, MockDesignExportLLM]:
    if return_value is None and raise_exception is None:
        return_value = _valid_output(input_data if input_data is not None else _input_full())
    llm = MockDesignExportLLM(return_value=return_value, raise_exception=raise_exception)
    return DesignExportGenerator(llm=llm), llm


# ---------------------------------------------------------------------------
# 시그니처·RAG 없음 검증 (Req 15.4, 15.5)
# ---------------------------------------------------------------------------


class TestSignatureAndNoDependency:
    def test_constructor_accepts_only_llm(self):
        from unittest.mock import MagicMock
        llm = MagicMock()
        service = DesignExportGenerator(llm=llm)
        assert service.llm is llm

    @pytest.mark.asyncio
    async def test_invoke_stream_never_called(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        assert llm.invoke_stream_calls == []

    @pytest.mark.asyncio
    async def test_no_rag_client_attribute(self):
        service, _ = _make_service()
        assert not hasattr(service, "rag"), "RAG 클라이언트 속성이 존재하면 안 됨"


# ---------------------------------------------------------------------------
# 정상 흐름 (Req 10.2, 10.6)
# ---------------------------------------------------------------------------


class TestHappyPath:
    @pytest.mark.asyncio
    async def test_returns_design_export_output(self):
        service, _ = _make_service()
        result = await service.generate_design_export(_input_full())
        assert isinstance(result, DesignExportOutput)

    @pytest.mark.asyncio
    async def test_llm_invoke_called_once(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        assert len(llm.invoke_calls) == 1

    @pytest.mark.asyncio
    async def test_llm_invoke_passes_design_export_output_schema(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        assert llm.invoke_calls[0]["expected_schema"] is DesignExportOutput

    @pytest.mark.asyncio
    async def test_llm_invoke_passes_max_tokens_8192(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        assert llm.invoke_calls[0]["max_tokens"] == 8192

    @pytest.mark.asyncio
    async def test_empty_accepted_steps_input_succeeds(self):
        service, _ = _make_service(input_data=_input_empty_steps())
        result = await service.generate_design_export(_input_empty_steps())
        assert isinstance(result, DesignExportOutput)

    @pytest.mark.asyncio
    async def test_multi_rs_input_succeeds(self):
        service, _ = _make_service(input_data=_input_multi_rs())
        result = await service.generate_design_export(_input_multi_rs())
        assert isinstance(result, DesignExportOutput)
        assert len(result.questions_per_rs) == 2


# ---------------------------------------------------------------------------
# 프롬프트 조립 검증
# ---------------------------------------------------------------------------


class TestPromptAssembly:
    @pytest.mark.asyncio
    async def test_prompt_contains_project_name(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        assert "스터디 매칭 앱" in llm.invoke_calls[0]["prompt"]

    @pytest.mark.asyncio
    async def test_prompt_contains_member_count(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        assert "4명" in llm.invoke_calls[0]["prompt"]

    @pytest.mark.asyncio
    async def test_prompt_contains_initial_prompt(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        assert "학과 선후배가 스터디를 쉽게 구성할 수 있는 앱을 만들고 싶음" in llm.invoke_calls[0]["prompt"]

    @pytest.mark.asyncio
    async def test_prompt_contains_constraints(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        assert "React + FastAPI" in llm.invoke_calls[0]["prompt"]

    @pytest.mark.asyncio
    async def test_prompt_contains_required_step_name(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        assert "대상 사용자 파악" in llm.invoke_calls[0]["prompt"]

    @pytest.mark.asyncio
    async def test_prompt_contains_goal(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        assert "정의된 문제로 불편을 겪는 구체적 사용자군을 식별한다" in llm.invoke_calls[0]["prompt"]

    @pytest.mark.asyncio
    async def test_prompt_contains_fulfillment_criteria(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        assert "1차 타겟 사용자군의 특성 정의" in llm.invoke_calls[0]["prompt"]

    @pytest.mark.asyncio
    async def test_prompt_contains_accepted_step_name(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        assert "타겟 사용자 인터뷰 계획" in llm.invoke_calls[0]["prompt"]

    @pytest.mark.asyncio
    async def test_prompt_empty_steps_contains_fallback_label(self):
        service, llm = _make_service(input_data=_input_empty_steps())
        await service.generate_design_export(_input_empty_steps())
        assert "없음" in llm.invoke_calls[0]["prompt"]

    @pytest.mark.asyncio
    async def test_no_unresolved_placeholders_in_prompt(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        prompt = llm.invoke_calls[0]["prompt"]
        for slot in ["{project_context_block}", "{selected_required_steps_block}"]:
            assert slot not in prompt, f"미치환 슬롯: {slot}"

    @pytest.mark.asyncio
    async def test_minimal_project_none_fields_use_placeholder(self):
        service, llm = _make_service(input_data=_input_empty_steps())
        await service.generate_design_export(_input_empty_steps())
        assert "(미입력)" in llm.invoke_calls[0]["prompt"]

    @pytest.mark.asyncio
    async def test_prompt_contains_mentoring_content(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        assert "타겟 사용자 인터뷰" in llm.invoke_calls[0]["prompt"]


# ---------------------------------------------------------------------------
# 표현 정직성 가드 (Req 9.3, design.md §3-7-2)
# ---------------------------------------------------------------------------


class TestHonestyGuardValidation:
    @pytest.mark.parametrize(
        "banned_text",
        [
            "답한 질문",
            "검토한 질문",
            "사고가 정리된 상태",
            "결론을 내린 영역",
            "답했다",
            "답한 상태",
        ],
    )
    @pytest.mark.asyncio
    async def test_banned_pattern_in_question_raises(self, banned_text: str):
        output = DesignExportOutput(
            questions_per_rs=[
                RSQuestions(
                    required_step_id="1-R2",
                    questions=[
                        f"이 단계에서 {banned_text}은 무엇인가?",
                        "두 번째 질문은?",
                        "세 번째 질문은?",
                    ],
                )
            ],
            core_summary=[
                "핵심 정리 1.",
                "핵심 정리 2.",
                "핵심 정리 3.",
            ],
        )
        service, _ = _make_service(return_value=output)
        with pytest.raises(OutputViolatesHonestyGuardError):
            await service.generate_design_export(_input_full())

    @pytest.mark.asyncio
    async def test_banned_pattern_in_core_summary_raises(self):
        output = DesignExportOutput(
            questions_per_rs=[
                RSQuestions(
                    required_step_id="1-R2",
                    questions=[
                        "첫 번째 질문?",
                        "두 번째 질문?",
                        "세 번째 질문?",
                    ],
                )
            ],
            core_summary=[
                "사용자가 답했다는 것을 알 수 있다.",
                "핵심 정리 2.",
                "핵심 정리 3.",
            ],
        )
        service, _ = _make_service(return_value=output)
        with pytest.raises(OutputViolatesHonestyGuardError):
            await service.generate_design_export(_input_full())

    @pytest.mark.asyncio
    async def test_honesty_violation_details_contains_banned_phrase(self):
        output = DesignExportOutput(
            questions_per_rs=[
                RSQuestions(
                    required_step_id="1-R2",
                    questions=[
                        "이 단계에서 답한 질문은 무엇인가?",
                        "두 번째 질문?",
                        "세 번째 질문?",
                    ],
                )
            ],
            core_summary=["정리 1.", "정리 2.", "정리 3."],
        )
        service, _ = _make_service(return_value=output)
        with pytest.raises(OutputViolatesHonestyGuardError) as exc_info:
            await service.generate_design_export(_input_full())
        assert "banned_phrase" in exc_info.value.details

    @pytest.mark.asyncio
    async def test_no_retry_after_honesty_violation(self):
        output = DesignExportOutput(
            questions_per_rs=[
                RSQuestions(
                    required_step_id="1-R2",
                    questions=["검토한 질문.", "두 번째.", "세 번째."],
                )
            ],
            core_summary=["정리 1.", "정리 2.", "정리 3."],
        )
        service, llm = _make_service(return_value=output)
        with pytest.raises(OutputViolatesHonestyGuardError):
            await service.generate_design_export(_input_full())
        assert len(llm.invoke_calls) == 1


# ---------------------------------------------------------------------------
# questions_per_rs ID 매칭 검증
# ---------------------------------------------------------------------------


class TestIDMatchingValidation:
    @pytest.mark.asyncio
    async def test_mismatched_ids_raises_honesty_guard_error(self):
        output = DesignExportOutput(
            questions_per_rs=[
                RSQuestions(
                    required_step_id="9-R9",  # 입력과 불일치
                    questions=["질문 1?", "질문 2?", "질문 3?"],
                )
            ],
            core_summary=["정리 1.", "정리 2.", "정리 3."],
        )
        service, _ = _make_service(return_value=output)
        with pytest.raises(OutputViolatesHonestyGuardError) as exc_info:
            await service.generate_design_export(_input_full())
        assert "expected" in exc_info.value.details
        assert "actual" in exc_info.value.details

    @pytest.mark.asyncio
    async def test_correct_ids_passes(self):
        output = _valid_output(_input_full())
        service, _ = _make_service(return_value=output)
        result = await service.generate_design_export(_input_full())
        assert result.questions_per_rs[0].required_step_id == "1-R2"

    @pytest.mark.asyncio
    async def test_multi_rs_id_order_mismatch_raises(self):
        output = DesignExportOutput(
            questions_per_rs=[
                RSQuestions(
                    required_step_id="1-R1",  # 순서 바뀜
                    questions=["질문 1?", "질문 2?", "질문 3?"],
                ),
                RSQuestions(
                    required_step_id="1-R2",  # 순서 바뀜
                    questions=["질문 1?", "질문 2?", "질문 3?"],
                ),
            ],
            core_summary=["정리 1.", "정리 2.", "정리 3."],
        )
        service, _ = _make_service(return_value=output)
        with pytest.raises(OutputViolatesHonestyGuardError):
            await service.generate_design_export(_input_multi_rs())


# ---------------------------------------------------------------------------
# LLM 실패 전파 (Req 12.1, 12.2)
# ---------------------------------------------------------------------------


class TestLLMErrorPropagation:
    @pytest.mark.asyncio
    async def test_bedrock_api_error_propagates(self):
        err = BedrockAPIError(
            message="Bedrock API 호출에 실패했습니다.",
            details={"error_type": "ClientError"},
        )
        service, _ = _make_service(raise_exception=err)
        with pytest.raises(BedrockAPIError):
            await service.generate_design_export(_input_full())

    @pytest.mark.asyncio
    async def test_ai_generation_failed_error_propagates(self):
        err = AIGenerationFailedError(
            message="재시도 초과",
            details={"last_error": {"type": "schema_validation_error", "attempt": 2}},
        )
        service, _ = _make_service(raise_exception=err)
        with pytest.raises(AIGenerationFailedError):
            await service.generate_design_export(_input_full())

    @pytest.mark.asyncio
    async def test_bedrock_error_not_rewrapped(self):
        original_err = BedrockAPIError(
            message="original",
            details={"error_type": "ClientError"},
        )
        service, _ = _make_service(raise_exception=original_err)
        with pytest.raises(BedrockAPIError) as exc_info:
            await service.generate_design_export(_input_full())
        assert exc_info.value is original_err


# ---------------------------------------------------------------------------
# _scan_banned 단독 검증
# ---------------------------------------------------------------------------


class TestScanBanned:
    def test_clean_texts_return_none(self):
        texts = ["질문을 인지한 상태인가?", "다음 단계는 무엇인가?", "핵심 목표가 무엇인가?"]
        assert _scan_banned(texts) is None

    @pytest.mark.parametrize(
        "banned_text",
        ["답한 질문", "검토한 질문", "사고가 정리된 상태", "결론을 내린 영역", "답했다", "답한 상태"],
    )
    def test_banned_text_detected(self, banned_text: str):
        texts = ["정상 텍스트.", f"이 부분에 {banned_text}이 포함됨.", "또 다른 텍스트."]
        result = _scan_banned(texts)
        assert result is not None
        violating_text, matched = result
        assert banned_text in violating_text
        assert matched in banned_text

    def test_returns_first_violation(self):
        texts = ["답한 질문 포함.", "검토한 질문도 포함."]
        result = _scan_banned(texts)
        assert result is not None
        assert "답한 질문" in result[1] or "검토한" in result[1]

    def test_empty_list_returns_none(self):
        assert _scan_banned([]) is None


# ---------------------------------------------------------------------------
# 프롬프트 파일 정적 검증 (design.md §7-1-1)
# ---------------------------------------------------------------------------


class TestPromptFileStaticValidation:
    """design_export.txt 내용을 직접 읽어 박제 항목을 검증한다."""

    @pytest.fixture(scope="class")
    def prompt_text(self) -> str:
        path = Path(__file__).parent.parent / "prompts" / "design_export.txt"
        return path.read_text(encoding="utf-8")

    def test_prompt_file_exists_and_nonempty(self, prompt_text: str):
        assert len(prompt_text) > 100

    def test_prompt_slots_present(self, prompt_text: str):
        assert "{project_context_block}" in prompt_text
        assert "{selected_required_steps_block}" in prompt_text

    def test_prompt_no_old_slots(self, prompt_text: str):
        # v1.0~v1.3 슬롯이 남아있지 않아야 함
        assert "{project_info_block}" not in prompt_text
        assert "{project_state_block}" not in prompt_text
        assert "{generated_at}" not in prompt_text

    def test_prompt_contains_json_output_format(self, prompt_text: str):
        # v1.4 Z+ 출력 키
        assert "questions_per_rs" in prompt_text
        assert "core_summary" in prompt_text

    def test_prompt_does_not_contain_rag_slot(self, prompt_text: str):
        assert "rag_context" not in prompt_text

    def test_prompt_contains_honesty_guard_table(self, prompt_text: str):
        assert "답한 질문" in prompt_text
        assert "검토한 질문" in prompt_text
        assert "사고가 정리된 상태" in prompt_text
        assert "결론을 내린 영역" in prompt_text

    def test_prompt_contains_transformation_instruction(self, prompt_text: str):
        # 사이드패널 멘토링 → What·Why 질문 변환 지시 (Req 8.3)
        assert "recommended_methods" in prompt_text
        assert "사용자 결정으로 오인" in prompt_text

    def test_prompt_contains_conversion_examples(self, prompt_text: str):
        # 변환 예시 5개 RS 커버
        assert "1-R2" in prompt_text
        assert "1-R3" in prompt_text
        assert "3-R3" in prompt_text
        assert "4-R1" in prompt_text
        assert "6-R1" in prompt_text

    def test_prompt_contains_questions_per_rs_structure(self, prompt_text: str):
        # required_step_id 매칭 키 언급
        assert "required_step_id" in prompt_text

    def test_prompt_prohibits_md_skeleton_output(self, prompt_text: str):
        # v1.4: 프롬프트가 AI에게 .md 골격 헤더 포함 금지를 지시함
        assert "포함하지 말 것" in prompt_text or "포함하지 않는다" in prompt_text


# ---------------------------------------------------------------------------
# Property-Based Tests (Hypothesis, design.md §5)
# ---------------------------------------------------------------------------

# -- Strategies --

_safe_text = st.text(
    alphabet=st.characters(
        whitelist_categories=("Lu", "Ll", "Nd", "Zs"),
        whitelist_characters=".,!?()[]가나다라마바사아자차카타파하",
    ),
    min_size=1,
    max_size=40,
).filter(lambda s: s.strip())

_recommended_method_st = st.builds(
    RecommendedMethod,
    title=_safe_text,
    content=_safe_text.map(lambda s: f"RMCONTENT_{s}"),
)

_common_mistake_st = st.builds(
    CommonMistake,
    mistake=_safe_text,
    bad_example=_safe_text.map(lambda s: f"BADEX_{s}"),
    good_example=_safe_text.map(lambda s: f"GOODEX_{s}"),
)

_mentoring_st = st.builds(
    MentoringContent,
    description=_safe_text,
    recommended_methods=st.lists(_recommended_method_st, min_size=0, max_size=3),
    common_mistakes=st.lists(_common_mistake_st, min_size=0, max_size=3),
    one_line_tip=_safe_text,
)

_accepted_step_st = st.builds(
    AcceptedStepForAI,
    name=_safe_text,
    description=_safe_text,
    sidepanel_mentoring=st.one_of(st.none(), _mentoring_st),
)


@st.composite
def _required_step_for_ai_st(draw: st.DrawFn) -> RequiredStepForAI:
    seq = draw(st.integers(min_value=1, max_value=6))
    ridx = draw(st.integers(min_value=1, max_value=4))
    uid = draw(st.uuids().map(lambda u: str(u)[:8]))
    return RequiredStepForAI(
        required_step_id=f"{seq}-R{ridx}-{uid}",
        required_step_name=draw(_safe_text),
        goal=draw(_safe_text),
        fulfillment_criteria=draw(st.lists(_safe_text, min_size=1, max_size=4)),
        accepted_general_steps=draw(st.lists(_accepted_step_st, min_size=0, max_size=3)),
    )


@st.composite
def design_export_input_strategy(draw: st.DrawFn) -> DesignExportInput:
    name = draw(st.one_of(st.none(), _safe_text))
    description = draw(st.one_of(st.none(), _safe_text))
    constraints = draw(
        st.one_of(
            st.none(),
            st.lists(_safe_text, min_size=0, max_size=3),
        )
    )
    project_context = ProjectContextForAI(
        name=name,
        description=description,
        duration_months=draw(st.integers(min_value=1, max_value=12)),
        member_count=draw(st.integers(min_value=1, max_value=20)),
        constraints=constraints,
        initial_prompt=draw(_safe_text),
    )
    selected_required_steps = draw(
        st.lists(_required_step_for_ai_st(), min_size=1, max_size=3)
    )
    return DesignExportInput(
        project_context=project_context,
        selected_required_steps=selected_required_steps,
    )


# -- PBT Mock --


def _generate_deterministic_output(input_data: DesignExportInput) -> DesignExportOutput:
    """DesignExportInput → 유효한 DesignExportOutput (결정론적, 정직성 가드 통과)."""
    questions_per_rs: list[RSQuestions] = []
    for rs in input_data.selected_required_steps:
        questions: list[str] = [
            f"{rs.required_step_name}의 핵심 목표는 무엇인가?",
            f"충족 기준 중 어떤 측면이 가장 중요한가?",
            f"이 단계에서 어떤 방향을 선택할 것인가?",
        ]
        for step in rs.accepted_general_steps[:3]:
            questions.append(f"{step.name}을(를) 통해 무엇을 파악하고자 했는가?")
        questions = questions[:6]
        questions_per_rs.append(
            RSQuestions(required_step_id=rs.required_step_id, questions=questions)
        )
    return DesignExportOutput(
        questions_per_rs=questions_per_rs,
        core_summary=[
            "핵심 목표를 중심으로 사고를 진행했는가?",
            "각 단계에서 무엇을 인지하고자 했는가?",
            "전체 흐름에서 어떤 방향을 선택했는가?",
        ],
    )


class _PBTMockLLM:
    """PBT 전용 LLM 대역 — 입력 기반 결정론적 출력 + 프롬프트 기록."""

    def __init__(self, input_data: DesignExportInput) -> None:
        self._output = _generate_deterministic_output(input_data)
        self.last_prompt: Optional[str] = None

    async def invoke(
        self,
        prompt: str,
        expected_schema: Any,
        max_retries: int = 2,
        max_tokens: Optional[int] = None,
    ) -> DesignExportOutput:
        self.last_prompt = prompt
        return self._output

    async def invoke_stream(self, *args: Any, **kwargs: Any) -> None:
        raise AssertionError("invoke_stream should not be called")


# -- Property Tests --


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(input_data=design_export_input_strategy())
def test_pbt_questions_per_rs_length_matches_input(input_data: DesignExportInput):
    """Property 1: questions_per_rs 길이가 selected_required_steps 길이와 동일하다."""
    llm = _PBTMockLLM(input_data)
    service = DesignExportGenerator(llm=llm)
    result = asyncio.run(service.generate_design_export(input_data))
    assert len(result.questions_per_rs) == len(input_data.selected_required_steps)


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(input_data=design_export_input_strategy())
def test_pbt_questions_per_rs_ids_match_input_order(input_data: DesignExportInput):
    """Property 2: questions_per_rs의 required_step_id가 입력 순서와 동일하다."""
    llm = _PBTMockLLM(input_data)
    service = DesignExportGenerator(llm=llm)
    result = asyncio.run(service.generate_design_export(input_data))
    expected = [rs.required_step_id for rs in input_data.selected_required_steps]
    actual = [rs_q.required_step_id for rs_q in result.questions_per_rs]
    assert actual == expected


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(input_data=design_export_input_strategy())
def test_pbt_questions_count_within_bounds(input_data: DesignExportInput):
    """Property 3: 각 RS의 질문 수가 3~6개 범위 안에 있다."""
    llm = _PBTMockLLM(input_data)
    service = DesignExportGenerator(llm=llm)
    result = asyncio.run(service.generate_design_export(input_data))
    for rs_q in result.questions_per_rs:
        assert 3 <= len(rs_q.questions) <= 6, (
            f"{rs_q.required_step_id} 질문 수 범위 초과: {len(rs_q.questions)}"
        )


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(input_data=design_export_input_strategy())
def test_pbt_core_summary_count_within_bounds(input_data: DesignExportInput):
    """Property 4: core_summary 항목 수가 3~6개 범위 안에 있다."""
    llm = _PBTMockLLM(input_data)
    service = DesignExportGenerator(llm=llm)
    result = asyncio.run(service.generate_design_export(input_data))
    assert 3 <= len(result.core_summary) <= 6


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(input_data=design_export_input_strategy())
def test_pbt_banned_expressions_not_in_output(input_data: DesignExportInput):
    """Property 5: 출력 질문·핵심 정리에 금지 표현이 등장하지 않는다."""
    llm = _PBTMockLLM(input_data)
    service = DesignExportGenerator(llm=llm)
    result = asyncio.run(service.generate_design_export(input_data))
    all_texts = [q for rs_q in result.questions_per_rs for q in rs_q.questions]
    all_texts.extend(result.core_summary)
    for pattern in _BANNED_PATTERNS:
        for text in all_texts:
            match = pattern.search(text)
            assert match is None, f"금지 패턴 감지: {pattern.pattern!r} → {text!r}"


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(input_data=design_export_input_strategy())
def test_pbt_empty_accepted_steps_rs_generates_min_questions(input_data: DesignExportInput):
    """Property 6: accepted_general_steps가 빈 RS도 최소 3개 질문을 생성한다."""
    llm = _PBTMockLLM(input_data)
    service = DesignExportGenerator(llm=llm)
    result = asyncio.run(service.generate_design_export(input_data))
    for i, rs in enumerate(input_data.selected_required_steps):
        if not rs.accepted_general_steps:
            assert len(result.questions_per_rs[i].questions) >= 3, (
                f"빈 RS {rs.required_step_id} 질문 수 부족: {len(result.questions_per_rs[i].questions)}"
            )


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(input_data=design_export_input_strategy())
def test_pbt_project_context_fields_in_prompt(input_data: DesignExportInput):
    """Property 7: 프롬프트에 project_context 핵심 필드(member_count, initial_prompt)가 포함된다."""
    llm = _PBTMockLLM(input_data)
    service = DesignExportGenerator(llm=llm)
    asyncio.run(service.generate_design_export(input_data))
    assert llm.last_prompt is not None
    assert str(input_data.project_context.member_count) in llm.last_prompt
    assert input_data.project_context.initial_prompt in llm.last_prompt
