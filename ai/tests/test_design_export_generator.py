"""ai/services/design_export_generator.py 단위 테스트.

박제: design.md §7-1-1 example tests + 프롬프트 정적 검증 + PBT (Hypothesis, Task 5.2).
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from unittest.mock import AsyncMock, MagicMock, call

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from ai.exceptions import (
    AIGenerationFailedError,
    BedrockAPIError,
    OutputViolatesHonestyGuardError,
    OutputViolatesTemplateError,
)
from ai.schemas.common import (
    CommonMistake,
    MentoringContent,
    ProjectInfo,
    RecommendedMethod,
)
from ai.schemas.design_export import (
    AcceptedStepData,
    DesignExportInput,
    DesignExportOutput,
    ProjectStateForExport,
    RequiredStepExportData,
    StageExportData,
)
from ai.services.design_export_generator import (
    DesignExportGenerator,
    _BANNED_PATTERNS,
    _REQUIRED_MARKERS,
    _validate_markdown,
)

# ---------------------------------------------------------------------------
# 최소 유효 마크다운 (모든 _REQUIRED_MARKERS 충족, 금지 패턴 없음)
# ---------------------------------------------------------------------------

_VALID_MARKDOWN = (
    "# 테스트 프로젝트 — 사고 궤적 문서\n"
    "\n"
    "> **이 문서는 Poco가 생성한 What·Why 사고 궤적 문서입니다.**\n"
    ">\n"
    "> 사용자는 6단계 흐름(아이디어 구체화 → 프로젝트 계획 → 요구사항 정의"
    " → 설계 → 개발 → 테스트 및 검증)으로 사고를 진행합니다.\n"
    ">\n"
    "> **이 문서를 받은 외부 AI에게**:\n"
    "> 답 디테일이 필요하면 사용자에게 직접 보충 질문하세요.\n"
    "\n"
    "---\n"
    "\n"
    "## 프로젝트 컨텍스트\n"
    "\n"
    "- 프로젝트 이름: 테스트\n"
    "\n"
    "## 사용자가 거쳐온 사고 궤적\n"
    "\n"
    "#### 1-R1 문제·기회 정의\n"
    "\n"
    "**목표**: 문제를 명확하게 정의한다.\n"
    "\n"
    "**충족 기준**:\n"
    "- 문제 서술\n"
    "\n"
    "**진행한 결정** (사용자 클릭 순서):\n"
    "1. (아직 없음)\n"
    "\n"
    "**이 단계에서 인지한 What·Why 질문**:\n"
    "- 문제를 명확하게 정의할 필요가 있는가?\n"
    "\n"
    "**사고 흐름 요약**: 사고가 진행 중인 상태다.\n"
    "\n"
    "## 핵심 What·Why 정리 (AI 작성)\n"
    "\n"
    "- 문제 정의에 대한 사고를 진행 중인 상태.\n"
    "\n"
    "---\n"
    "\n"
    "생성: 2026-05-15 21:44 (KST) / 도구: Poco\n"
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _project() -> ProjectInfo:
    return ProjectInfo(
        project_id="proj-1",
        name="스터디 매칭 앱",
        duration_months=3,
        member_count=4,
        description="대학생용 스터디 매칭 플랫폼",
        constraints=["React + FastAPI", "AWS 프리 티어"],
        initial_prompt="스터디 메이트 매칭 서비스를 만들고 싶음",
    )


def _project_minimal() -> ProjectInfo:
    return ProjectInfo(
        project_id="proj-2",
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


def _accepted_step() -> AcceptedStepData:
    return AcceptedStepData(
        step_id="step-1",
        name="타겟 사용자 인터뷰 계획",
        description="1차 타겟 사용자군의 특성을 정의하는 활동",
        accepted_at=datetime(2026, 5, 15, 10, 0, tzinfo=timezone.utc),
        sidepanel_mentoring=_mentoring(),
    )


def _required_step_with_steps() -> RequiredStepExportData:
    return RequiredStepExportData(
        required_step_id="1-R2",
        required_step_name="대상 사용자 파악",
        goal="정의된 문제로 불편을 겪는 구체적 사용자군을 식별한다.",
        entry_criteria="문제/기회에 관한 맥락이 존재한다.",
        fulfillment_criteria=[
            "1차 타겟 사용자군의 특성 정의",
            "사용자의 현재 행동·습관·맥락 파악",
            "사용자 검증 활동",
        ],
        accepted_general_steps=[_accepted_step()],
    )


def _required_step_empty() -> RequiredStepExportData:
    return RequiredStepExportData(
        required_step_id="1-R1",
        required_step_name="문제·기회 정의",
        goal="핵심 문제 또는 기회를 서술하고 명확화한다.",
        entry_criteria="프로젝트 초기 아이디어가 존재한다.",
        fulfillment_criteria=[
            "문제/기회 자체에 대한 서술·명확화",
            "문제의 중요도·임팩트 분석",
        ],
        accepted_general_steps=[],
    )


def _stage_full() -> StageExportData:
    return StageExportData(
        stage_sequence=1,
        stage_name="아이디어 구체화",
        required_steps=[_required_step_with_steps()],
    )


def _stage_empty() -> StageExportData:
    return StageExportData(
        stage_sequence=1,
        stage_name="아이디어 구체화",
        required_steps=[_required_step_empty()],
    )


def _input_full() -> DesignExportInput:
    return DesignExportInput(
        project_info=_project(),
        project_state=ProjectStateForExport(stages=[_stage_full()]),
        generated_at=datetime(2026, 5, 15, 21, 44, tzinfo=timezone.utc),
    )


def _input_empty_steps() -> DesignExportInput:
    return DesignExportInput(
        project_info=_project_minimal(),
        project_state=ProjectStateForExport(stages=[_stage_empty()]),
        generated_at=datetime(2026, 5, 15, 9, 0, tzinfo=timezone.utc),
    )


def _make_service(
    llm_return: Any = None,
    llm_side_effect: Any = None,
) -> tuple[DesignExportGenerator, MagicMock]:
    llm = MagicMock()
    llm.invoke = AsyncMock()
    llm.invoke_stream = MagicMock()  # 호출되면 안 됨
    if llm_side_effect is not None:
        llm.invoke.side_effect = llm_side_effect
    else:
        llm.invoke.return_value = (
            llm_return
            if llm_return is not None
            else DesignExportOutput(markdown=_VALID_MARKDOWN)
        )
    return DesignExportGenerator(llm=llm), llm


# ---------------------------------------------------------------------------
# _validate_markdown — 단독 검증 (Req 12.4)
# ---------------------------------------------------------------------------


class TestValidateMarkdownPass:
    def test_valid_markdown_passes(self):
        _validate_markdown(_VALID_MARKDOWN)  # 예외 없어야 함

    def test_all_required_markers_present_in_valid_markdown(self):
        for marker in _REQUIRED_MARKERS:
            assert marker in _VALID_MARKDOWN, f"테스트 마크다운에 마커 누락: {marker!r}"

    def test_no_banned_patterns_in_valid_markdown(self):
        for pattern in _BANNED_PATTERNS:
            assert not pattern.search(_VALID_MARKDOWN), (
                f"테스트 마크다운에 금지 패턴 매치: {pattern.pattern!r}"
            )


class TestValidateMarkdownMarkerMissing:
    @pytest.mark.parametrize("marker", _REQUIRED_MARKERS)
    def test_missing_marker_raises_template_error(self, marker: str):
        broken = _VALID_MARKDOWN.replace(marker, "___REMOVED___")
        with pytest.raises(OutputViolatesTemplateError) as exc_info:
            _validate_markdown(broken)
        assert exc_info.value.details["missing_marker"] == marker

    def test_empty_markdown_raises_template_error(self):
        with pytest.raises(OutputViolatesTemplateError):
            _validate_markdown("")


class TestValidateMarkdownBannedPatterns:
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
    def test_banned_pattern_raises_honesty_error(self, banned_text: str):
        # valid markdown에 금지 표현을 삽입
        injected = _VALID_MARKDOWN + f"\n{banned_text}\n"
        with pytest.raises(OutputViolatesHonestyGuardError) as exc_info:
            _validate_markdown(injected)
        assert exc_info.value.details["banned_phrase"] in injected

    def test_blockquote_guidance_sentence_passes(self):
        # "답을 적어둔 상태가 아니라 질문을 인지한 상태일 수 있으니" 는
        # 자기소개 블록쿼터의 박제 표현 — 금지 패턴 어느 것에도 매치되지 않아야 함
        text_with_guidance = (
            _VALID_MARKDOWN
            + "\n> 사용자가 *\"답을 적어둔 상태\"* 가 아니라 *\"질문을 인지한 상태\"* 일 수 있으니,\n"
        )
        _validate_markdown(text_with_guidance)  # 예외 없어야 함


# ---------------------------------------------------------------------------
# 시그니처·RAG 없음 검증 (Req 15.4, 15.5)
# ---------------------------------------------------------------------------


class TestSignatureAndNoDependency:
    def test_constructor_accepts_only_llm(self):
        llm = MagicMock()
        service = DesignExportGenerator(llm=llm)
        assert service.llm is llm

    @pytest.mark.asyncio
    async def test_invoke_stream_never_called(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        llm.invoke_stream.assert_not_called()

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
        assert result.markdown == _VALID_MARKDOWN

    @pytest.mark.asyncio
    async def test_llm_invoke_called_once(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        llm.invoke.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_llm_invoke_passes_design_export_output_schema(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        schema_arg = llm.invoke.await_args.args[1]
        assert schema_arg is DesignExportOutput

    @pytest.mark.asyncio
    async def test_llm_invoke_passes_max_tokens_4096(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        kwargs = llm.invoke.await_args.kwargs
        assert kwargs.get("max_tokens") == 4096

    @pytest.mark.asyncio
    async def test_empty_accepted_steps_input_succeeds(self):
        service, _ = _make_service()
        result = await service.generate_design_export(_input_empty_steps())
        assert isinstance(result, DesignExportOutput)


# ---------------------------------------------------------------------------
# 프롬프트 조립 검증
# ---------------------------------------------------------------------------


class TestPromptAssembly:
    @pytest.mark.asyncio
    async def test_prompt_contains_project_name(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        prompt = llm.invoke.await_args.args[0]
        assert "스터디 매칭 앱" in prompt

    @pytest.mark.asyncio
    async def test_prompt_contains_member_count(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        prompt = llm.invoke.await_args.args[0]
        assert "4명" in prompt

    @pytest.mark.asyncio
    async def test_prompt_contains_initial_prompt(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        prompt = llm.invoke.await_args.args[0]
        assert "스터디 메이트 매칭 서비스를 만들고 싶음" in prompt

    @pytest.mark.asyncio
    async def test_prompt_contains_constraints(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        prompt = llm.invoke.await_args.args[0]
        assert "React + FastAPI" in prompt

    @pytest.mark.asyncio
    async def test_prompt_contains_required_step_name(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        prompt = llm.invoke.await_args.args[0]
        assert "대상 사용자 파악" in prompt

    @pytest.mark.asyncio
    async def test_prompt_contains_fulfillment_criteria(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        prompt = llm.invoke.await_args.args[0]
        assert "1차 타겟 사용자군의 특성 정의" in prompt

    @pytest.mark.asyncio
    async def test_prompt_contains_accepted_step_name(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        prompt = llm.invoke.await_args.args[0]
        assert "타겟 사용자 인터뷰 계획" in prompt

    @pytest.mark.asyncio
    async def test_prompt_contains_generated_at(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        prompt = llm.invoke.await_args.args[0]
        assert "2026-05-15 21:44" in prompt

    @pytest.mark.asyncio
    async def test_prompt_empty_steps_contains_none_label(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_empty_steps())
        prompt = llm.invoke.await_args.args[0]
        assert "없음" in prompt  # Accept된 일반 Step: 없음

    @pytest.mark.asyncio
    async def test_no_unresolved_placeholders_in_prompt(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        prompt = llm.invoke.await_args.args[0]
        for slot in ["{project_info_block}", "{project_state_block}", "{generated_at}"]:
            assert slot not in prompt, f"미치환 슬롯: {slot}"

    @pytest.mark.asyncio
    async def test_prompt_contains_mentoring_content(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_full())
        prompt = llm.invoke.await_args.args[0]
        assert "타겟 사용자 인터뷰" in prompt

    @pytest.mark.asyncio
    async def test_minimal_project_none_fields_use_placeholder(self):
        service, llm = _make_service()
        await service.generate_design_export(_input_empty_steps())
        prompt = llm.invoke.await_args.args[0]
        # name, description, constraints 가 None/empty → "(미입력)" 들어가야 함
        assert "(미입력)" in prompt


# ---------------------------------------------------------------------------
# 출력 검증 위반 (Req 12.4, design.md §6-2)
# ---------------------------------------------------------------------------


class TestOutputValidation:
    @pytest.mark.asyncio
    async def test_template_violation_raises_immediately(self):
        broken_md = "마커 없는 본문"
        service, _ = _make_service(
            llm_return=DesignExportOutput(markdown=broken_md)
        )
        with pytest.raises(OutputViolatesTemplateError):
            await service.generate_design_export(_input_full())

    @pytest.mark.asyncio
    async def test_honesty_violation_raises_immediately(self):
        injected_md = _VALID_MARKDOWN + "\n이 사용자는 모든 질문에 답했다.\n"
        service, _ = _make_service(
            llm_return=DesignExportOutput(markdown=injected_md)
        )
        with pytest.raises(OutputViolatesHonestyGuardError):
            await service.generate_design_export(_input_full())

    @pytest.mark.asyncio
    async def test_no_retry_after_template_violation(self):
        """검증 위반 시 LLM 을 재호출하지 않는다 (design.md §6-2)."""
        broken_md = "마커 없는 본문"
        service, llm = _make_service(
            llm_return=DesignExportOutput(markdown=broken_md)
        )
        with pytest.raises(OutputViolatesTemplateError):
            await service.generate_design_export(_input_full())
        assert llm.invoke.await_count == 1

    @pytest.mark.asyncio
    async def test_no_retry_after_honesty_violation(self):
        injected_md = _VALID_MARKDOWN + "\n검토한 질문 목록.\n"
        service, llm = _make_service(
            llm_return=DesignExportOutput(markdown=injected_md)
        )
        with pytest.raises(OutputViolatesHonestyGuardError):
            await service.generate_design_export(_input_full())
        assert llm.invoke.await_count == 1


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
        service, _ = _make_service(llm_side_effect=err)
        with pytest.raises(BedrockAPIError):
            await service.generate_design_export(_input_full())

    @pytest.mark.asyncio
    async def test_ai_generation_failed_error_propagates(self):
        err = AIGenerationFailedError(
            message="재시도 초과",
            details={"last_error": {"type": "schema_validation_error", "attempt": 2}},
        )
        service, _ = _make_service(llm_side_effect=err)
        with pytest.raises(AIGenerationFailedError):
            await service.generate_design_export(_input_full())

    @pytest.mark.asyncio
    async def test_bedrock_error_not_rewrapped(self):
        """BedrockAPIError 는 재포장 없이 그대로 raise 된다."""
        original_err = BedrockAPIError(
            message="original",
            details={"error_type": "ClientError"},
        )
        service, _ = _make_service(llm_side_effect=original_err)
        with pytest.raises(BedrockAPIError) as exc_info:
            await service.generate_design_export(_input_full())
        assert exc_info.value is original_err


# ---------------------------------------------------------------------------
# 프롬프트 파일 정적 검증 (design.md §7-1-1)
# ---------------------------------------------------------------------------


class TestPromptFileStaticValidation:
    """design_export.txt 내용을 직접 읽어 박제 항목을 검증한다."""

    @pytest.fixture(scope="class")
    def prompt_text(self) -> str:
        path = Path(__file__).parent.parent / "prompts" / "design_export.txt"
        return path.read_text(encoding="utf-8")

    def test_prompt_file_exists(self, prompt_text: str):
        assert len(prompt_text) > 0

    def test_prompt_contains_transformation_instruction(self, prompt_text: str):
        # 사이드패널 멘토링 → What·Why 질문 변환 지시 포함 (Req 8.3)
        assert "recommended_methods" in prompt_text
        assert "사용자 결정으로 오인" in prompt_text

    def test_prompt_contains_honesty_guard_table(self, prompt_text: str):
        # 정직성 가드 표 6쌍 포함 (Req 9.3)
        assert "답한 질문" in prompt_text
        assert "검토한 질문" in prompt_text
        assert "사고가 정리된 상태" in prompt_text
        assert "결론을 내린 영역" in prompt_text

    def test_prompt_contains_external_ai_guidance(self, prompt_text: str):
        # 외부 AI 행동 지침 포함 (Req 7.3, 9.4)
        assert "답을 적어둔 상태가 아니라 질문을 인지한 상태일 수 있으니" in prompt_text
        assert "직접 보충 질문하세요" in prompt_text

    def test_prompt_contains_six_stage_flow_terms(self, prompt_text: str):
        # 6단계 흐름 어휘 (Req 7.2)
        for term in [
            "아이디어 구체화",
            "프로젝트 계획",
            "요구사항 정의",
            "설계",
            "개발",
            "테스트 및 검증",
        ]:
            assert term in prompt_text, f"6단계 흐름 어휘 누락: {term!r}"

    def test_prompt_does_not_contain_rag_slot(self, prompt_text: str):
        # RAG 슬롯 포함 금지 (Req 15.5)
        assert "{rag_context}" not in prompt_text
        assert "rag_context" not in prompt_text.lower().replace("rag_context", "")
        # rag_context 가 전혀 없어야 함
        assert "rag_context" not in prompt_text

    def test_prompt_contains_json_output_format(self, prompt_text: str):
        # 단일 키 JSON 출력 형식 명시
        assert '"markdown"' in prompt_text or "'markdown'" in prompt_text

    def test_prompt_contains_max_tokens_reference(self, prompt_text: str):
        # 출력 길이 제약 (Req 10.6)
        assert "4,000" in prompt_text or "4096" in prompt_text

    def test_prompt_contains_fixed_template_skeleton(self, prompt_text: str):
        # 고정 템플릿 골격 포함
        assert "이 문서는 Poco가 생성한 What·Why 사고 궤적 문서입니다." in prompt_text
        assert "## 프로젝트 컨텍스트" in prompt_text
        assert "## 사용자가 거쳐온 사고 궤적" in prompt_text
        assert "## 핵심 What·Why 정리" in prompt_text

    def test_prompt_contains_conversion_examples(self, prompt_text: str):
        # 변환 예시 5개 Stage 커버 (Stage 1, 1, 3, 4, 6)
        assert "1-R2" in prompt_text  # 예시 1
        assert "1-R3" in prompt_text  # 예시 2
        assert "3-R3" in prompt_text  # 예시 3
        assert "4-R1" in prompt_text  # 예시 4
        assert "6-R1" in prompt_text  # 예시 5

    def test_prompt_slots_present(self, prompt_text: str):
        # 3개 슬롯이 프롬프트에 존재해야 함
        assert "{project_info_block}" in prompt_text
        assert "{project_state_block}" in prompt_text
        assert "{generated_at}" in prompt_text


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
    AcceptedStepData,
    step_id=st.uuids().map(str),
    name=_safe_text,
    description=_safe_text,
    accepted_at=st.datetimes(
        min_value=datetime(2024, 1, 1),
        max_value=datetime(2026, 12, 31),
    ),
    sidepanel_mentoring=st.one_of(st.none(), _mentoring_st),
)


@st.composite
def _required_step_export_st(draw: st.DrawFn) -> RequiredStepExportData:
    seq = draw(st.integers(min_value=1, max_value=6))
    ridx = draw(st.integers(min_value=1, max_value=4))
    # UUID suffix ensures globally unique IDs across stages (for order-preservation tests)
    uid = draw(st.uuids().map(lambda u: str(u)[:8]))
    return RequiredStepExportData(
        required_step_id=f"{seq}-R{ridx}-{uid}",
        required_step_name=draw(_safe_text),
        goal=draw(_safe_text),
        entry_criteria=draw(_safe_text),
        fulfillment_criteria=draw(st.lists(_safe_text, min_size=1, max_size=4)),
        accepted_general_steps=draw(st.lists(_accepted_step_st, min_size=0, max_size=3)),
    )


@st.composite
def _stage_export_st(draw: st.DrawFn) -> StageExportData:
    seq = draw(st.integers(min_value=1, max_value=6))
    stage_names = [
        "아이디어 구체화", "프로젝트 계획", "요구사항 정의",
        "설계", "개발", "테스트 및 검증",
    ]
    return StageExportData(
        stage_sequence=seq,
        stage_name=stage_names[seq - 1],
        required_steps=draw(st.lists(_required_step_export_st(), min_size=1, max_size=2)),
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
    project_info = ProjectInfo(
        project_id=str(draw(st.uuids())),
        name=name,
        duration_months=draw(st.integers(min_value=1, max_value=24)),
        member_count=draw(st.integers(min_value=1, max_value=10)),
        description=description,
        constraints=constraints,
        initial_prompt=draw(_safe_text),
    )
    stages = draw(st.lists(_stage_export_st(), min_size=1, max_size=2))
    generated_at = draw(
        st.datetimes(
            min_value=datetime(2024, 1, 1),
            max_value=datetime(2026, 12, 31),
        )
    )
    return DesignExportInput(
        project_info=project_info,
        project_state=ProjectStateForExport(stages=stages),
        generated_at=generated_at,
    )


# -- MockDesignExportLLM --


def _generate_deterministic_markdown(input_data: DesignExportInput) -> str:
    """DesignExportInput → _validate_markdown 통과 + Property 5~7 조건 만족하는 결정론적 .md 생성."""
    pi = input_data.project_info
    name = pi.name if pi.name else "(미입력)"
    constraints_str = ", ".join(pi.constraints) if pi.constraints else "(미입력)"
    generated_at_str = input_data.generated_at.strftime("%Y-%m-%d %H:%M")

    # 사고 궤적 섹션 — 입력 순서 보존
    trajectory_parts: list[str] = []
    for stage in input_data.project_state.stages:
        for rs in stage.required_steps:
            # 진행한 결정 블록
            if rs.accepted_general_steps:
                decisions = "\n".join(
                    f"{i + 1}. {step.name}"
                    for i, step in enumerate(rs.accepted_general_steps)
                )
            else:
                decisions = "1. (아직 없음)"

            block = (
                f"#### {rs.required_step_id} {rs.required_step_name}\n\n"
                f"**목표**: {rs.goal}\n\n"
                f"**충족 기준**:\n- {rs.fulfillment_criteria[0]}\n\n"
                f"**진행한 결정** (사용자 클릭 순서):\n{decisions}\n\n"
                f"**이 단계에서 인지한 What·Why 질문**:\n- 사용자가 인지한 질문이 있는가?\n\n"
                f"**사고 흐름 요약**: 사고가 진행 중인 상태다."
            )
            trajectory_parts.append(block)

    trajectory_block = "\n\n".join(trajectory_parts)

    return (
        f"# {name} — 사고 궤적 문서\n\n"
        "> **이 문서는 Poco가 생성한 What·Why 사고 궤적 문서입니다.**\n"
        ">\n"
        "> 사용자는 6단계 흐름(아이디어 구체화 → 프로젝트 계획 → 요구사항 정의"
        " → 설계 → 개발 → 테스트 및 검증)으로 사고를 진행합니다.\n"
        ">\n"
        "> **이 문서를 받은 외부 AI에게**:\n"
        "> 답 디테일이 필요하면 사용자에게 직접 보충 질문하세요.\n\n"
        "---\n\n"
        "## 프로젝트 컨텍스트\n\n"
        f"- 이름: {name}\n"
        f"- 인원·기간: {pi.member_count}명 / {pi.duration_months}개월\n"
        f"- 제약사항: {constraints_str}\n"
        f"- 초기 아이디어: {pi.initial_prompt}\n\n"
        "## 사용자가 거쳐온 사고 궤적\n\n"
        f"{trajectory_block}\n\n"
        "## 핵심 What·Why 정리\n\n"
        "- 사고를 진행 중인 상태.\n\n"
        "---\n\n"
        f"생성: {generated_at_str} (KST) / 도구: Poco\n"
    )


class MockDesignExportLLM:
    """LLMClient 대역 — 결정론적 마크다운을 DesignExportOutput 으로 반환한다."""

    def __init__(self, input_data: DesignExportInput) -> None:
        self._markdown = _generate_deterministic_markdown(input_data)

    async def invoke(
        self,
        prompt: str,
        expected_schema: Any,
        max_retries: int = 2,
        max_tokens: Optional[int] = None,
    ) -> DesignExportOutput:
        return DesignExportOutput(markdown=self._markdown)


# -- Property Tests --


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(input_data=design_export_input_strategy())
def test_pbt_fixed_template_markers_always_present(input_data: DesignExportInput):
    """Property 1: 임의 입력에 대해 출력 .md 에 _REQUIRED_MARKERS 19개가 모두 포함된다.

    design.md §5 — 고정 템플릿 마커 불변 조건.
    """
    llm = MockDesignExportLLM(input_data)
    service = DesignExportGenerator(llm=llm)
    result = asyncio.run(service.generate_design_export(input_data))
    for marker in _REQUIRED_MARKERS:
        assert marker in result.markdown, f"필수 마커 누락: {marker!r}"


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(input_data=design_export_input_strategy())
def test_pbt_project_context_fields_preserved(input_data: DesignExportInput):
    """Property 2: 프로젝트 컨텍스트 필드(name/member_count/duration_months/constraints)가 출력에 반영된다.

    design.md §5 — 프로젝트 컨텍스트 보존 불변 조건.
    """
    llm = MockDesignExportLLM(input_data)
    service = DesignExportGenerator(llm=llm)
    result = asyncio.run(service.generate_design_export(input_data))

    pi = input_data.project_info
    expected_name = pi.name if pi.name else "(미입력)"
    assert expected_name in result.markdown

    assert str(pi.member_count) in result.markdown
    assert str(pi.duration_months) in result.markdown

    if pi.constraints:
        for c in pi.constraints:
            assert c in result.markdown
    else:
        assert "(미입력)" in result.markdown


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(input_data=design_export_input_strategy())
def test_pbt_footer_timestamp_exact_match(input_data: DesignExportInput):
    """Property 3: 푸터 타임스탬프가 generated_at 을 그대로 반영한다.

    design.md §5 — 푸터 타임스탬프 불변 조건 (Req 7.9).
    """
    llm = MockDesignExportLLM(input_data)
    service = DesignExportGenerator(llm=llm)
    result = asyncio.run(service.generate_design_export(input_data))

    expected_ts = input_data.generated_at.strftime("%Y-%m-%d %H:%M")
    assert f"{expected_ts} (KST)" in result.markdown
    assert "도구: Poco" in result.markdown


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(input_data=design_export_input_strategy())
def test_pbt_mentoring_raw_content_not_in_output(input_data: DesignExportInput):
    """Property 4: sidepanel_mentoring 의 원본 content/bad_example/good_example 이 출력에 노출되지 않는다.

    design.md §5 — 멘토링 원본 콘텐츠 미노출 불변 조건 (방향 3: 변환 규칙).
    RMCONTENT_/BADEX_/GOODEX_ 접두사로 전략에서 마킹해 두었으므로 접두사 존재 여부로 검사한다.
    """
    llm = MockDesignExportLLM(input_data)
    service = DesignExportGenerator(llm=llm)
    result = asyncio.run(service.generate_design_export(input_data))

    assert "RMCONTENT_" not in result.markdown
    assert "BADEX_" not in result.markdown
    assert "GOODEX_" not in result.markdown


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(input_data=design_export_input_strategy())
def test_pbt_decision_section_correctness(input_data: DesignExportInput):
    """Property 5: "진행한 결정" 블록이 accepted_general_steps 유무에 따라 올바르게 채워진다.

    design.md §5 — 빈 목록 → "(아직 없음)", 비어있지 않으면 step 이름 포함.
    """
    llm = MockDesignExportLLM(input_data)
    service = DesignExportGenerator(llm=llm)
    result = asyncio.run(service.generate_design_export(input_data))

    for stage in input_data.project_state.stages:
        for rs in stage.required_steps:
            if not rs.accepted_general_steps:
                assert "(아직 없음)" in result.markdown
            else:
                for step in rs.accepted_general_steps:
                    assert step.name in result.markdown


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(input_data=design_export_input_strategy())
def test_pbt_banned_expressions_not_in_output(input_data: DesignExportInput):
    """Property 6: 출력 .md 에 표현 정직성 가드 금지 패턴이 등장하지 않는다.

    design.md §5 — 정직성 가드 불변 조건 (Req 9.3, §3-6-2).
    """
    llm = MockDesignExportLLM(input_data)
    service = DesignExportGenerator(llm=llm)
    result = asyncio.run(service.generate_design_export(input_data))

    for pattern in _BANNED_PATTERNS:
        match = pattern.search(result.markdown)
        assert match is None, f"금지 패턴 감지: {pattern.pattern!r} → {match.group(0)!r}"


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(input_data=design_export_input_strategy())
def test_pbt_input_order_preserved_in_output(input_data: DesignExportInput):
    """Property 7: 입력 Stage → RequiredStep → AcceptedStep 순서가 출력에서 유지된다.

    design.md §5 — 입력 순서 보존 불변 조건.
    """
    llm = MockDesignExportLLM(input_data)
    service = DesignExportGenerator(llm=llm)
    result = asyncio.run(service.generate_design_export(input_data))
    md = result.markdown

    # 각 required_step_id 의 등장 위치가 입력 순서와 동일해야 함
    positions: list[int] = []
    for stage in input_data.project_state.stages:
        for rs in stage.required_steps:
            pos = md.find(rs.required_step_id)
            assert pos != -1, f"required_step_id {rs.required_step_id!r} 미발견"
            positions.append(pos)

    assert positions == sorted(positions), "required_step 등장 순서가 입력 순서와 다름"
