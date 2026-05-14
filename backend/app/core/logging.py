"""중앙 로깅 설정.

Lambda + CloudWatch 환경을 기본 가정. 앱 진입점(main.py)에서
`setup_logging()`을 1회 호출하고, 각 모듈은 `get_logger(__name__)`로
로거를 획득해 사용한다.

사용 예:
    from app.core.logging import get_logger

    logger = get_logger(__name__)
    logger.info("step accepted", extra={"step_id": str(step_id)})
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from app.core.config import settings

# logging.LogRecord 의 표준 attribute 목록 — extra 식별용
# (asctime 은 Formatter.format() 호출 시 동적으로 추가되므로 함께 포함)
_RESERVED_LOGRECORD_ATTRS = {
    "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
    "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
    "created", "msecs", "relativeCreated", "thread", "threadName",
    "processName", "process", "message", "taskName", "asctime",
}


def _collect_extras(record: logging.LogRecord) -> dict[str, Any]:
    """LogRecord에서 사용자가 `extra=`로 넣은 필드만 추출."""
    return {
        k: v
        for k, v in record.__dict__.items()
        if k not in _RESERVED_LOGRECORD_ATTRS and not k.startswith("_")
    }


class JsonFormatter(logging.Formatter):
    """CloudWatch 가독성을 위한 JSON 포맷터."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        # 사용자가 logger.info(..., extra={...})로 넣은 추가 필드 병합
        payload.update(_collect_extras(record))

        return json.dumps(payload, ensure_ascii=False, default=str)


class NoisyLoggerFilter(logging.Filter):
    """외부 라이브러리의 DEBUG/INFO 로그를 핸들러 단에서 차단.

    logger.setLevel(WARNING)만으로는 라이브러리가 자체적으로 레벨을 재설정하는
    경우(httpcore 등) 우회될 수 있어, 출력 직전에 한 번 더 필터링한다.
    WARNING 이상은 통과시킨다.
    """

    NOISY_PREFIXES = (
        "httpcore",
        "httpx",
        "botocore",
        "boto3",
        "urllib3",
        "s3transfer",
        "uvicorn.access",
        "asyncio",
    )

    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelno >= logging.WARNING:
            return True
        for prefix in self.NOISY_PREFIXES:
            if record.name == prefix or record.name.startswith(prefix + "."):
                return False
        return True


class TextFormatter(logging.Formatter):
    """로컬 개발용 텍스트 포맷터. extra 필드를 메시지 뒤에 `key=value` 로 출력."""

    def __init__(self) -> None:
        super().__init__(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        extras = _collect_extras(record)
        if extras:
            extras_str = " ".join(f"{k}={v}" for k, v in extras.items())
            base = f"{base} | {extras_str}"
        return base


def setup_logging() -> None:
    """루트 로거 초기화. 앱 진입점에서 1회 호출."""
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)

    # Lambda 환경에서 AWS가 미리 추가한 핸들러 제거 (중복 출력 방지)
    for h in root.handlers[:]:
        root.removeHandler(h)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.addFilter(NoisyLoggerFilter())

    if settings.LOG_FORMAT.lower() == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(TextFormatter())

    root.addHandler(handler)

    # 1차 방어선: logger 단에서도 레벨 조정 (라이브러리가 재설정해도 핸들러 필터가 막음)
    for noisy in NoisyLoggerFilter.NOISY_PREFIXES:
        logging.getLogger(noisy).setLevel(logging.WARNING)


class _SafeLogger(logging.LoggerAdapter):
    """`extra` 키가 LogRecord 표준 속성과 충돌하면 자동으로 prefix 를 붙여
    `KeyError: "Attempt to overwrite ... in LogRecord"` 예외를 방지한다.

    예: extra={"name": "foo"} → 실제로는 extra={"extra_name": "foo"} 로 전달.
    """

    def process(self, msg, kwargs):
        extra = kwargs.get("extra")
        if extra:
            safe: dict[str, Any] = {}
            for k, v in extra.items():
                if k in _RESERVED_LOGRECORD_ATTRS:
                    safe[f"extra_{k}"] = v
                else:
                    safe[k] = v
            kwargs["extra"] = safe
        return msg, kwargs


def get_logger(name: str) -> logging.LoggerAdapter:
    """모듈별 로거 획득.

    Args:
        name: 일반적으로 `__name__` 전달.
    """
    return _SafeLogger(logging.getLogger(name), {})
