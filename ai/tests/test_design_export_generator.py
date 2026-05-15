"""ai/services/design_export_generator.py 단위 테스트.

박제: design.md §7-1-1 example tests + 프롬프트 정적 검증.
Property-based tests는 Task 5.2* 별도 파일(test_design_export_generator_property.py)에서 처리.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, call

import pytest

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
