"""ai/prompts/template.py 단위 테스트."""

import pytest

from ai.exceptions import PromptTemplateNotFoundError
from ai.prompts.template import PromptTemplate


class TestPromptTemplateLoad:
    """load() 메서드 테스트."""

    def test_load_existing_template(self):
        """존재하는 템플릿 파일 로드 성공."""
        content = PromptTemplate.load("generate")
        assert isinstance(content, str)

    def test_load_all_scenarios(self):
        """3개 시나리오 모두 로드 가능."""
        for scenario in ("generate", "accept", "side_panel"):
            content = PromptTemplate.load(scenario)
            assert isinstance(content, str)

    def test_load_nonexistent_raises(self):
        """존재하지 않는 파일 → PromptTemplateNotFoundError."""
        with pytest.raises(PromptTemplateNotFoundError) as exc_info:
            PromptTemplate.load("nonexistent")
        assert "nonexistent.txt" in str(exc_info.value)
        assert exc_info.value.details["scenario"] == "nonexistent"


class TestPromptTemplateRender:
    """render() 메서드 테스트."""

    def test_basic_substitution(self):
        """기본 변수 치환."""
        template = "프로젝트: {project_name}, Stage: {stage_name}"
        result = PromptTemplate.render(
            template, project_name="Poco", stage_name="아이디어 구체화"
        )
        assert result == "프로젝트: Poco, Stage: 아이디어 구체화"

    def test_missing_variable_preserved(self):
        """제공되지 않은 변수는 원본 플레이스홀더 유지."""
        template = "이름: {name}, 설명: {description}"
        result = PromptTemplate.render(template, name="Poco")
        assert result == "이름: Poco, 설명: {description}"

    def test_no_variables(self):
        """변수 없는 템플릿은 그대로 반환."""
        template = "변수 없는 텍스트입니다."
        result = PromptTemplate.render(template)
        assert result == "변수 없는 텍스트입니다."

    def test_empty_template(self):
        """빈 템플릿."""
        result = PromptTemplate.render("")
        assert result == ""

    def test_multiple_same_variable(self):
        """같은 변수가 여러 번 등장."""
        template = "{name}은 {name}입니다."
        result = PromptTemplate.render(template, name="Poco")
        assert result == "Poco은 Poco입니다."


class TestPromptTemplateLoadAndRender:
    """load_and_render() 편의 메서드 테스트."""

    def test_load_and_render(self):
        """로드 + 렌더 한 번에."""
        result = PromptTemplate.load_and_render("generate")
        assert isinstance(result, str)

    def test_load_and_render_nonexistent(self):
        """존재하지 않는 파일 → PromptTemplateNotFoundError."""
        with pytest.raises(PromptTemplateNotFoundError):
            PromptTemplate.load_and_render("nonexistent")
