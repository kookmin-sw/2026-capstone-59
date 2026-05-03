"""터미널 기반 Stage 1 R1~R4 수동 테스트 시뮬레이터.

실행: ``python -m ai.cli_simulator``

실제 Bedrock API를 호출하여 generate → accept → side_panel 흐름을 모사한다.
인메모리 상태만 유지하며 DB는 사용하지 않는다.
"""

from __future__ import annotations

import asyncio
import logging
import sys
import uuid
from typing import Optional

import boto3

from ai.clients.llm import LLMClient
from ai.clients.rag import RAGClient
from ai.config import ai_settings
from ai.fixtures.required_steps import stage_1_required_steps
from ai.schemas.accept import AcceptInput
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
from ai.services.required_step_judge import RequiredStepJudge
from ai.services.side_panel_generator import SidePanelGenerator
from ai.services.step_generator import StepGenerator

_STAGE = StageInfo(stage_id="stage-1", stage_number=1, name="아이디어 구체화")


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
    constraints = _input_optional("제약사항 (선택, 엔터=스킵): ")

    return ProjectInfo(
        project_id=str(uuid.uuid4()),
        name=name,
        duration_months=duration_months,
        member_count=member_count,
        description=description,
        constraints=constraints,
        initial_prompt=initial_prompt,
    )


def _build_services() -> tuple[StepGenerator, RequiredStepJudge, SidePanelGenerator]:
    bedrock_runtime = boto3.client("bedrock-runtime", region_name=ai_settings.AWS_REGION)
    bedrock_agent_runtime = boto3.client(
        "bedrock-agent-runtime", region_name=ai_settings.AWS_REGION
    )

    llm = LLMClient(
        bedrock_client=bedrock_runtime,
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
            stage_number=_STAGE.stage_number,
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
                stage_number=_STAGE.stage_number,
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
                    stage_number=_STAGE.stage_number,
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


def main() -> None:
    """엔트리포인트 — 인터랙티브 Stage 1 시뮬레이션."""
    _setup_logging()

    _section("Poco AI 시뮬레이터 — Stage 1 (R1~R4)")
    print(f"  AWS_REGION : {ai_settings.AWS_REGION}")
    print(f"  MODEL_ID   : {ai_settings.MODEL_ID}")
    print(f"  KB_ID      : {ai_settings.KB_ID or '(미설정 — RAG는 빈 결과 폴백)'}")

    project = _build_project_info()
    step_gen, judge, side_panel_gen = _build_services()

    try:
        asyncio.run(_run(project, step_gen, judge, side_panel_gen))
    except KeyboardInterrupt:
        print()
        _info("사용자 중단")


if __name__ == "__main__":
    main()
