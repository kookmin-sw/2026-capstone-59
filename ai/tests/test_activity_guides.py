"""ai/prompts/activity_guides.py 단위 테스트."""

import json
import logging

import pytest

from ai.prompts.activity_guides import (
    ACTIVITY_GUIDES,
    _FREE_MODE_GUIDE,
    resolve_activity_guide,
)
from ai.schemas.common import RequiredStepInfo


# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------

_ALL_REQUIRED_STEP_NAMES = list(ACTIVITY_GUIDES.keys())

_FAKE_REQUIRED_STEP_BASE = dict(
    step_id="rs-1",
    is_completed=False,
    goal="목표",
    entry_criteria="진입 기준",
    fulfillment_criteria=["측면 1", "측면 2"],
    minimum_fulfillment_count=2,
)


def _make_required_step(name: str) -> RequiredStepInfo:
    return RequiredStepInfo(name=name, **_FAKE_REQUIRED_STEP_BASE)


# ---------------------------------------------------------------------------
# 자유 생성 모드 (current_required_step=None)
# ---------------------------------------------------------------------------


class TestFreeModeGuide:
    def test_none_returns_free_mode_string(self):
        result = resolve_activity_guide(None)
        assert result == _FREE_MODE_GUIDE

    def test_free_mode_string_contains_자유_생성_모드(self):
        result = resolve_activity_guide(None)
        assert "자유 생성 모드" in result


# ---------------------------------------------------------------------------
# 24개 R 키 lookup
# ---------------------------------------------------------------------------


class TestKnownKeyLookup:
    @pytest.mark.parametrize("name", _ALL_REQUIRED_STEP_NAMES)
    def test_all_24_keys_return_non_empty_guide(self, name: str):
        result = resolve_activity_guide(_make_required_step(name))
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.parametrize("name", _ALL_REQUIRED_STEP_NAMES)
    def test_returned_guide_is_not_free_mode(self, name: str):
        result = resolve_activity_guide(_make_required_step(name))
        assert result != _FREE_MODE_GUIDE

    def test_대상_사용자_파악_guide_contains_페르소나(self):
        result = resolve_activity_guide(_make_required_step("대상 사용자 파악"))
        assert "페르소나" in result

    def test_실현_가능성_검토_guide_contains_기술_스택(self):
        result = resolve_activity_guide(_make_required_step("실현 가능성 검토"))
        assert "기술" in result

    def test_guide_contains_good_and_bad_examples(self):
        result = resolve_activity_guide(_make_required_step("문제/기회 정의"))
        assert "좋은 예" in result
        assert "나쁜 예" in result


# ---------------------------------------------------------------------------
# 미등록 키 — 폴백 + 경고 로그
# ---------------------------------------------------------------------------


class TestUnknownKeyFallback:
    def test_unknown_name_returns_free_mode_guide(self):
        result = resolve_activity_guide(_make_required_step("존재하지 않는 Step"))
        assert result == _FREE_MODE_GUIDE

    def test_unknown_name_emits_warning_log(self, caplog):
        with caplog.at_level(logging.WARNING, logger="ai.prompts.activity_guides"):
            resolve_activity_guide(_make_required_step("가짜 Step 이름"))

        assert any("activity_guide_lookup_miss" in r.message for r in caplog.records)

    def test_warning_log_contains_step_name(self, caplog):
        fake_name = "완전히 없는 Step"
        with caplog.at_level(logging.WARNING, logger="ai.prompts.activity_guides"):
            resolve_activity_guide(_make_required_step(fake_name))

        log_json = next(
            (r.message for r in caplog.records if "activity_guide_lookup_miss" in r.message),
            None,
        )
        assert log_json is not None
        payload = json.loads(log_json)
        assert payload["name"] == fake_name


# ---------------------------------------------------------------------------
# ACTIVITY_GUIDES dict 구조 검증
# ---------------------------------------------------------------------------


class TestActivityGuidesDict:
    def test_contains_exactly_24_entries(self):
        assert len(ACTIVITY_GUIDES) == 24

    def test_all_values_are_strings(self):
        for key, value in ACTIVITY_GUIDES.items():
            assert isinstance(value, str), f"{key}: value is not str"

    def test_stage1_all_four_r_present(self):
        for name in ["문제/기회 정의", "대상 사용자 파악", "핵심 컨셉 정의", "실현 가능성 검토"]:
            assert name in ACTIVITY_GUIDES

    def test_stage2_all_four_r_present(self):
        for name in ["일정 계획 수립", "역할 분담", "위험 식별", "개발 환경/도구 결정"]:
            assert name in ACTIVITY_GUIDES

    def test_stage6_all_four_r_present(self):
        for name in ["테스트 계획 수립", "테스트 수행", "결과 분석 및 결함 기록", "수용 테스트/최종 검토"]:
            assert name in ACTIVITY_GUIDES
