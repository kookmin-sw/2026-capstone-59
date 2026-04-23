class PocoError(Exception):
    """Poco 도메인 예외 기반 클래스."""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class BadRequestError(PocoError):
    def __init__(self, message: str = "잘못된 요청 파라미터입니다."):
        super().__init__(code="BAD_REQUEST", message=message)


class NotFoundError(PocoError):
    def __init__(self, message: str = "리소스를 찾을 수 없습니다."):
        super().__init__(code="NOT_FOUND", message=message)


class InvalidStateError(PocoError):
    def __init__(self, message: str = "현재 상태에서 허용되지 않는 작업입니다."):
        super().__init__(code="INVALID_STATE_TRANSITION", message=message)


class StageCompletionBlockedError(PocoError):
    def __init__(self, message: str = "모든 필수 Step을 완료해야 Stage를 넘어갈 수 있습니다.", details: dict | None = None):
        super().__init__(code="STAGE_COMPLETION_BLOCKED", message=message)
        self.details = details or {}


class ValidationError(PocoError):
    def __init__(self, message: str = "입력값이 올바르지 않습니다."):
        super().__init__(code="VALIDATION_ERROR", message=message)


class InternalError(PocoError):
    def __init__(self, message: str = "서버 내부 오류가 발생했습니다."):
        super().__init__(code="INTERNAL_ERROR", message=message)


class AIServiceUnavailableError(PocoError):
    def __init__(self, message: str = "AI 서비스에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요."):
        super().__init__(code="AI_SERVICE_UNAVAILABLE", message=message)


class NotionServiceUnavailableError(PocoError):
    def __init__(self, message: str = "Notion 템플릿 생성에 실패했습니다. 잠시 후 다시 시도해주세요."):
        super().__init__(code="NOTION_SERVICE_UNAVAILABLE", message=message)
