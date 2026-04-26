"""AI 모듈 커스텀 예외 및 에러 코드.

backend 의존성(FastAPI 등) 없이 독립 동작한다.
"""

from enum import Enum


class AIErrorCode(str, Enum):
    """AI 모듈 에러 코드."""

    AI_GENERATION_FAILED = "AI_GENERATION_FAILED"
    SCHEMA_VALIDATION_ERROR = "SCHEMA_VALIDATION_ERROR"
    RAG_SEARCH_FAILED = "RAG_SEARCH_FAILED"
    PROMPT_TEMPLATE_NOT_FOUND = "PROMPT_TEMPLATE_NOT_FOUND"
    BEDROCK_API_ERROR = "BEDROCK_API_ERROR"


class AIError(Exception):
    """AI 모듈 기반 예외 클래스."""

    def __init__(self, code: AIErrorCode, message: str, details: dict | None = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"[{code.value}] {message}")


class AIGenerationFailedError(AIError):
    """Claude 호출 실패 또는 재시도 초과."""

    def __init__(self, message: str = "AI 생성에 실패했습니다.", details: dict | None = None):
        super().__init__(AIErrorCode.AI_GENERATION_FAILED, message, details)


class SchemaValidationError(AIError):
    """출력 스키마 불일치."""

    def __init__(self, message: str = "응답 스키마 검증에 실패했습니다.", details: dict | None = None):
        super().__init__(AIErrorCode.SCHEMA_VALIDATION_ERROR, message, details)


class RAGSearchFailedError(AIError):
    """KB 검색 실패 (비치명적)."""

    def __init__(self, message: str = "RAG 검색에 실패했습니다.", details: dict | None = None):
        super().__init__(AIErrorCode.RAG_SEARCH_FAILED, message, details)


class PromptTemplateNotFoundError(AIError):
    """프롬프트 파일 미존재."""

    def __init__(self, message: str = "프롬프트 템플릿을 찾을 수 없습니다.", details: dict | None = None):
        super().__init__(AIErrorCode.PROMPT_TEMPLATE_NOT_FOUND, message, details)


class BedrockAPIError(AIError):
    """Bedrock API 레벨 에러 (throttling, timeout 등)."""

    def __init__(self, message: str = "Bedrock API 호출에 실패했습니다.", details: dict | None = None):
        super().__init__(AIErrorCode.BEDROCK_API_ERROR, message, details)
