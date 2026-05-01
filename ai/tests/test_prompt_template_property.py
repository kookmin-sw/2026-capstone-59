"""hypothesis 기반 PromptTemplate property 테스트."""

import re

from hypothesis import given, settings
from hypothesis import strategies as st

from ai.prompts.template import PromptTemplate

# 유효한 Python 식별자 전략 (format_map 키로 사용 가능)
_identifier = st.from_regex(r"[a-z][a-z0-9_]{0,9}", fullmatch=True)
_value = st.text(min_size=1, max_size=30).filter(lambda s: "{" not in s and "}" not in s)


@settings(max_examples=100)
@given(
    prefix=st.text(max_size=20).filter(lambda s: "{" not in s and "}" not in s),
    suffix=st.text(max_size=20).filter(lambda s: "{" not in s and "}" not in s),
    var_items=st.lists(
        st.tuples(_identifier, _value),
        min_size=1,
        max_size=5,
    ),
)
def test_prompt_template_render_substitution_completeness(prefix, suffix, var_items):
    # 중복 키 제거 (마지막 값 우선)
    variables = dict(var_items)

    # {var_name} 플레이스홀더를 포함한 템플릿 구성
    placeholders = "".join(f"{{{name}}}" for name in variables)
    template = prefix + placeholders + suffix

    result = PromptTemplate.render(template, **variables)

    # 미치환 플레이스홀더가 남아있지 않아야 한다
    remaining = re.findall(r"\{[a-z][a-z0-9_]*\}", result)
    assert remaining == [], f"미치환 플레이스홀더 발견: {remaining}"

    # 모든 변수 값이 결과에 포함되어야 한다
    for value in variables.values():
        assert value in result, f"변수 값 '{value}'이 결과에 없음"
