"""ai/services/position_label.py 단위 테스트."""

import json
from pathlib import Path

import pytest

from ai.schemas.common import RequiredStepInfo
from ai.services.position_label import resolve_position_label


def _make_rs(name: str) -> RequiredStepInfo:
    return RequiredStepInfo(
        step_id="rs-test",
        name=name,
        is_completed=False,
        goal="목표",
        entry_criteria="진입 기준",
        fulfillment_criteria=["측면 1", "측면 2"],
        minimum_fulfillment_count=2,
    )


class TestPositionLabelStage1:
    def test_first_r_returns_project_starting(self):
        rs = _make_rs("문제/기회 정의")
        assert resolve_position_label(1, rs) == "프로젝트의 출발점"

    def test_last_r_returns_initial_closing(self):
        rs = _make_rs("실현 가능성 검토")
        assert resolve_position_label(1, rs) == "초기 단계의 마무리 지점"

    def test_middle_r_returns_initial_flow(self):
        rs = _make_rs("대상 사용자 파악")
        assert resolve_position_label(1, rs) == "초기 단계의 흐름 안"


class TestPositionLabelMiddleStages:
    @pytest.mark.parametrize("stage,first_r,natural", [
        (2, "일정 계획 수립", "기획 단계"),
        (3, "요구사항 도출", "요구사항 단계"),
        (4, "시스템 아키텍처 정의", "설계 단계"),
        (5, "개발 환경 구축", "개발 단계"),
    ])
    def test_first_r_returns_first_step(self, stage, first_r, natural):
        rs = _make_rs(first_r)
        assert resolve_position_label(stage, rs) == f"{natural}의 첫 걸음"

    @pytest.mark.parametrize("stage,last_r,natural", [
        (2, "개발 환경/도구 결정", "기획 단계"),
        (3, "요구사항 검토", "요구사항 단계"),
        (4, "설계 리뷰", "설계 단계"),
        (5, "코드 리뷰 및 자체 검증", "개발 단계"),
    ])
    def test_last_r_returns_closing(self, stage, last_r, natural):
        rs = _make_rs(last_r)
        assert resolve_position_label(stage, rs) == f"{natural}의 마무리 지점"


class TestPositionLabelStage6:
    def test_first_r_returns_verification_starting(self):
        rs = _make_rs("테스트 계획 수립")
        assert resolve_position_label(6, rs) == "검증의 출발점"

    def test_last_r_returns_final_gate(self):
        rs = _make_rs("최종 검토")
        assert resolve_position_label(6, rs) == "프로젝트의 마지막 관문"

    def test_middle_r_returns_verification_flow(self):
        rs = _make_rs("테스트 수행")
        assert resolve_position_label(6, rs) == "검증 단계의 흐름 안"


class TestPositionLabelEdgeCases:
    def test_none_required_step_returns_natural_position(self):
        assert resolve_position_label(2, None) == "기획 단계의 한 자리"

    def test_unknown_required_step_name_returns_flow(self):
        rs = _make_rs("존재하지 않는 R")
        assert resolve_position_label(3, rs) == "요구사항 단계의 흐름 안"

    def test_label_never_contains_stage_keyword(self):
        """모든 출력 라벨에 "Stage" 단어가 등장하지 않는지 검증."""
        rs = _make_rs("문제/기회 정의")
        for stage in range(1, 7):
            for r_name in [
                "문제/기회 정의", "대상 사용자 파악", "실현 가능성 검토",
                "일정 계획 수립", "최종 검토",
            ]:
                rs.name = r_name
                label = resolve_position_label(stage, rs)
                assert "Stage" not in label, f"Label '{label}' contains 'Stage'"
                assert "Step" not in label, f"Label '{label}' contains 'Step'"


class TestPositionLabelSourceSync:
    """names.json single source 동기화 검증."""

    def test_names_json_24_required_steps_all_resolve(self):
        names_path = (
            Path(__file__).parent.parent.parent
            / "content" / "required-steps" / "names.json"
        )
        with open(names_path, encoding="utf-8") as f:
            data = json.load(f)

        for entry in data["names"]:
            rs_id = entry["required_step_id"]  # "1-R1"
            stage = int(rs_id.split("-")[0])
            rs = _make_rs(entry["user_facing_name"])
            label = resolve_position_label(stage, rs)
            assert isinstance(label, str)
            assert len(label) > 0
            assert "Stage" not in label
            assert "Step" not in label
