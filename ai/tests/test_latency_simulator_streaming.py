"""ai/latency_simulator.py --streaming 경로 단위 테스트."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai import latency_simulator as ls
from ai.schemas.accept import AcceptOutput
from ai.schemas.common import GeneratedStep
from ai.schemas.generate import GenerateOutput


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _async_gen(chunks: list, first_chunk_delay: float = 0.0):
    """fake chunks를 지연과 함께 yield하는 async generator."""
    import asyncio as _asyncio

    for i, c in enumerate(chunks):
        if i == 0 and first_chunk_delay > 0:
            await _asyncio.sleep(first_chunk_delay)
        yield c


def _mock_stream_services(first_chunk_delay: float = 0.0, total_chunks: int = 3):
    """스트리밍 경로용 mock 서비스 3종."""
    valid_generate = GenerateOutput(
        generated_steps=[
            GeneratedStep(name="A", description="a"),
            GeneratedStep(name="B", description="b"),
            GeneratedStep(name="C", description="c"),
        ]
    )
    valid_judge = AcceptOutput(is_current_required_step_completed=True)

    step_gen = MagicMock()
    step_gen.generate_steps = AsyncMock(return_value=valid_generate)

    judge = MagicMock()
    judge.judge_required_step = AsyncMock(return_value=valid_judge)

    sp_gen = MagicMock()
    chunks_list = [f"chunk_{i}" for i in range(total_chunks)]
    sp_gen.generate_stream = MagicMock(
        side_effect=lambda _input: _async_gen(chunks_list, first_chunk_delay)
    )

    return step_gen, judge, sp_gen


def _mock_non_stream_services():
    """non-stream 경로용 mock 서비스 (test_latency_simulator_cli._mock_services 동일)."""
    from ai.schemas.common import (
        CommonMistake,
        DictionaryItem,
        MentoringContent,
        RecommendedMethod,
    )
    from ai.schemas.side_panel import SidePanelOutput

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
                CommonMistake(mistake="m", bad_example="b", good_example="g"),
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


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestParseArgsStreaming:
    def test_streaming_flag_true(self) -> None:
        args = ls._parse_args(["--streaming"])
        assert args.streaming is True

    def test_streaming_flag_default_false(self) -> None:
        args = ls._parse_args([])
        assert args.streaming is False


class TestTtftTtltCalculation:
    @pytest.mark.asyncio
    async def test_first_chunk_delay_measured_as_ttft(self) -> None:
        """첫 번째 청크 지연이 TTFT로 측정되는지 검증."""
        sp_gen = MagicMock()
        sp_gen.generate_stream = MagicMock(
            side_effect=lambda _inp: _async_gen(["X", "Y"], first_chunk_delay=0.1)
        )

        fake_input = MagicMock()
        result = await ls._consume_stream("label_0", sp_gen, fake_input)

        assert result["label"] == "label_0"
        assert 0.08 <= result["ttft_s"] <= 0.3, f"ttft={result['ttft_s']}"
        assert result["ttlt_s"] >= result["ttft_s"]
        assert result["aggregated_text"] == "XY"


class TestStreamingArtifactSchema:
    def test_summary_has_streaming_fields(self, tmp_path: Path) -> None:
        """--streaming artifact가 schema 1.1 + 필수 필드를 갖는지 검증."""
        target = tmp_path / "stream_out.json"
        with patch.object(ls, "_build_services", return_value=_mock_stream_services()):
            exit_code = ls.main([
                "--streaming", "--output", str(target), "--runs", "2",
            ])

        assert exit_code == 0
        artifact = json.loads(target.read_text(encoding="utf-8"))

        assert artifact["schema_version"] == "1.1"
        assert artifact["mode"] == "streaming"

        summary = artifact["summary"]
        for key in ["ttft", "ttlt", "pipeline_ttft", "pipeline_ttlt"]:
            assert key in summary, f"missing key: {key}"
            assert "p50" in summary[key]
            assert "p100" in summary[key]

        for run in artifact["per_run"]:
            assert "side_panel_streams" in run
            assert len(run["side_panel_streams"]) == 3
            for stream in run["side_panel_streams"]:
                assert set(stream.keys()) == {"label", "ttft_s", "ttlt_s"}
            for key in ["stage_b_ttft_s", "stage_b_ttlt_s",
                        "pipeline_ttft_s", "pipeline_ttlt_s"]:
                assert key in run, f"missing run key: {key}"


class TestNonStreamingSchemaPreserved:
    def test_non_stream_artifact_has_no_mode_field_and_v1_schema(
        self, tmp_path: Path
    ) -> None:
        """non-stream artifact는 schema 1.0이고 mode 필드가 없어야 함."""
        target = tmp_path / "non_stream_out.json"
        with patch.object(ls, "_build_services", return_value=_mock_non_stream_services()):
            exit_code = ls.main(["--output", str(target), "--runs", "1"])

        assert exit_code == 0
        artifact = json.loads(target.read_text(encoding="utf-8"))

        assert artifact["schema_version"] == "1.0"
        assert "mode" not in artifact

        for run in artifact["per_run"]:
            for key in ["judge_s", "generate_s", "side_panel_s",
                        "stage_a_s", "stage_b_s", "pipeline_s"]:
                assert key in run, f"missing run key: {key}"
            for key in ["side_panel_streams", "stage_b_ttft_s", "pipeline_ttft_s"]:
                assert key not in run, f"unexpected streaming key: {key}"
