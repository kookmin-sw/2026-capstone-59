"""터미널 기반 AI 시나리오 수동 테스트 시뮬레이터.

실행: ``python -m ai.cli_simulator``

실제 Anthropic Direct API + Bedrock KB(RAG)를 호출하여
generate → accept → side_panel 흐름, 또는 design-export 시나리오를 모사한다.
인메모리 상태만 유지하며 DB는 사용하지 않는다.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import time
import uuid
from typing import Optional

import boto3
from anthropic import AsyncAnthropic

from ai.clients.llm import LLMClient
from ai.clients.rag import RAGClient
from ai.config import ai_settings
from ai.exceptions import (
    AIGenerationFailedError,
    BedrockAPIError,
    OutputViolatesHonestyGuardError,
)
from ai.fixtures.required_steps import stage_1_required_steps
from ai.schemas.accept import AcceptInput
from ai.schemas.common import (
    CommonMistake,
    DecisionHistoryItem,
    MentoringContent,
    ProjectInfo,
    RecommendedMethod,
    RequiredStepInfo,
    RequiredStepStatus,
    StageInfo,
    StepInfo,
)
from ai.schemas.design_export import (
    AcceptedStepForAI,
    DesignExportInput,
    DesignExportOutput,
    ProjectContextForAI,
    RequiredStepForAI,
)
from ai.schemas.generate import GenerateInput, GenerateOutput
from ai.schemas.side_panel import SidePanelInput, SidePanelOutput
from ai.services import generate_design_export
from ai.services.required_step_judge import RequiredStepJudge
from ai.services.side_panel_generator import SidePanelGenerator
from ai.services.step_generator import StepGenerator

_STAGE = StageInfo(stage_id="stage-1", stage_sequence=1, name="아이디어 구체화")


# ---------------------------------------------------------------------------
# 출력 헬퍼
# ---------------------------------------------------------------------------


def _hr(char: str = "─", width: int = 60) -> None:
    print(char * width)


def _section(title: str) -> None:
    print()
    _hr("═")
    print(f"  {title}")
    _hr("═")


def _info(msg: str) -> None:
    print(f"ℹ️  {msg}")


def _ok(msg: str) -> None:
    print(f"✅ {msg}")


def _wait(msg: str) -> None:
    print(f"⏳ {msg}")


def _fail(msg: str) -> None:
    print(f"❌ {msg}")


# ---------------------------------------------------------------------------
# 입력 헬퍼
# ---------------------------------------------------------------------------


def _input_required(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        _fail("필수 항목입니다. 다시 입력해주세요.")


def _input_optional(prompt: str) -> Optional[str]:
    value = input(prompt).strip()
    return value or None


def _input_int(prompt: str, minimum: int = 1) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
            if value < minimum:
                _fail(f"{minimum} 이상의 정수를 입력해주세요.")
                continue
            return value
        except ValueError:
            _fail("정수를 입력해주세요.")


def _input_choice(prompt: str, valid: range) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
            if value in valid:
                return value
            _fail(f"{valid.start}~{valid.stop - 1} 중에서 선택해주세요.")
        except ValueError:
            _fail("번호를 입력해주세요.")


def _input_yes_no(prompt: str) -> bool:
    while True:
        raw = input(prompt).strip().lower()
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no", ""):
            return False
        _fail("y 또는 n으로 답해주세요.")


# ---------------------------------------------------------------------------
# 초기화
# ---------------------------------------------------------------------------


def _build_project_info() -> ProjectInfo:
    _section("프로젝트 초기 정보 입력")
    initial_prompt = _input_required("아이디어를 입력하세요: ")
    duration_months = _input_int("프로젝트 기간 (개월): ", minimum=1)
    member_count = _input_int("프로젝트 인원 (명): ", minimum=1)
    name = _input_optional("프로젝트 이름 (선택, 엔터=스킵): ")
    description = _input_optional("프로젝트 설명 (선택, 엔터=스킵): ")
    _constraints_raw = _input_optional("제약사항 (선택, 콤마 구분 또는 엔터=스킵): ")
    constraints = (
        [c.strip() for c in _constraints_raw.split(",") if c.strip()]
        if _constraints_raw
        else None
    )

    return ProjectInfo(
        project_id=str(uuid.uuid4()),
        name=name,
        duration_months=duration_months,
        member_count=member_count,
        description=description,
        constraints=constraints,
        initial_prompt=initial_prompt,
    )


def _build_anthropic_client() -> AsyncAnthropic:
    """Anthropic Direct API용 AsyncAnthropic 클라이언트 생성.

    환경변수 ANTHROPIC_API_KEY 우선, 없으면 ai_settings에서 fallback.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY") or ai_settings.ANTHROPIC_API_KEY
    return AsyncAnthropic(api_key=api_key)


def _build_services() -> tuple[StepGenerator, RequiredStepJudge, SidePanelGenerator]:
    anthropic_client = _build_anthropic_client()
    bedrock_agent_runtime = boto3.client(
        "bedrock-agent-runtime", region_name=ai_settings.AWS_REGION
    )

    llm = LLMClient(
        anthropic_client=anthropic_client,
        model_id=ai_settings.MODEL_ID,
        max_tokens=ai_settings.MAX_TOKENS,
        temperature=ai_settings.TEMPERATURE,
    )
    rag = RAGClient(bedrock_agent_client=bedrock_agent_runtime, kb_id=ai_settings.KB_ID)

    return (
        StepGenerator(llm=llm, rag=rag),
        RequiredStepJudge(llm=llm),
        SidePanelGenerator(llm=llm, rag=rag),
    )


# ---------------------------------------------------------------------------
# 출력 포맷터
# ---------------------------------------------------------------------------


def _print_required_step_banner(step: RequiredStepInfo, index: int, total: int) -> None:
    _section(f"필수 Step {index + 1}/{total} — {step.name}")
    print(f"  목표: {step.goal}")
    print(f"  진입 기준: {step.entry_criteria}")
    print("  충족 기준 측면:")
    for i, criterion in enumerate(step.fulfillment_criteria, start=1):
        print(f"    {i}. {criterion}")
    print(f"  최소 충족 개수: {step.minimum_fulfillment_count}")


def _print_generated_steps(output: GenerateOutput) -> None:
    print()
    _hr()
    print("  AI가 제안한 다음 Step 후보:")
    _hr()
    for i, step in enumerate(output.generated_steps, start=1):
        print(f"  {i}. {step.name}")
    _hr()


def _print_side_panel(output: SidePanelOutput) -> None:
    _section("📋 사이드패널")
    print()
    print("  📖 설명")
    _hr()
    print(f"  {output.mentoring.description}")
    print()
    print("  🔥 추천 방법")
    _hr()
    for method in output.mentoring.recommended_methods:
        print(f"  • {method.title}")
        print(f"    {method.content}")
    print()
    print("  ⚠️  흔한 실수")
    _hr()
    for mistake in output.mentoring.common_mistakes:
        print(f"  • {mistake.mistake}")
        print(f"      ❌ {mistake.bad_example}")
        print(f"      ✅ {mistake.good_example}")
    print()
    print("  💡 한 줄 팁")
    _hr()
    print(f"  {output.mentoring.one_line_tip}")
    print()
    print("  📚 용어 사전")
    _hr()
    for item in output.dictionary:
        print(f"  • {item.term}: {item.definition}")
    print()


# ---------------------------------------------------------------------------
# 상태 헬퍼
# ---------------------------------------------------------------------------


def _required_steps_status(required_steps: list[RequiredStepInfo]) -> list[RequiredStepStatus]:
    return [
        RequiredStepStatus(name=rs.name, order=i + 1, is_completed=rs.is_completed)
        for i, rs in enumerate(required_steps)
    ]


# ---------------------------------------------------------------------------
# 메인 루프
# ---------------------------------------------------------------------------


async def _run(
    project: ProjectInfo,
    step_gen: StepGenerator,
    judge: RequiredStepJudge,
    side_panel_gen: SidePanelGenerator,
) -> None:
    required_steps = stage_1_required_steps()
    current_index = 0
    decision_history: list[DecisionHistoryItem] = []

    # 시작점: R1 노드를 사용자가 클릭한 상태로 가정
    current_required = required_steps[current_index]
    decision_history.append(
        DecisionHistoryItem(
            step_id=current_required.step_id,
            name=current_required.name,
            status="ACCEPTED",
            stage_sequence=_STAGE.stage_sequence,
        )
    )
    current_step = StepInfo(step_id=current_required.step_id, name=current_required.name)
    accepted_steps_in_required: list[StepInfo] = []

    _print_required_step_banner(current_required, current_index, len(required_steps))

    while True:
        # ---- 1) generate ----
        _info("AI가 다음 Step 후보를 생성합니다...")
        gen_input = GenerateInput(
            project_info=project,
            current_stage=_STAGE,
            decision_history=decision_history,
            current_step=current_step,
            current_required_step=current_required,
        )
        try:
            gen_output = await step_gen.generate_steps(gen_input)
        except Exception as exc:
            _fail(f"generate 호출 실패: {type(exc).__name__}: {exc}")
            return

        _print_generated_steps(gen_output)

        # ---- 2) 사용자 선택 ----
        choice = _input_choice("선택 (1/2/3): ", range(1, 4))
        picked = gen_output.generated_steps[choice - 1]
        picked_step_info = StepInfo(step_id=str(uuid.uuid4()), name=picked.name)
        _ok(f"선택: {picked.name}")

        decision_history.append(
            DecisionHistoryItem(
                step_id=picked_step_info.step_id,
                name=picked_step_info.name,
                status="ACCEPTED",
                stage_sequence=_STAGE.stage_sequence,
            )
        )
        accepted_steps_in_required.append(picked_step_info)
        current_step = picked_step_info

        # ---- 3) accept ----
        _info("AI가 필수 Step 충족 여부를 판단합니다...")
        accept_input = AcceptInput(
            project_info=project,
            current_stage=_STAGE,
            required_steps_status=_required_steps_status(required_steps),
            current_required_step=current_required,
            accepted_steps_in_required=list(accepted_steps_in_required),
            accepted_step=picked_step_info,
        )
        try:
            accept_output = await judge.judge_required_step(accept_input)
        except Exception as exc:
            _fail(f"accept 호출 실패: {type(exc).__name__}: {exc}")
            return

        if accept_output.is_current_required_step_completed:
            _ok(f"필수 Step '{current_required.name}' 완료!")
        else:
            _wait(f"아직 미충족 (계속 진행) — {current_required.name}")

        # ---- 4) side_panel ----
        if _input_yes_no("사이드패널 보기? (y/N): "):
            _info("AI가 사이드패널 콘텐츠를 생성합니다...")
            sp_input = SidePanelInput(
                project_info=project,
                current_stage=_STAGE,
                target_step=picked_step_info,
                decision_history=decision_history,
                current_required_step=current_required,
            )
            try:
                sp_output = await side_panel_gen.generate_side_panel(sp_input)
                _print_side_panel(sp_output)
            except Exception as exc:
                _fail(f"side_panel 호출 실패: {type(exc).__name__}: {exc}")

        # ---- 5) 필수 Step 전환 ----
        if accept_output.is_current_required_step_completed:
            current_required.is_completed = True
            current_index += 1
            accepted_steps_in_required = []

            if current_index >= len(required_steps):
                _section("🎉 Stage 1 (아이디어 구체화) 완료!")
                _ok("R1 ~ R4 4개 필수 Step을 모두 충족했습니다.")
                return

            current_required = required_steps[current_index]
            decision_history.append(
                DecisionHistoryItem(
                    step_id=current_required.step_id,
                    name=current_required.name,
                    status="ACCEPTED",
                    stage_sequence=_STAGE.stage_sequence,
                )
            )
            current_step = StepInfo(
                step_id=current_required.step_id, name=current_required.name
            )
            _info(f"다음 필수 Step으로 전진: {current_required.name}")
            _print_required_step_banner(
                current_required, current_index, len(required_steps)
            )


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(name)s :: %(message)s",
        stream=sys.stderr,
    )
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


# ---------------------------------------------------------------------------
# design-export — fixture 데이터
# ---------------------------------------------------------------------------

_QUICK_MENTORING = MentoringContent(
    description="타겟 사용자를 파악하는 자리예요.",
    recommended_methods=[
        RecommendedMethod(
            title="타겟 사용자 인터뷰",
            content="5~10명의 타겟 사용자를 만나 현재 행동·맥락을 들어요.",
        ),
        RecommendedMethod(
            title="공개 설문",
            content="구글폼으로 30명 이상 대상 빠른 데이터 수집이 가능해요.",
        ),
    ],
    common_mistakes=[
        CommonMistake(
            mistake="친한 사람만 인터뷰하기",
            bad_example="친구 3명에게 물어봤다.",
            good_example="다양한 상황의 사용자 5명을 인터뷰했다.",
        ),
    ],
    one_line_tip="타겟 사용자의 '하루'를 알면 페르소나가 살아 있어요.",
)


def _design_export_quick_input() -> DesignExportInput:
    """빠른 모드 fixture — 즉시 실행 가능한 Stage 1 R2 데이터 (v1.4 Z+)."""
    project_context = ProjectContextForAI(
        name="스터디 매칭 앱",
        description="대학생용 스터디 매칭 플랫폼",
        duration_months=3,
        member_count=4,
        constraints=["React + FastAPI", "AWS 프리 티어"],
        initial_prompt="학과 선후배가 스터디를 쉽게 구성할 수 있는 앱을 만들고 싶음",
    )
    accepted_steps = [
        AcceptedStepForAI(
            name="타겟 사용자 인터뷰 계획",
            description="1차 타겟 사용자군 특성 정의 활동",
            sidepanel_mentoring=_QUICK_MENTORING,
        ),
        AcceptedStepForAI(
            name="경쟁 서비스 조사",
            description="에브리타임·카카오오픈채팅 등 기존 대안 분석",
            sidepanel_mentoring=None,
        ),
        AcceptedStepForAI(
            name="사용자 검증 설문 설계",
            description="30명 대상 구글폼 설문 항목 정의",
            sidepanel_mentoring=None,
        ),
    ]
    required_step = RequiredStepForAI(
        required_step_id="1-R2",
        required_step_name="대상 사용자 파악",
        goal="정의된 문제로 불편을 겪는 구체적 사용자군을 식별한다.",
        fulfillment_criteria=[
            "1차 타겟 사용자군의 특성 정의",
            "사용자의 현재 행동·습관·맥락 파악",
            "사용자 검증 활동",
        ],
        accepted_general_steps=accepted_steps,
    )
    return DesignExportInput(
        project_context=project_context,
        selected_required_steps=[required_step],
    )


def _design_export_detailed_input() -> DesignExportInput:
    """상세 모드 — 사용자 입력으로 ProjectContext + RS 수 선택 (v1.4 Z+)."""
    _section("design-export — 상세 입력")
    initial_prompt = _input_required("초기 아이디어: ")
    duration_months = _input_int("기간 (개월): ", minimum=1)
    member_count = _input_int("인원 (명): ", minimum=1)
    name = _input_optional("프로젝트 이름 (선택): ")
    _constraints_raw = _input_optional("제약사항 (콤마 구분, 선택): ")
    constraints = (
        [c.strip() for c in _constraints_raw.split(",") if c.strip()]
        if _constraints_raw
        else None
    )
    project_context = ProjectContextForAI(
        name=name,
        duration_months=duration_months,
        member_count=member_count,
        constraints=constraints,
        initial_prompt=initial_prompt,
    )

    num_rs = _input_choice("선택할 Required_Step 수 (1~3): ", range(1, 4))
    selected_required_steps: list[RequiredStepForAI] = []
    stage_names = [
        "아이디어 구체화", "프로젝트 계획", "요구사항 정의",
        "설계", "개발", "테스트 및 검증",
    ]
    for rs_idx in range(num_rs):
        seq = _input_choice(
            f"  RS{rs_idx + 1} — Stage 번호 (1~6): ", range(1, 7)
        )
        num_as = _input_choice(
            f"  RS{rs_idx + 1} — accepted_general_steps 수 (0~3): ",
            range(0, 4),
        )
        accepted: list[AcceptedStepForAI] = []
        for as_idx in range(num_as):
            accepted.append(
                AcceptedStepForAI(
                    name=f"Step {seq}-{rs_idx + 1}-{as_idx + 1}",
                    description="(시뮬레이터 자동 생성)",
                    sidepanel_mentoring=None,
                )
            )
        selected_required_steps.append(
            RequiredStepForAI(
                required_step_id=f"{seq}-R{rs_idx + 1}",
                required_step_name=f"{stage_names[seq - 1]} 필수 Step {rs_idx + 1}",
                goal="(시뮬레이터 자동 생성)",
                fulfillment_criteria=["기준 1", "기준 2"],
                accepted_general_steps=accepted,
            )
        )

    return DesignExportInput(
        project_context=project_context,
        selected_required_steps=selected_required_steps,
    )


def _build_design_export_anthropic() -> AsyncAnthropic:
    """design-export용 AsyncAnthropic 클라이언트 생성."""
    return _build_anthropic_client()


def _print_design_export_header(input_data: DesignExportInput) -> None:
    _section("design-export 시나리오 시작")
    ctx = input_data.project_context
    total_as = sum(
        len(rs.accepted_general_steps) for rs in input_data.selected_required_steps
    )
    print(f"  이름          : {ctx.name or '(미입력)'}")
    print(f"  인원·기간     : {ctx.member_count}명 / {ctx.duration_months}개월")
    print(f"  Required_Step : {len(input_data.selected_required_steps)}개")
    print(f"  accepted steps: {total_as}개")


def _print_design_export_result(result: DesignExportOutput) -> None:
    """AI 생성 결과(questions_per_rs + core_summary)를 터미널에 출력."""
    _section("AI 생성 결과 (v1.4 Z+)")

    print()
    print("  [RS별 What·Why 질문]")
    _hr()
    for rs_q in result.questions_per_rs:
        print(f"  • {rs_q.required_step_id}")
        for i, q in enumerate(rs_q.questions, start=1):
            print(f"    {i}. {q}")
        print()

    print("  [핵심 What·Why 정리]")
    _hr()
    for item in result.core_summary:
        print(f"  - {item}")
    print()

    _ok("검증 PASS (금지 표현 0건, required_step_id 매칭 정상)")
    _hr()


async def _run_design_export(input_data: DesignExportInput) -> None:
    """design-export 시나리오 실행 — Anthropic 호출 + 결과 출력 (v1.4 Z+)."""
    anthropic_client = _build_design_export_anthropic()

    _wait("프롬프트 렌더 + Anthropic 호출 중...")
    t_start = time.perf_counter()
    try:
        result = await generate_design_export(
            input_data=input_data,
            anthropic_client=anthropic_client,
            model_id=ai_settings.MODEL_ID,
        )
    except OutputViolatesHonestyGuardError as exc:
        elapsed = time.perf_counter() - t_start
        _fail(f"검증 실패 (HONESTY)  [{elapsed:.2f}s]")
        phrase = exc.details.get("banned_phrase", "(알 수 없음)")
        print(f"  banned_phrase: {phrase!r}")
        expected = exc.details.get("expected")
        actual = exc.details.get("actual")
        if expected is not None and actual is not None:
            print(f"  expected IDs: {expected}")
            print(f"  actual IDs  : {actual}")
        print("  → 프롬프트 강화 또는 max_tokens 재검토 필요.")
        return
    except BedrockAPIError as exc:
        elapsed = time.perf_counter() - t_start
        _fail(f"LLM API 오류  [{elapsed:.2f}s]: {exc.message}")
        return
    except AIGenerationFailedError as exc:
        elapsed = time.perf_counter() - t_start
        _fail(f"AI 생성 실패  [{elapsed:.2f}s]: {exc.message}")
        return

    elapsed = time.perf_counter() - t_start
    total_questions = sum(len(rs_q.questions) for rs_q in result.questions_per_rs)

    print()
    _hr()
    print("  [응답 수신]")
    print(f"  응답 시간       : {elapsed:.2f}s")
    print(f"  RS 수           : {len(result.questions_per_rs)}개")
    print(f"  질문 총 수      : {total_questions}개")
    print(f"  핵심 정리 수    : {len(result.core_summary)}개")
    _hr()

    _print_design_export_result(result)


# ---------------------------------------------------------------------------
# 메인 루프
# ---------------------------------------------------------------------------


def main() -> None:
    """엔트리포인트 — 시나리오 선택 후 실행."""
    _setup_logging()

    _section("Poco AI 시뮬레이터")
    print(f"  AWS_REGION : {ai_settings.AWS_REGION}")
    print(f"  MODEL_ID   : {ai_settings.MODEL_ID}")
    print(f"  KB_ID      : {ai_settings.KB_ID or '(미설정 — RAG는 빈 결과 폴백)'}")

    print()
    print("  시나리오 선택:")
    print("  1. Stage 1 (R1~R4) 시뮬레이션 [generate → accept → side_panel]")
    print("  2. design-export 시나리오 [사고 궤적 .md 생성]")
    scenario = _input_choice("번호: ", range(1, 3))

    if scenario == 1:
        _run_stage1_scenario()
    else:
        _run_design_export_scenario()


def _run_stage1_scenario() -> None:
    """기존 Stage 1 R1~R4 시뮬레이션 진입점."""
    _section("Poco AI 시뮬레이터 — Stage 1 (R1~R4)")
    project = _build_project_info()
    step_gen, judge, side_panel_gen = _build_services()
    try:
        asyncio.run(_run(project, step_gen, judge, side_panel_gen))
    except KeyboardInterrupt:
        print()
        _info("사용자 중단")


def _run_design_export_scenario() -> None:
    """design-export 시나리오 진입점."""
    print()
    print("  입력 모드 선택:")
    print("  1. 빠른 모드 (사전 fixture — 즉시 실행)")
    print("  2. 상세 모드 (직접 입력)")
    mode = _input_choice("번호: ", range(1, 3))

    if mode == 1:
        input_data = _design_export_quick_input()
    else:
        input_data = _design_export_detailed_input()

    _print_design_export_header(input_data)

    try:
        asyncio.run(_run_design_export(input_data))
    except KeyboardInterrupt:
        print()
        _info("사용자 중단")

    if _input_yes_no("다시 실행? (y/N): "):
        _run_design_export_scenario()


if __name__ == "__main__":
    main()
