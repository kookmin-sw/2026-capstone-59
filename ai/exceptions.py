"""AI 모듈 커스텀 예외 및 에러 코드.

backend 의존성(FastAPI 등) 없이 독립 동작한다.
"""

from enum import Enum
from typing import Optional


class AIErrorCode(str, Enum):
    """AI 모듈 에러 코드."""

    AI_GENERATION_FAILED = "AI_GENERATION_FAILED"
    SCHEMA_VALIDATION_ERROR = "SCHEMA_VALIDATION_ERROR"
    RAG_SEARCH_FAILED = "RAG_SEARCH_FAILED"
    PROMPT_TEMPLATE_NOT_FOUND = "PROMPT_TEMPLATE_NOT_FOUND"
    BEDROCK_API_ERROR = "BEDROCK_API_ERROR"


class AIError(Exception):
    """AI 모듈 기반 예외 클래스."""

    def __init__(self, code: AIErrorCode, message: str, details: Optional[dict] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"[{code.value}] {message}")


class AIGenerationFailedError(AIError):
    """Claude 호출 실패 또는 재시도 초과."""

    def __init__(self, message: str = "AI 생성에 실패했습니다.", details: Optional[dict] = None):
        super().__init__(AIErrorCode.AI_GENERATION_FAILED, message, details)


class SchemaValidationError(AIError):
    """출력 스키마 불일치."""

    def __init__(self, message: str = "응답 스키마 검증에 실패했습니다.", details: Optional[dict] = None):
        super().__init__(AIErrorCode.SCHEMA_VALIDATION_ERROR, message, details)


class RAGSearchFailedError(AIError):
    """KB 검색 실패 (비치명적)."""

    def __init__(self, message: str = "RAG 검색에 실패했습니다.", details: Optional[dict] = None):
        super().__init__(AIErrorCode.RAG_SEARCH_FAILED, message, details)


class PromptTemplateNotFoundError(AIError):
    """프롬프트 파일 미존재."""

    def __init__(self, message: str = "프롬프트 템플릿을 찾을 수 없습니다.", details: Optional[dict] = None):
        super().__init__(AIErrorCode.PROMPT_TEMPLATE_NOT_FOUND, message, details)


class BedrockAPIError(AIError):
    """Bedrock API 레벨 에러 (throttling, timeout 등)."""

    def __init__(self, message: str = "Bedrock API 호출에 실패했습니다.", details: Optional[dict] = None):
        super().__init__(AIErrorCode.BEDROCK_API_ERROR, message, details)


class OutputViolatesTemplateError(AIError):
    """design-export 출력 .md 가 고정 템플릿 마커를 만족하지 않음.

    박제: Poco_Design_Export_Spec_v1.md v1.3 §5-2 (고정 템플릿 + AI 채움).
    SCHEMA_VALIDATION_ERROR 코드 재사용 (design.md §6-3 — 코드 폭발 방지).
    백엔드는 details["missing_marker"] 로 분기 가능.
    """

    def __init__(
        self,
        message: str = "출력이 고정 템플릿 마커를 만족하지 않습니다.",
        details: Optional[dict] = None,
    ):
        super().__init__(AIErrorCode.SCHEMA_VALIDATION_ERROR, message, details)


class OutputViolatesHonestyGuardError(AIError):
    """design-export 출력 .md 에 금지 표현이 등장함.

    박제: Poco_Design_Export_Spec_v1.md v1.3 §4-8 (표현 정직성).
    SCHEMA_VALIDATION_ERROR 코드 재사용 (design.md §6-3 — 코드 폭발 방지).
    백엔드는 details["banned_phrase"] 로 분기 가능.
    """

    def __init__(
        self,
        message: str = "출력이 표현 정직성 가드를 위반했습니다.",
        details: Optional[dict] = None,
    ):
        super().__init__(AIErrorCode.SCHEMA_VALIDATION_ERROR, message, details)
