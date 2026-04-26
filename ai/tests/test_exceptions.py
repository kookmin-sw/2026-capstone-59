"""ai/exceptions.py 단위 테스트."""

import pytest

from ai.exceptions import (
    AIError,
    AIErrorCode,
    AIGenerationFailedError,
    BedrockAPIError,
    PromptTemplateNotFoundError,
    RAGSearchFailedError,
    SchemaValidationError,
)


class TestAIErrorCode:
    """AIErrorCode enum 테스트."""

    def test_all_codes_exist(self):
        codes = {e.value for e in AIErrorCode}
        assert codes == {
            "AI_GENERATION_FAILED",
            "SCHEMA_VALIDATION_ERROR",
            "RAG_SEARCH_FAILED",
            "PROMPT_TEMPLATE_NOT_FOUND",
            "BEDROCK_API_ERROR",
        }

    def test_is_str_enum(self):
        assert isinstance(AIErrorCode.AI_GENERATION_FAILED, str)


class TestAIError:
    """AIError 기반 클래스 테스트."""

    def test_base_error_attributes(self):
        err = AIError(AIErrorCode.BEDROCK_API_ERROR, "test msg", {"key": "val"})
        assert err.code == AIErrorCode.BEDROCK_API_ERROR
        assert err.message == "test msg"
        assert err.details == {"key": "val"}
        assert "[BEDROCK_API_ERROR] test msg" in str(err)

    def test_details_default_empty_dict(self):
        err = AIError(AIErrorCode.RAG_SEARCH_FAILED, "msg")
        assert err.details == {}


class TestConcreteExceptions:
    """각 커스텀 예외 클래스 테스트."""

    @pytest.mark.parametrize(
        "exc_cls,expected_code",
        [
            (AIGenerationFailedError, AIErrorCode.AI_GENERATION_FAILED),
            (SchemaValidationError, AIErrorCode.SCHEMA_VALIDATION_ERROR),
            (RAGSearchFailedError, AIErrorCode.RAG_SEARCH_FAILED),
            (PromptTemplateNotFoundError, AIErrorCode.PROMPT_TEMPLATE_NOT_FOUND),
            (BedrockAPIError, AIErrorCode.BEDROCK_API_ERROR),
        ],
    )
    def test_default_message_and_code(self, exc_cls, expected_code):
        err = exc_cls()
        assert err.code == expected_code
        assert isinstance(err, AIError)
        assert err.message  # non-empty default message

    def test_custom_message_and_details(self):
        err = BedrockAPIError("timeout occurred", details={"model_id": "claude-3"})
        assert err.message == "timeout occurred"
        assert err.details["model_id"] == "claude-3"

    def test_exceptions_are_catchable_as_base(self):
        with pytest.raises(AIError):
            raise SchemaValidationError("bad schema")
