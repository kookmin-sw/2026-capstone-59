"""Bedrock Claude LLM 클라이언트.

boto3 bedrock-runtime 클라이언트를 의존성 주입받아, 프롬프트를 호출하고
응답을 Pydantic 스키마로 검증한다. 스키마/JSON 실패는 재시도, Bedrock API
에러는 즉시 raise한다.
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from json import JSONDecodeError
from typing import Any, Optional, TypeVar

from botocore.exceptions import BotoCoreError, ClientError
from pydantic import BaseModel, ValidationError

from ai.exceptions import AIGenerationFailedError, BedrockAPIError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

_ANTHROPIC_VERSION = "bedrock-2023-05-31"


def _log(level: int, event: str, **fields: Any) -> None:
    """JSON 직렬화된 단일 라인을 표준 logging으로 emit."""
    payload = {"event": event, **fields}
    logger.log(level, json.dumps(payload, ensure_ascii=False, default=str))


class LLMClient:
    """Bedrock Claude 호출 + Pydantic 스키마 검증 래퍼."""

    def __init__(
        self,
        bedrock_client: Any,
        model_id: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> None:
        self.bedrock_client = bedrock_client
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.temperature = temperature

    async def invoke(
        self,
        prompt: str,
        expected_schema: type[T],
        max_retries: int = 2,
    ) -> T:
        """Claude를 호출하여 expected_schema로 검증된 인스턴스를 반환.

        - JSON 파싱 실패 / 스키마 불일치 → max_retries 까지 재시도
        - Bedrock API 에러(ClientError, BotoCoreError) → 즉시 BedrockAPIError
        - 재시도 초과 → AIGenerationFailedError (불일치 필드 details 포함)
        """
        correlation_id = str(uuid.uuid4())
        request_body = json.dumps(
            {
                "anthropic_version": _ANTHROPIC_VERSION,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "messages": [{"role": "user", "content": prompt}],
            }
        )

        _log(
            logging.INFO,
            "llm_invoke_start",
            correlation_id=correlation_id,
            model_id=self.model_id,
            max_retries=max_retries,
            prompt_len=len(prompt),
            schema=expected_schema.__name__,
        )

        last_error: Optional[dict[str, Any]] = None

        for attempt in range(max_retries + 1):
            try:
                response = await asyncio.to_thread(
                    self.bedrock_client.invoke_model,
                    modelId=self.model_id,
                    body=request_body,
                    contentType="application/json",
                    accept="application/json",
                )
            except (ClientError, BotoCoreError) as exc:
                error_details = {
                    "correlation_id": correlation_id,
                    "model_id": self.model_id,
                    "attempt": attempt,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
                _log(logging.ERROR, "llm_bedrock_api_error", **error_details)
                raise BedrockAPIError(
                    message="Bedrock API 호출에 실패했습니다.",
                    details=error_details,
                ) from exc

            try:
                raw = response["body"].read()
                envelope = json.loads(raw)
                text = envelope["content"][0]["text"]
                stripped = text.strip()
                if stripped.startswith("```"):
                    lines = stripped.splitlines()
                    stripped = "\n".join(lines[1:-1]).strip()
                payload = json.loads(stripped)
                validated = expected_schema.model_validate(payload)
            except JSONDecodeError as exc:
                last_error = {
                    "type": "json_decode_error",
                    "message": str(exc),
                    "attempt": attempt,
                }
                _log(
                    logging.WARNING,
                    "llm_invoke_retry",
                    correlation_id=correlation_id,
                    model_id=self.model_id,
                    attempt=attempt,
                    reason="json_decode_error",
                    error=str(exc),
                )
                continue
            except ValidationError as exc:
                last_error = {
                    "type": "schema_validation_error",
                    "schema": expected_schema.__name__,
                    "errors": exc.errors(),
                    "attempt": attempt,
                }
                _log(
                    logging.WARNING,
                    "llm_invoke_retry",
                    correlation_id=correlation_id,
                    model_id=self.model_id,
                    attempt=attempt,
                    reason="schema_validation_error",
                    schema=expected_schema.__name__,
                    errors=exc.errors(),
                )
                continue
            except (KeyError, IndexError, TypeError) as exc:
                last_error = {
                    "type": "malformed_response",
                    "message": str(exc),
                    "attempt": attempt,
                }
                _log(
                    logging.WARNING,
                    "llm_invoke_retry",
                    correlation_id=correlation_id,
                    model_id=self.model_id,
                    attempt=attempt,
                    reason="malformed_response",
                    error=str(exc),
                )
                continue

            _log(
                logging.INFO,
                "llm_invoke_success",
                correlation_id=correlation_id,
                model_id=self.model_id,
                attempt=attempt,
                schema=expected_schema.__name__,
            )
            return validated

        details = {
            "correlation_id": correlation_id,
            "model_id": self.model_id,
            "max_retries": max_retries,
            "last_error": last_error,
        }
        _log(logging.ERROR, "llm_invoke_failed", **details)
        raise AIGenerationFailedError(
            message="AI 생성에 실패했습니다 (재시도 초과).",
            details=details,
        )
