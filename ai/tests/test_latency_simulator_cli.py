"""ai/latency_simulator.py CLI / 순수 함수 단위 테스트.

실제 Bedrock은 호출하지 않는다. `_build_services`를 mock하여 서비스 객체들을
AsyncMock으로 주입하고, CLI가 `--baseline` refuse 경로 / summary 생성 등
순수 기능을 올바르게 수행하는지 검증한다.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai import latency_simulator as ls
from ai.schemas.accept import AcceptOutput
from ai.schemas.common import (
    CommonMistake,
    DictionaryItem,
    GeneratedStep,
    MentoringContent,
    RecommendedMethod,
)
from ai.schemas.generate import GenerateOutput
from ai.schemas.side_panel import SidePanelOutput


# ---------------------------------------------------------------------------
# _parse_args
# ---------------------------------------------------------------------------


class TestParseArgs:
    def test_parses_runs_output_and_baseline(self) -> None:
        args = ls._parse_args(["--runs", "5", "--output", "/tmp/x.json", "--baseline"])

        assert args.runs == 5
        assert args.output == "/tmp/x.json"
        assert args.baseline is True

    def test_defaults(self) -> None:
        args = ls._parse_args([])

        assert args.runs == 1
        assert args.output is None
        assert args.baseline is False


# ---------------------------------------------------------------------------
# _percentile
# ---------------------------------------------------------------------------


class TestPercentile:
    def test_single_element_p50_and_p100_equal_value(self) -> None:
        assert ls._percentile([1.0], 0.5) == 1.0
        assert ls._percentile([1.0], 1.0) == 1.0

    def test_five_elements_nearest_rank(self) -> None:
        vals = [1.0, 2.0, 3.0, 4.0, 5.0]
        # nearest-rank: k = round(0.5 * 4) = 2 → sorted[2] = 3.0
        assert ls._percentile(vals, 0.5) == 3.0
        # p100 은 항상 max
        assert ls._percentile(vals, 1.0) == 5.0

    def test_empty_returns_zero(self) -> None:
        assert ls._percentile([], 0.5) == 0.0


# ---------------------------------------------------------------------------
# _summarize
# ---------------------------------------------------------------------------


class TestSummarize:
    def test_produces_all_six_fields_with_p50_p100(self) -> None:
        per_run: List[Dict[str, Any]] = [
            {
                "judge_s": 2.0,
                "generate_s": 5.0,
                "side_panel_s": [10.0, 11.0, 9.0],
                "stage_a_s": 5.0,
                "stage_b_s": 11.0,
                "pipeline_s": 16.0,
            },
            {
                "judge_s": 3.0,
                "generate_s": 6.0,
                "side_panel_s": [9.5, 10.5, 11.5],
                "stage_a_s": 6.0,
                "stage_b_s": 11.5,
                "pipeline_s": 17.5,
            },
        ]

        summary = ls._summarize(per_run)

        assert set(summary.keys()) == {
            "judge",
            "generate",
            "side_panel_max",
            "stage_a",
            "stage_b",
            "pipeline",
        }
        for key in summary:
            assert set(summary[key].keys()) == {"p50", "p100"}

        # side_panel_max는 각 run의 max를 사용 → [11.0, 11.5]
        assert summary["side_panel_max"]["p100"] == 11.5
        assert summary["pipeline"]["p100"] == 17.5


# ---------------------------------------------------------------------------
# --baseline refuse 경로
# ---------------------------------------------------------------------------


def _mock_services():
    """latency_simulator가 기대하는 서비스 3개를 AsyncMock으로 반환."""
    valid_generate = GenerateOutput(
        generated_steps=[
            GeneratedStep(name="A", description="a"),
            GeneratedStep(name="B", description="b"),
            GeneratedStep(name="C", description="c"),
        ]
    )
    valid_side_panel = SidePanelOutput(
        mentoring=MentoringContent(
            description="d",
            recommended_methods=[
                RecommendedMethod(title="t1", content="c1"),
                RecommendedMethod(title="t2", content="c2"),
            ],
            common_mistakes=[
                CommonMistake(
                    mistake="m",
                    bad_example="b",
                    good_example="g",
                ),
            ],
            one_line_tip="tip",
        ),
        dictionary=[
            DictionaryItem(term="x", definition="y"),
            DictionaryItem(term="z", definition="w"),
        ],
    )
    valid_judge = AcceptOutput(is_current_required_step_completed=True)

    step_gen = MagicMock()
    step_gen.generate_steps = AsyncMock(return_value=valid_generate)

    judge = MagicMock()
    judge.judge_required_step = AsyncMock(return_value=valid_judge)

    sp_gen = MagicMock()
    sp_gen.generate_side_panel = AsyncMock(return_value=valid_side_panel)

    return step_gen, judge, sp_gen


class TestBaselineRefuse:
    def test_refuses_when_baseline_output_already_exists(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        target = tmp_path / "baseline.json"
        target.write_text("{}", encoding="utf-8")
        assert target.exists()

        exit_code = ls.main(["--baseline", "--output", str(target)])

        assert exit_code == 2
        captured = capsys.readouterr()
        assert "[refuse]" in captured.err
        assert str(target) in captured.err
        # 기존 파일 내용이 보존되어야 한다
        assert target.read_text(encoding="utf-8") == "{}"

    def test_writes_artifact_when_baseline_target_does_not_exist(
        self, tmp_path: Path
    ) -> None:
        target = tmp_path / "nested" / "baseline.json"
        assert not target.exists()

        with patch.object(ls, "_build_services", return_value=_mock_services()):
            exit_code = ls.main(["--baseline", "--output", str(target), "--runs", "1"])

        assert exit_code == 0
        assert target.exists()
