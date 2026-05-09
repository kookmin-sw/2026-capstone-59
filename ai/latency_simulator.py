"""Pipeline 레이턴시 측정용 CLI 시뮬레이터.

실행: ``python -m ai.latency_simulator [--runs N] [--output PATH] [--baseline]``

Stage 1 R1("문제/기회 정의") 고정 fixture 입력으로 Pipeline 1회(또는 N회)를
실제 Bedrock에 대해 실행하고, stage별/call별 wall-clock elapsed를 기록한다.

Pipeline 구조:
    Stage A — judge ∥ generate (asyncio.gather)
    Stage B — side_panel × 3  (asyncio.gather, generated_steps 3개)

- ai/cli_simulator.py는 수정하지 않는다. 필요한 빌더 로직은 본 모듈에 재구현한다.
- Python 3.9 호환을 위해 typing.Optional/Dict/List를 사용한다.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Awaitable, Dict, List, Optional, Tuple

import boto3

from ai.clients.llm import LLMClient
from ai.clients.rag import RAGClient
from ai.config import ai_settings
from ai.fixtures.required_steps import stage_1_required_steps
from ai.schemas.accept import AcceptInput, AcceptOutput
from ai.schemas.common import (
    DecisionHistoryItem,
    GeneratedStep,
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


SCHEMA_VERSION = "1.0"
SCHEMA_VERSION_STREAMING = "1.1"
SCENARIO_TAG = "stage1_r1_problem_definition"
DEFAULT_BASELINE_PATH = Path(".kiro/specs/ai-latency-optimization/baseline.json")


# ---------------------------------------------------------------------------
# Fixture — Stage 1 R1 "문제/기회 정의" 고정 입력
# ---------------------------------------------------------------------------


_STAGE = StageInfo(stage_id="stage-1", stage_sequence=1, name="아이디어 구체화")


def _build_fixture_project() -> ProjectInfo:
    return ProjectInfo(
        project_id="fixture-proj-001",
        name="Latency Baseline Fixture",
        duration_months=3,
        member_count=4,
        description="레이턴시 측정용 고정 프로젝트",
        constraints="기술 스택은 React + FastAPI로 제한",
        initial_prompt=(
            "배달 라이더들이 경로를 비효율적으로 다니는 문제를 AI로 해결하고 싶어요"
        ),
    )


def _build_fixture_required_step() -> RequiredStepInfo:
    """Stage 1 R1 ("문제/기회 정의")을 fixture로 재사용."""
    return stage_1_required_steps()[0]


def _build_required_steps_status() -> List[RequiredStepStatus]:
    steps = stage_1_required_steps()
    return [
        RequiredStepStatus(name=rs.name, order=i + 1, is_completed=False)
        for i, rs in enumerate(steps)
    ]


def _build_generate_input() -> GenerateInput:
    project = _build_fixture_project()
    required = _build_fixture_required_step()
    current_step = StepInfo(step_id=required.step_id, name=required.name)
    decision_history = [
        DecisionHistoryItem(
            step_id=required.step_id,
            name=required.name,
            status="ACCEPTED",
            stage_sequence=_STAGE.stage_sequence,
        )
    ]
    return GenerateInput(
        project_info=project,
        current_stage=_STAGE,
        decision_history=decision_history,
        current_step=current_step,
        current_required_step=required,
    )


def _build_accept_input() -> AcceptInput:
    project = _build_fixture_project()
    required = _build_fixture_required_step()
    # 방금 Accept한 Step = 필수 Step 영역 내에서 사용자가 선택한 Step
    accepted_step = StepInfo(step_id=str(uuid.uuid4()), name="문제 상황 서술")
    return AcceptInput(
        project_info=project,
        current_stage=_STAGE,
        required_steps_status=_build_required_steps_status(),
        current_required_step=required,
        accepted_steps_in_required=[accepted_step],
        accepted_step=accepted_step,
    )


def _build_side_panel_input(generated: GeneratedStep) -> SidePanelInput:
    project = _build_fixture_project()
    required = _build_fixture_required_step()
    target = StepInfo(step_id=str(uuid.uuid4()), name=generated.name)
    decision_history = [
        DecisionHistoryItem(
            step_id=required.step_id,
            name=required.name,
            status="ACCEPTED",
            stage_sequence=_STAGE.stage_sequence,
        )
    ]
    return SidePanelInput(
        project_info=project,
        current_stage=_STAGE,
        target_step=target,
        decision_history=decision_history,
        current_required_step=required,
    )


# ---------------------------------------------------------------------------
# Service 빌더 (cli_simulator._build_services와 동등한 로직을 재구현)
# ---------------------------------------------------------------------------


def _build_services() -> Tuple[StepGenerator, RequiredStepJudge, SidePanelGenerator]:
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
# 측정 / 실행
# ---------------------------------------------------------------------------


class _StageError(Exception):
    """Pipeline 실행 중 특정 stage/call에서 발생한 예외를 식별 가능한 형태로 래핑."""

    def __init__(self, label: str, elapsed_s: float, cause: BaseException) -> None:
        super().__init__(f"[{label}] after {elapsed_s:.3f}s: {type(cause).__name__}: {cause}")
        self.label = label
        self.elapsed_s = elapsed_s
        self.cause = cause


async def _measure_call(label: str, coro: Awaitable[Any]) -> Dict[str, Any]:
    start = time.perf_counter()
    try:
        result = await coro
    except BaseException as exc:  # noqa: BLE001 — 래핑 후 재throw
        elapsed = time.perf_counter() - start
        raise _StageError(label, elapsed, exc) from exc
    elapsed = time.perf_counter() - start
    return {"elapsed_s": elapsed, "result": result}


async def _run_pipeline(
    step_gen: StepGenerator,
    judge: RequiredStepJudge,
    sp_gen: SidePanelGenerator,
) -> Dict[str, Any]:
    """Stage A (judge ∥ generate) → Stage B (side_panel × 3)."""
    # --- Stage A ---
    t0 = time.perf_counter()
    judge_coro = _measure_call("judge", judge.judge_required_step(_build_accept_input()))
    gen_coro = _measure_call("generate", step_gen.generate_steps(_build_generate_input()))
    judge_m, gen_m = await asyncio.gather(judge_coro, gen_coro)
    stage_a_s = time.perf_counter() - t0

    gen_output: GenerateOutput = gen_m["result"]
    judge_output: AcceptOutput = judge_m["result"]

    # --- Stage B ---
    t1 = time.perf_counter()
    sp_coros = [
        _measure_call(
            f"side_panel_{i}",
            sp_gen.generate_side_panel(_build_side_panel_input(step)),
        )
        for i, step in enumerate(gen_output.generated_steps)
    ]
    sp_ms = await asyncio.gather(*sp_coros)
    stage_b_s = time.perf_counter() - t1

    pipeline_s = stage_a_s + stage_b_s
    return {
        "judge_s": judge_m["elapsed_s"],
        "generate_s": gen_m["elapsed_s"],
        "side_panel_s": [m["elapsed_s"] for m in sp_ms],
        "stage_a_s": stage_a_s,
        "stage_b_s": stage_b_s,
        "pipeline_s": pipeline_s,
        "outputs": {
            "judge": judge_output.model_dump(mode="json"),
            "generate": gen_output.model_dump(mode="json"),
            "side_panels": [m["result"].model_dump(mode="json") for m in sp_ms],
        },
    }


async def _consume_stream(
    label: str,
    sp_gen: SidePanelGenerator,
    input_data: SidePanelInput,
) -> Dict[str, Any]:
    """SidePanelGenerator.generate_stream을 소비하며 TTFT/TTLT 측정."""
    start = time.perf_counter()
    first_chunk_at: Optional[float] = None
    chunks: List[str] = []
    try:
        async for chunk in sp_gen.generate_stream(input_data):
            if first_chunk_at is None:
                first_chunk_at = time.perf_counter()
            chunks.append(chunk)
    except BaseException as exc:  # noqa: BLE001
        elapsed = time.perf_counter() - start
        raise _StageError(label, elapsed, exc) from exc
    end = time.perf_counter()
    ttft = (first_chunk_at - start) if first_chunk_at is not None else 0.0
    ttlt = end - start
    return {
        "label": label,
        "ttft_s": ttft,
        "ttlt_s": ttlt,
        "aggregated_text": "".join(chunks),
    }


async def _run_pipeline_streaming(
    step_gen: StepGenerator,
    judge: RequiredStepJudge,
    sp_gen: SidePanelGenerator,
) -> Dict[str, Any]:
    """Stage A는 non-stream 그대로, Stage B만 3개 병렬 스트림."""
    # --- Stage A (기존 동일) ---
    t0 = time.perf_counter()
    judge_coro = _measure_call("judge", judge.judge_required_step(_build_accept_input()))
    gen_coro = _measure_call("generate", step_gen.generate_steps(_build_generate_input()))
    judge_m, gen_m = await asyncio.gather(judge_coro, gen_coro)
    stage_a_s = time.perf_counter() - t0

    gen_output: GenerateOutput = gen_m["result"]
    judge_output: AcceptOutput = judge_m["result"]

    # --- Stage B (streaming × 3) ---
    t1 = time.perf_counter()
    sp_tasks = [
        _consume_stream(
            f"side_panel_{i}",
            sp_gen,
            _build_side_panel_input(step),
        )
        for i, step in enumerate(gen_output.generated_steps)
    ]
    sp_results = await asyncio.gather(*sp_tasks)
    stage_b_wall_s = time.perf_counter() - t1

    ttfts = [r["ttft_s"] for r in sp_results]
    ttlts = [r["ttlt_s"] for r in sp_results]
    stage_b_ttft_s = min(ttfts) if ttfts else 0.0
    stage_b_ttlt_s = max(ttlts) if ttlts else 0.0
    pipeline_ttft_s = stage_a_s + stage_b_ttft_s
    pipeline_ttlt_s = stage_a_s + stage_b_ttlt_s

    return {
        "judge_s": judge_m["elapsed_s"],
        "generate_s": gen_m["elapsed_s"],
        "side_panel_streams": [
            {
                "label": r["label"],
                "ttft_s": r["ttft_s"],
                "ttlt_s": r["ttlt_s"],
            }
            for r in sp_results
        ],
        "stage_a_s": stage_a_s,
        "stage_b_wall_s": stage_b_wall_s,
        "stage_b_ttft_s": stage_b_ttft_s,
        "stage_b_ttlt_s": stage_b_ttlt_s,
        "pipeline_ttft_s": pipeline_ttft_s,
        "pipeline_ttlt_s": pipeline_ttlt_s,
        "outputs": {
            "judge": judge_output.model_dump(mode="json"),
            "generate": gen_output.model_dump(mode="json"),
            "side_panels": [
                {"label": r["label"], "aggregated_text": r["aggregated_text"]}
                for r in sp_results
            ],
        },
    }


# ---------------------------------------------------------------------------
# 통계 (외부 의존성 없음)
# ---------------------------------------------------------------------------


def _percentile(values: List[float], pct: float) -> float:
    """nearest-rank 방식 percentile. 단일 원소에도 안전.

    - pct=0.5  → median (p50)
    - pct=1.0  → max    (p100)
    - 빈 리스트 → 0.0
    """
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    if pct >= 1.0:
        return sorted_vals[-1]
    if pct <= 0.0:
        return sorted_vals[0]
    k = max(
        0,
        min(len(sorted_vals) - 1, int(round(pct * (len(sorted_vals) - 1)))),
    )
    return sorted_vals[k]


def _summarize(per_run: List[Dict[str, Any]]) -> Dict[str, Any]:
    """per_run 집계 → judge/generate/side_panel_max/stage_a/stage_b/pipeline × (p50, p100)."""

    def field(pick) -> Dict[str, float]:
        vals = [pick(r) for r in per_run]
        return {"p50": _percentile(vals, 0.5), "p100": _percentile(vals, 1.0)}

    return {
        "judge": field(lambda r: r["judge_s"]),
        "generate": field(lambda r: r["generate_s"]),
        "side_panel_max": field(lambda r: max(r["side_panel_s"])),
        "stage_a": field(lambda r: r["stage_a_s"]),
        "stage_b": field(lambda r: r["stage_b_s"]),
        "pipeline": field(lambda r: r["pipeline_s"]),
    }


def _strip_outputs_for_run(run: Dict[str, Any]) -> Dict[str, Any]:
    """per_run 저장 시 응답 본문은 제외하고 타이밍만 남긴다."""
    return {
        "judge_s": run["judge_s"],
        "generate_s": run["generate_s"],
        "side_panel_s": run["side_panel_s"],
        "stage_a_s": run["stage_a_s"],
        "stage_b_s": run["stage_b_s"],
        "pipeline_s": run["pipeline_s"],
    }


def _strip_outputs_for_stream_run(run: Dict[str, Any]) -> Dict[str, Any]:
    """streaming per_run 저장 시 응답 본문을 제거하고 타이밍만 남긴다."""
    return {
        "judge_s": run["judge_s"],
        "generate_s": run["generate_s"],
        "side_panel_streams": run["side_panel_streams"],
        "stage_a_s": run["stage_a_s"],
        "stage_b_wall_s": run["stage_b_wall_s"],
        "stage_b_ttft_s": run["stage_b_ttft_s"],
        "stage_b_ttlt_s": run["stage_b_ttlt_s"],
        "pipeline_ttft_s": run["pipeline_ttft_s"],
        "pipeline_ttlt_s": run["pipeline_ttlt_s"],
    }


def _summarize_streaming(per_run: List[Dict[str, Any]]) -> Dict[str, Any]:
    """streaming per_run 집계 — ttft/ttlt/pipeline_ttft/pipeline_ttlt × (p50, p100)."""

    def field(pick) -> Dict[str, float]:
        vals = [pick(r) for r in per_run]
        return {"p50": _percentile(vals, 0.5), "p100": _percentile(vals, 1.0)}

    return {
        "judge": field(lambda r: r["judge_s"]),
        "generate": field(lambda r: r["generate_s"]),
        "stage_a": field(lambda r: r["stage_a_s"]),
        "ttft": field(lambda r: r["stage_b_ttft_s"]),
        "ttlt": field(lambda r: r["stage_b_ttlt_s"]),
        "pipeline_ttft": field(lambda r: r["pipeline_ttft_s"]),
        "pipeline_ttlt": field(lambda r: r["pipeline_ttlt_s"]),
    }


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# 콘솔 출력 (한국어)
# ---------------------------------------------------------------------------


def _hr(char: str = "─", width: int = 55) -> None:
    print(char * width)


def _section(title: str) -> None:
    print()
    _hr("═")
    print(f"  {title}")
    _hr("═")


def _print_run(index: int, total: int, run: Dict[str, Any]) -> None:
    _section(f"Run {index + 1}/{total} — Pipeline Latency")
    print("  Stage A (judge ∥ generate)")
    print(f"    judge        : {run['judge_s']:.3f}s")
    print(f"    generate     : {run['generate_s']:.3f}s")
    print(f"    stage_a_s    : {run['stage_a_s']:.3f}s  (= max of the two)")
    print("  Stage B (side_panel × 3)")
    for i, s in enumerate(run["side_panel_s"]):
        print(f"    side_panel[{i}]: {s:.3f}s")
    print(f"    stage_b_s    : {run['stage_b_s']:.3f}s  (= max of the three)")
    print(f"  Pipeline total : {run['pipeline_s']:.3f}s  (= stage_a + stage_b)")

    outputs = run.get("outputs") or {}
    gen = outputs.get("generate") or {}
    generated_steps = gen.get("generated_steps") or []
    if generated_steps:
        print()
        _hr()
        print("  [generate] 생성된 3개 Step")
        _hr()
        for i, step in enumerate(generated_steps, start=1):
            name = step.get("name", "")
            desc = step.get("description", "")
            print(f"  {i}. {name}")
            if desc:
                print(f"     {desc}")

    side_panels = outputs.get("side_panels") or []
    for i, sp in enumerate(side_panels):
        print()
        _hr()
        print(f"  [side_panel #{i + 1}]")
        _hr()
        mentoring = sp.get("mentoring") or {}
        print(f"  description     : {mentoring.get('description', '')}")
        methods = mentoring.get("recommended_methods") or []
        for j, m in enumerate(methods, start=1):
            print(f"  method[{j}]       : {m.get('title', '')} — {m.get('content', '')}")
        mistakes = mentoring.get("common_mistakes") or []
        for j, mk in enumerate(mistakes, start=1):
            print(f"  mistake[{j}]      : {mk.get('mistake', '')}")
            print(f"    bad           : {mk.get('bad_example', '')}")
            print(f"    good          : {mk.get('good_example', '')}")
        tip = mentoring.get("one_line_tip", "")
        if tip:
            print(f"  one_line_tip    : {tip}")
        dictionary = sp.get("dictionary") or []
        for j, d in enumerate(dictionary, start=1):
            print(f"  dict[{j}]         : {d.get('term', '')} — {d.get('definition', '')}")


def _print_summary(summary: Dict[str, Any], runs_count: int) -> None:
    _section(f"Summary (N={runs_count})")
    fields = [
        ("judge", "judge         "),
        ("generate", "generate      "),
        ("side_panel_max", "side_panel_max"),
        ("stage_a", "stage_a       "),
        ("stage_b", "stage_b       "),
        ("pipeline", "pipeline      "),
    ]
    for key, label in fields:
        entry = summary.get(key, {})
        p50 = entry.get("p50", 0.0)
        p100 = entry.get("p100", 0.0)
        print(f"  {label} p50={p50:.3f}s  p100={p100:.3f}s")


def _print_stream_run(index: int, total: int, run: Dict[str, Any]) -> None:
    _section(f"Run {index + 1}/{total} — Pipeline Latency (streaming)")
    print("  Stage A (judge ∥ generate)")
    print(f"    judge        : {run['judge_s']:.3f}s")
    print(f"    generate     : {run['generate_s']:.3f}s")
    print(f"    stage_a_s    : {run['stage_a_s']:.3f}s  (= max of the two)")
    print("  Stage B (side_panel × 3, streaming)")
    for stream in run["side_panel_streams"]:
        print(
            f"    {stream['label']}: "
            f"ttft={stream['ttft_s']:.3f}s  ttlt={stream['ttlt_s']:.3f}s"
        )
    print(
        f"    stage_b      : ttft={run['stage_b_ttft_s']:.3f}s (min)  "
        f"ttlt={run['stage_b_ttlt_s']:.3f}s (max)  wall={run['stage_b_wall_s']:.3f}s"
    )
    print(
        f"  Pipeline       : ttft={run['pipeline_ttft_s']:.3f}s  "
        f"ttlt={run['pipeline_ttlt_s']:.3f}s"
    )


def _print_stream_summary(summary: Dict[str, Any], runs_count: int) -> None:
    _section(f"Summary — streaming (N={runs_count})")
    fields = [
        ("judge", "judge         "),
        ("generate", "generate      "),
        ("stage_a", "stage_a       "),
        ("ttft", "ttft          "),
        ("ttlt", "ttlt          "),
        ("pipeline_ttft", "pipeline_ttft "),
        ("pipeline_ttlt", "pipeline_ttlt "),
    ]
    for key, label in fields:
        entry = summary.get(key, {})
        p50 = entry.get("p50", 0.0)
        p100 = entry.get("p100", 0.0)
        print(f"  {label} p50={p50:.3f}s  p100={p100:.3f}s")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m ai.latency_simulator",
        description="Pipeline 레이턴시 측정 CLI (Stage 1 R1 fixture 고정)",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Pipeline 반복 실행 횟수 (기본 1)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="결과 JSON 파일 저장 경로 (생략 시 저장 안 함)",
    )
    parser.add_argument(
        "--baseline",
        action="store_true",
        help=(
            "Baseline 기록 모드. target 파일이 이미 존재하면 refuse(exit 2). "
            "--output 미지정 시 기본 경로 .kiro/specs/ai-latency-optimization/baseline.json 사용"
        ),
    )
    parser.add_argument(
        "--streaming",
        action="store_true",
        help="Stage B를 스트리밍 모드로 실행하고 TTFT/TTLT를 측정한다 (artifact schema 1.1).",
    )
    return parser.parse_args(argv)


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(name)s :: %(message)s",
        stream=sys.stderr,
    )
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def main(argv: Optional[List[str]] = None) -> int:
    """엔트리포인트.

    Exit codes:
        0   — 성공
        1   — Pipeline 실행 실패 (stage/call 예외 등)
        2   — --baseline 모드에서 target 파일이 이미 존재
        130 — 사용자 중단 (SIGINT)
    """
    _setup_logging()
    args = _parse_args(argv)

    if args.baseline:
        target = Path(args.output) if args.output else DEFAULT_BASELINE_PATH
        if target.exists():
            print(
                f"[refuse] Baseline 이미 존재: {target}",
                file=sys.stderr,
            )
            return 2

    try:
        step_gen, judge, sp_gen = _build_services()
    except Exception as exc:  # noqa: BLE001
        print(
            f"[fail] service_init exc={type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 1

    per_run: List[Dict[str, Any]] = []
    per_run_full: List[Dict[str, Any]] = []

    try:
        for i in range(args.runs):
            try:
                # run마다 새 event loop를 사용해 run 간 상태 오염을 방지
                if args.streaming:
                    run_result = asyncio.run(_run_pipeline_streaming(step_gen, judge, sp_gen))
                else:
                    run_result = asyncio.run(_run_pipeline(step_gen, judge, sp_gen))
            except _StageError as e:
                print(
                    f"[fail] stage={e.label} "
                    f"exc={type(e.cause).__name__}: {e.cause}",
                    file=sys.stderr,
                )
                return 1
            except Exception as exc:  # noqa: BLE001
                print(
                    f"[fail] stage=unknown exc={type(exc).__name__}: {exc}",
                    file=sys.stderr,
                )
                return 1

            per_run_full.append(run_result)
            if args.streaming:
                per_run.append(_strip_outputs_for_stream_run(run_result))
                _print_stream_run(i, args.runs, run_result)
            else:
                per_run.append(_strip_outputs_for_run(run_result))
                _print_run(i, args.runs, run_result)
    except KeyboardInterrupt:
        print()
        print("[interrupt] 사용자 중단", file=sys.stderr)
        return 130

    if args.streaming:
        summary = _summarize_streaming(per_run)
        _print_stream_summary(summary, args.runs)
    else:
        summary = _summarize(per_run)
        _print_summary(summary, args.runs)

    artifact = {
        "schema_version": SCHEMA_VERSION_STREAMING if args.streaming else SCHEMA_VERSION,
        "timestamp": _utc_now_iso(),
        "model_id": ai_settings.MODEL_ID,
        "scenario": SCENARIO_TAG,
        "runs_count": args.runs,
        "per_run": per_run,
        "summary": summary,
    }
    if args.streaming:
        artifact["mode"] = "streaming"

    if args.output or args.baseline:
        out_path = Path(args.output) if args.output else DEFAULT_BASELINE_PATH
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(artifact, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[saved] {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
