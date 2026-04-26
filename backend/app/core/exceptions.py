from fastapi import status as http_status


class PocoError(Exception):
    """Poco 도메인 예외 기반 클래스."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = http_status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class InvalidInputError(PocoError):
    def __init__(self, message: str = "요청 파라미터 형식이 올바르지 않습니다."):
        super().__init__(
            code="INVALID_INPUT",
            message=message,
            status_code=http_status.HTTP_400_BAD_REQUEST,
        )


class DuplicateProjectNameError(PocoError):
    def __init__(self, message: str = "이미 존재하는 프로젝트 이름입니다."):
        super().__init__(
            code="DUPLICATE_PROJECT_NAME",
            message=message,
            status_code=http_status.HTTP_409_CONFLICT,
        )


class StepAlreadyAcceptedError(PocoError):
    def __init__(self, message: str = "이미 Accept된 Step입니다."):
        super().__init__(
            code="STEP_ALREADY_ACCEPTED",
            message=message,
            status_code=http_status.HTTP_409_CONFLICT,
        )


class InvalidRollbackTargetError(PocoError):
    def __init__(self, message: str = "롤백할 수 없는 대상입니다."):
        super().__init__(
            code="INVALID_ROLLBACK_TARGET",
            message=message,
            status_code=http_status.HTTP_400_BAD_REQUEST,
        )


class ProjectNotFoundError(PocoError):
    def __init__(self, message: str = "프로젝트를 찾을 수 없습니다."):
        super().__init__(
            code="PROJECT_NOT_FOUND",
            message=message,
            status_code=http_status.HTTP_404_NOT_FOUND,
        )


class StageNotFoundError(PocoError):
    def __init__(self, message: str = "Stage를 찾을 수 없습니다."):
        super().__init__(
            code="STAGE_NOT_FOUND",
            message=message,
            status_code=http_status.HTTP_404_NOT_FOUND,
        )


class StepNotFoundError(PocoError):
    def __init__(self, message: str = "Step을 찾을 수 없습니다."):
        super().__init__(
            code="STEP_NOT_FOUND",
            message=message,
            status_code=http_status.HTTP_404_NOT_FOUND,
        )


class ProjectNotInitializedError(PocoError):
    def __init__(self, message: str = "초기화되지 않은 프로젝트입니다."):
        super().__init__(
            code="PROJECT_NOT_INITIALIZED",
            message=message,
            status_code=http_status.HTTP_400_BAD_REQUEST,
        )


class StepGenerationLimitError(PocoError):
    def __init__(self, message: str = "Step 추가생성 횟수를 초과했습니다. (최대 6개)"):
        super().__init__(
            code="STEP_GENERATION_LIMIT",
            message=message,
            status_code=http_status.HTTP_400_BAD_REQUEST,
        )


class AIGenerationFailedError(PocoError):
    def __init__(self, message: str = "AI Step 생성에 실패했습니다."):
        super().__init__(
            code="AI_GENERATION_FAILED",
            message=message,
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class NotionAPIFailedError(PocoError):
    def __init__(self, message: str = "Notion 템플릿 생성에 실패했습니다."):
        super().__init__(
            code="NOTION_API_FAILED",
            message=message,
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class OAuthAuthorizationError(PocoError):
    def __init__(self, message: str = "OAuth 인증에 실패했습니다."):
        super().__init__(
            code="OAUTH_AUTHORIZATION_FAILED",
            message=message,
            status_code=http_status.HTTP_400_BAD_REQUEST,
        )


class UnsupportedOAuthProviderError(PocoError):
    def __init__(self, message: str = "지원하지 않는 OAuth Provider입니다."):
        super().__init__(
            code="UNSUPPORTED_OAUTH_PROVIDER",
            message=message,
            status_code=http_status.HTTP_400_BAD_REQUEST,
        )


class InvalidTokenError(PocoError):
    def __init__(self, message: str = "유효하지 않은 토큰입니다."):
        super().__init__(
            code="INVALID_TOKEN",
            message=message,
            status_code=http_status.HTTP_401_UNAUTHORIZED,
        )


class UserNotFoundError(PocoError):
    def __init__(self, message: str = "사용자를 찾을 수 없습니다."):
        super().__init__(
            code="USER_NOT_FOUND",
            message=message,
            status_code=http_status.HTTP_404_NOT_FOUND,
        )
