"""ai/schemas/ 단위 테스트."""

import pytest
from pydantic import ValidationError

from ai.schemas.accept import AcceptInput, AcceptOutput
from ai.schemas.common import (
    CommonMistake,
    DecisionHistoryItem,
    DictionaryItem,
    GeneratedStep,
    MentoringContent,
    ProjectInfo,
    RecommendedMethod,
    RequiredStepInfo,
    RequiredStepStatus,
    RetrievedChunk,
    StageInfo,
    StepInfo,
)
from ai.schemas.generate import GenerateInput, GenerateOutput
from ai.schemas.side_panel import SidePanelInput, SidePanelOutput

# ---------------------------------------------------------------------------
# Fixtures — 재사용 가능한 최소 유효 데이터
# ---------------------------------------------------------------------------

PROJECT_INFO = {
    "project_id": "proj-1",
    "duration_months": 6,
    "member_count": 4,
    "initial_prompt": "쇼핑몰 개발",
}

STAGE_INFO = {
    "stage_id": "stage-1",
    "stage_sequence": 1,
    "name": "요구사항 분석",
}

STEP_INFO = {"step_id": "step-1", "name": "요구사항 수집"}

REQUIRED_STEP_INFO = {
    "step_id": "rs-1",
    "name": "기능 명세 작성",
    "is_completed": False,
    "goal": "기능 명세 완성",
    "entry_criteria": "프로젝트 킥오프 완료",
    "fulfillment_criteria": ["측면A", "측면B", "측면C"],
    "minimum_fulfillment_count": 2,
}

GENERATED_STEP = {"name": "설계 단계", "description": "시스템 설계를 수행한다"}


# ---------------------------------------------------------------------------
# common.py
# ---------------------------------------------------------------------------


class TestProjectInfo:
    def test_valid(self):
        m = ProjectInfo(**PROJECT_INFO)
        assert m.project_id == "proj-1"
        assert m.name is None

    def test_optional_fields_accepted(self):
        m = ProjectInfo(**PROJECT_INFO, name="Poco", description="설명", constraints=["제약"])
        assert m.name == "Poco"

    @pytest.mark.parametrize("missing", ["project_id", "duration_months", "member_count", "initial_prompt"])
    def test_missing_required_field(self, missing):
        data = {k: v for k, v in PROJECT_INFO.items() if k != missing}
        with pytest.raises(ValidationError):
            ProjectInfo(**data)


class TestStageInfo:
    def test_valid(self):
        m = StageInfo(**STAGE_INFO)
        assert m.stage_sequence == 1

    @pytest.mark.parametrize("missing", ["stage_id", "stage_sequence", "name"])
    def test_missing_required_field(self, missing):
        data = {k: v for k, v in STAGE_INFO.items() if k != missing}
        with pytest.raises(ValidationError):
            StageInfo(**data)


class TestStepInfo:
    def test_valid(self):
        m = StepInfo(**STEP_INFO)
        assert m.step_id == "step-1"

    @pytest.mark.parametrize("missing", ["step_id", "name"])
    def test_missing_required_field(self, missing):
        data = {k: v for k, v in STEP_INFO.items() if k != missing}
        with pytest.raises(ValidationError):
            StepInfo(**data)


class TestDecisionHistoryItem:
    def test_valid(self):
        m = DecisionHistoryItem(step_id="s1", name="분석", status="accepted")
        assert m.stage_sequence is None

    def test_missing_status(self):
        with pytest.raises(ValidationError):
            DecisionHistoryItem(step_id="s1", name="분석")


class TestRequiredStepInfo:
    def test_valid(self):
        m = RequiredStepInfo(**REQUIRED_STEP_INFO)
        assert len(m.fulfillment_criteria) == 3
        assert m.minimum_fulfillment_count == 2

    @pytest.mark.parametrize(
        "missing",
        ["step_id", "name", "is_completed", "goal", "entry_criteria", "fulfillment_criteria", "minimum_fulfillment_count"],
    )
    def test_missing_required_field(self, missing):
        data = {k: v for k, v in REQUIRED_STEP_INFO.items() if k != missing}
        with pytest.raises(ValidationError):
            RequiredStepInfo(**data)


class TestRequiredStepStatus:
    def test_valid(self):
        m = RequiredStepStatus(name="기능 명세", order=1, is_completed=False)
        assert m.order == 1

    def test_missing_order(self):
        with pytest.raises(ValidationError):
            RequiredStepStatus(name="기능 명세", is_completed=True)


class TestGeneratedStep:
    def test_valid(self):
        m = GeneratedStep(**GENERATED_STEP)
        assert m.name == "설계 단계"

    @pytest.mark.parametrize("missing", ["name", "description"])
    def test_missing_required_field(self, missing):
        data = {k: v for k, v in GENERATED_STEP.items() if k != missing}
        with pytest.raises(ValidationError):
            GeneratedStep(**data)


class TestRecommendedMethod:
    def test_valid(self):
        m = RecommendedMethod(title="방법1", content="내용1")
        assert m.title == "방법1"

    def test_missing_content(self):
        with pytest.raises(ValidationError):
            RecommendedMethod(title="방법1")


class TestCommonMistake:
    def test_valid(self):
        m = CommonMistake(mistake="실수", bad_example="나쁜 예", good_example="좋은 예")
        assert m.good_example == "좋은 예"

    @pytest.mark.parametrize("missing", ["mistake", "bad_example", "good_example"])
    def test_missing_required_field(self, missing):
        data = {"mistake": "실수", "bad_example": "나쁜 예", "good_example": "좋은 예"}
        data.pop(missing)
        with pytest.raises(ValidationError):
            CommonMistake(**data)


class TestRetrievedChunk:
    def test_valid(self):
        m = RetrievedChunk(text="청크 내용", relevance_score=0.95)
        assert m.relevance_score == pytest.approx(0.95)

    def test_missing_relevance_score(self):
        with pytest.raises(ValidationError):
            RetrievedChunk(text="청크 내용")


# ---------------------------------------------------------------------------
# generate.py
# ---------------------------------------------------------------------------


class TestGenerateInput:
    def _base(self, **kwargs):
        return {
            "project_info": PROJECT_INFO,
            "current_stage": STAGE_INFO,
            "decision_history": [],
            "current_step": STEP_INFO,
            **kwargs,
        }

    def test_valid_minimal(self):
        m = GenerateInput(**self._base())
        assert m.current_required_step is None
        assert m.rag_context is None

    def test_valid_full(self):
        m = GenerateInput(
            **self._base(
                current_required_step=REQUIRED_STEP_INFO,
                rag_context={"chunks": []},
            )
        )
        assert m.current_required_step is not None

    @pytest.mark.parametrize("missing", ["project_info", "current_stage", "decision_history", "current_step"])
    def test_missing_required_field(self, missing):
        data = {k: v for k, v in self._base().items() if k != missing}
        with pytest.raises(ValidationError):
            GenerateInput(**data)


class TestGenerateOutput:
    def _three_steps(self):
        return [GENERATED_STEP] * 3

    def test_valid_exactly_three(self):
        m = GenerateOutput(generated_steps=self._three_steps())
        assert len(m.generated_steps) == 3

    def test_zero_steps_raises(self):
        with pytest.raises(ValidationError, match="exactly 3"):
            GenerateOutput(generated_steps=[])

    def test_two_steps_raises(self):
        with pytest.raises(ValidationError, match="exactly 3"):
            GenerateOutput(generated_steps=[GENERATED_STEP, GENERATED_STEP])

    def test_four_steps_raises(self):
        with pytest.raises(ValidationError, match="exactly 3"):
            GenerateOutput(generated_steps=[GENERATED_STEP] * 4)

    def test_missing_generated_steps(self):
        with pytest.raises(ValidationError):
            GenerateOutput()

    def test_steps_are_generated_step_instances(self):
        m = GenerateOutput(generated_steps=self._three_steps())
        assert all(isinstance(s, GeneratedStep) for s in m.generated_steps)


# ---------------------------------------------------------------------------
# accept.py
# ---------------------------------------------------------------------------


class TestAcceptInput:
    def _base(self, **kwargs):
        return {
            "project_info": PROJECT_INFO,
            "current_stage": STAGE_INFO,
            "required_steps_status": [],
            "accepted_steps_in_required": [],
            "accepted_step": STEP_INFO,
            **kwargs,
        }

    def test_valid_minimal(self):
        m = AcceptInput(**self._base())
        assert m.current_required_step is None

    def test_valid_full(self):
        m = AcceptInput(
            **self._base(
                current_required_step=REQUIRED_STEP_INFO,
                rag_context={"docs": []},
            )
        )
        assert m.current_required_step.step_id == "rs-1"

    @pytest.mark.parametrize(
        "missing",
        ["project_info", "current_stage", "required_steps_status", "accepted_steps_in_required", "accepted_step"],
    )
    def test_missing_required_field(self, missing):
        data = {k: v for k, v in self._base().items() if k != missing}
        with pytest.raises(ValidationError):
            AcceptInput(**data)


class TestAcceptOutput:
    def test_true(self):
        m = AcceptOutput(is_current_required_step_completed=True)
        assert m.is_current_required_step_completed is True

    def test_false(self):
        m = AcceptOutput(is_current_required_step_completed=False)
        assert m.is_current_required_step_completed is False

    def test_missing_field(self):
        with pytest.raises(ValidationError):
            AcceptOutput()

    @pytest.mark.parametrize("truthy_str", ["true", "1", "yes"])
    def test_coercion_from_truthy_string(self, truthy_str):
        # Pydantic v2는 "true"/"1" 등을 bool로 강제 변환한다
        m = AcceptOutput(is_current_required_step_completed=truthy_str)
        assert m.is_current_required_step_completed is True

    @pytest.mark.parametrize("falsy_str", ["false", "0", "no"])
    def test_coercion_from_falsy_string(self, falsy_str):
        m = AcceptOutput(is_current_required_step_completed=falsy_str)
        assert m.is_current_required_step_completed is False

    def test_non_coercible_string_raises(self):
        with pytest.raises(ValidationError):
            AcceptOutput(is_current_required_step_completed="maybe")

    def test_none_raises(self):
        with pytest.raises(ValidationError):
            AcceptOutput(is_current_required_step_completed=None)

    def test_integer_one_coerced_to_true(self):
        m = AcceptOutput(is_current_required_step_completed=1)
        assert m.is_current_required_step_completed is True

    def test_integer_zero_coerced_to_false(self):
        m = AcceptOutput(is_current_required_step_completed=0)
        assert m.is_current_required_step_completed is False


# ---------------------------------------------------------------------------
# side_panel.py
# ---------------------------------------------------------------------------


class TestSidePanelInput:
    def _base(self, **kwargs):
        return {
            "project_info": PROJECT_INFO,
            "current_stage": STAGE_INFO,
            "target_step": STEP_INFO,
            "decision_history": [],
            **kwargs,
        }

    def test_valid_minimal(self):
        m = SidePanelInput(**self._base())
        assert m.current_required_step is None
        assert m.rag_context is None

    def test_valid_full(self):
        m = SidePanelInput(
            **self._base(
                current_required_step=REQUIRED_STEP_INFO,
                rag_context={"key": "val"},
            )
        )
        assert m.rag_context == {"key": "val"}

    @pytest.mark.parametrize(
        "missing", ["project_info", "current_stage", "target_step", "decision_history"]
    )
    def test_missing_required_field(self, missing):
        data = {k: v for k, v in self._base().items() if k != missing}
        with pytest.raises(ValidationError):
            SidePanelInput(**data)


class TestSidePanelOutput:
    def _valid_mentoring(self):
        return {
            "description": "단계 설명",
            "recommended_methods": [{"title": "방법1", "content": "내용1"}],
            "common_mistakes": [
                {"mistake": "실수1", "bad_example": "나쁜 예", "good_example": "좋은 예"}
            ],
            "one_line_tip": "팁입니다",
        }

    def _valid_dictionary(self):
        return [
            {"term": "페르소나", "definition": "타겟 사용자를 대표하는 가상의 인물 모델"},
            {"term": "MVP", "definition": "최소 기능만 갖춘 초기 제품"},
        ]

    def _valid(self):
        return {
            "mentoring": self._valid_mentoring(),
            "dictionary": self._valid_dictionary(),
        }

    def test_valid(self):
        m = SidePanelOutput(**self._valid())
        assert m.mentoring.one_line_tip == "팁입니다"
        assert len(m.mentoring.recommended_methods) == 1
        assert len(m.mentoring.common_mistakes) == 1
        assert len(m.dictionary) == 2
        assert m.dictionary[0].term == "페르소나"

    def test_empty_lists_accepted(self):
        data = self._valid()
        data["mentoring"]["recommended_methods"] = []
        data["mentoring"]["common_mistakes"] = []
        data["dictionary"] = []
        m = SidePanelOutput(**data)
        assert m.mentoring.recommended_methods == []
        assert m.dictionary == []

    @pytest.mark.parametrize("missing", ["mentoring", "dictionary"])
    def test_missing_top_level_field(self, missing):
        data = {k: v for k, v in self._valid().items() if k != missing}
        with pytest.raises(ValidationError):
            SidePanelOutput(**data)

    @pytest.mark.parametrize(
        "missing", ["description", "recommended_methods", "common_mistakes", "one_line_tip"]
    )
    def test_missing_mentoring_field(self, missing):
        data = self._valid()
        data["mentoring"] = {k: v for k, v in data["mentoring"].items() if k != missing}
        with pytest.raises(ValidationError):
            SidePanelOutput(**data)

    @pytest.mark.parametrize("missing", ["term", "definition"])
    def test_missing_dictionary_item_field(self, missing):
        data = self._valid()
        data["dictionary"] = [
            {k: v for k, v in data["dictionary"][0].items() if k != missing}
        ]
        with pytest.raises(ValidationError):
            SidePanelOutput(**data)


class TestMentoringContent:
    def _valid(self):
        return {
            "description": "설명",
            "recommended_methods": [{"title": "T", "content": "C"}],
            "common_mistakes": [
                {"mistake": "m", "bad_example": "b", "good_example": "g"}
            ],
            "one_line_tip": "팁",
        }

    def test_valid(self):
        m = MentoringContent(**self._valid())
        assert m.one_line_tip == "팁"

    @pytest.mark.parametrize(
        "missing", ["description", "recommended_methods", "common_mistakes", "one_line_tip"]
    )
    def test_missing_required_field(self, missing):
        data = {k: v for k, v in self._valid().items() if k != missing}
        with pytest.raises(ValidationError):
            MentoringContent(**data)


class TestDictionaryItem:
    def test_valid(self):
        item = DictionaryItem(term="페르소나", definition="타겟 사용자 모델")
        assert item.term == "페르소나"
        assert item.definition == "타겟 사용자 모델"

    @pytest.mark.parametrize("missing", ["term", "definition"])
    def test_missing_required_field(self, missing):
        data = {"term": "T", "definition": "D"}
        del data[missing]
        with pytest.raises(ValidationError):
            DictionaryItem(**data)
