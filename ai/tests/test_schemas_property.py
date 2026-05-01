"""hypothesis 기반 property 테스트."""

from hypothesis import given, settings
from hypothesis import strategies as st

from ai.schemas.common import (
    CommonMistake,
    DictionaryItem,
    GeneratedStep,
    MentoringContent,
    RecommendedMethod,
)
from ai.schemas.generate import GenerateOutput
from ai.schemas.side_panel import SidePanelOutput

_nonempty_text = st.text(min_size=1)

_generated_step_st = st.builds(
    GeneratedStep,
    name=_nonempty_text,
    description=_nonempty_text,
)

_recommended_method_st = st.builds(
    RecommendedMethod,
    title=_nonempty_text,
    content=_nonempty_text,
)

_common_mistake_st = st.builds(
    CommonMistake,
    mistake=_nonempty_text,
    bad_example=_nonempty_text,
    good_example=_nonempty_text,
)


# Property 4: generate 출력 구조 불변성
@settings(max_examples=100)
@given(
    steps=st.lists(_generated_step_st, min_size=3, max_size=3),
)
def test_generate_output_invariants(steps):
    output = GenerateOutput(generated_steps=steps)

    assert len(output.generated_steps) == 3
    for step in output.generated_steps:
        assert isinstance(step.name, str) and step.name
        assert isinstance(step.description, str) and step.description


_dictionary_item_st = st.builds(
    DictionaryItem,
    term=_nonempty_text,
    definition=_nonempty_text,
)


# Property 7: side_panel 출력 구조 완전성 (mentoring + dictionary 2탭 구조)
@settings(max_examples=100)
@given(
    description=_nonempty_text,
    recommended_methods=st.lists(_recommended_method_st, min_size=0, max_size=5),
    common_mistakes=st.lists(_common_mistake_st, min_size=0, max_size=5),
    one_line_tip=_nonempty_text,
    dictionary=st.lists(_dictionary_item_st, min_size=0, max_size=5),
)
def test_side_panel_output_completeness(
    description, recommended_methods, common_mistakes, one_line_tip, dictionary
):
    output = SidePanelOutput(
        mentoring=MentoringContent(
            description=description,
            recommended_methods=recommended_methods,
            common_mistakes=common_mistakes,
            one_line_tip=one_line_tip,
        ),
        dictionary=dictionary,
    )

    assert output.mentoring.description
    assert output.mentoring.one_line_tip

    for method in output.mentoring.recommended_methods:
        assert method.title
        assert method.content

    for mistake in output.mentoring.common_mistakes:
        assert mistake.mistake
        assert mistake.bad_example
        assert mistake.good_example

    for item in output.dictionary:
        assert item.term
        assert item.definition
