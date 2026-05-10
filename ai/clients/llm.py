"""Bedrock Claude LLM 클라이언트.

boto3 bedrock-runtime 클라이언트를 의존성 주입받아, 프롬프트를 호출하고
응답을 Pydantic 스키마로 검증한다. 스키마/JSON 실패는 재시도, Bedrock API
에러는 즉시 raise한다.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from json import JSONDecodeError
from typing import Any, AsyncIterator, Optional, TypeVar

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
        max_tokens: Optional[int] = None,
    ) -> T:
        """Claude를 호출하여 expected_schema로 검증된 인스턴스를 반환.

        - JSON 파싱 실패 / 스키마 불일치 → max_retries 까지 재시도
        - Bedrock API 에러(ClientError, BotoCoreError) → 즉시 BedrockAPIError
        - 재시도 초과 → AIGenerationFailedError (불일치 필드 details 포함)

        max_tokens 우선순위:
            invoke(max_tokens=X) 명시값 > self.max_tokens (생성자 값) > 생성자 기본값(4096).
        재시도 루프 안에서는 동일 request_body(= 동일 effective_max_tokens)를 재사용한다.
        """
        correlation_id = str(uuid.uuid4())
        effective_max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        request_body = json.dumps(
            {
                "anthropic_version": _ANTHROPIC_VERSION,
                "max_tokens": effective_max_tokens,
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
            max_tokens=effective_max_tokens,
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

    async def invoke_stream(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Bedrock Claude 스트리밍 호출. content_block_delta의 text만 yield.

        - Pydantic 검증 없음. 재시도 없음.
        - max_tokens 우선순위: 인자 > self.max_tokens > 생성자 기본값 (invoke와 동일).
        - ClientError/BotoCoreError → BedrockAPIError로 래핑하여 re-raise.
        - JSON decode 실패 청크는 log warning 후 skip (스트림 전체는 계속).
        - 응답이 코드 펜스(```json...``` 또는 ```...```)로 감싸인 경우 자동으로 벗겨낸다.
        """
        correlation_id = str(uuid.uuid4())
        effective_max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        request_body = json.dumps(
            {
                "anthropic_version": _ANTHROPIC_VERSION,
                "max_tokens": effective_max_tokens,
                "temperature": self.temperature,
                "messages": [{"role": "user", "content": prompt}],
            }
        )

        _log(
            logging.INFO,
            "llm_invoke_stream_start",
            correlation_id=correlation_id,
            model_id=self.model_id,
            max_tokens=effective_max_tokens,
            prompt_len=len(prompt),
        )

        start = time.perf_counter()
        total_chunks = 0

        try:
            response = await asyncio.to_thread(
                self.bedrock_client.invoke_model_with_response_stream,
                modelId=self.model_id,
                body=request_body,
                contentType="application/json",
            )
        except (ClientError, BotoCoreError) as exc:
            elapsed = time.perf_counter() - start
            error_details = {
                "correlation_id": correlation_id,
                "model_id": self.model_id,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "elapsed_s": round(elapsed, 3),
            }
            _log(logging.ERROR, "llm_invoke_stream_failed", **error_details)
            raise BedrockAPIError(
                message="Bedrock 스트리밍 호출에 실패했습니다.",
                details=error_details,
            ) from exc

        # Opening fence prefixes Bedrock may prepend to JSON output.
        _FENCE_PREFIXES = ("```json\n", "```json\r\n", "```\n", "```\r\n")
        # Must be ≥ len("\n```") = 4 to catch the longest trailing fence.
        _TAIL_BUFFER_SIZE = 4

        first_flush = False   # True once opening-fence decision is made
        fence_active = False  # True if an opening fence was stripped
        pending = ""          # pre-flush accumulator
        tail_buffer = ""      # sliding window for trailing-fence detection

        _SENTINEL = object()
        try:
            event_iter = iter(response["body"])
            while True:
                event = await asyncio.to_thread(next, event_iter, _SENTINEL)
                if event is _SENTINEL:
                    break
                chunk_bytes = event.get("chunk", {}).get("bytes") if isinstance(event, dict) else None
                if not chunk_bytes:
                    # MagicMock 기반 이벤트는 dict가 아닐 수 있어 getattr fallback.
                    chunk_obj = getattr(event, "get", lambda _k, _d=None: None)("chunk", {})
                    chunk_bytes = chunk_obj.get("bytes") if isinstance(chunk_obj, dict) else None
                if not chunk_bytes:
                    continue
                try:
                    payload = json.loads(chunk_bytes.decode("utf-8"))
                except (JSONDecodeError, UnicodeDecodeError) as exc:
                    _log(
                        logging.WARNING,
                        "llm_invoke_stream_chunk_skipped",
                        correlation_id=correlation_id,
                        reason=type(exc).__name__,
                    )
                    continue
                if payload.get("type") != "content_block_delta":
                    continue
                text = payload.get("delta", {}).get("text", "")
                if not text:
                    continue

                total_chunks += 1

                if not first_flush:
                    pending += text
                    stripped_p = pending.lstrip()
                    ready = False
                    if not stripped_p.startswith("`"):
                        # Definitely not a fence — flush immediately (TTFT优先)
                        ready = True
                    elif len(stripped_p) >= 3 and not stripped_p.startswith("```"):
                        # Starts with ` or `` but not ``` — not a fence
                        ready = True
                    elif stripped_p.startswith("```") and ("\n" in pending or len(pending) >= 200):
                        # Confirmed fence opening; wait for the newline that ends the fence line
                        ready = True
                    if ready:
                        matched = None
                        for prefix in _FENCE_PREFIXES:
                            if stripped_p.startswith(prefix):
                                matched = prefix
                                break
                        if matched:
                            fence_active = True
                            leading_ws = len(pending) - len(stripped_p)
                            tail_buffer = pending[leading_ws + len(matched):]
                        else:
                            tail_buffer = pending
                        first_flush = True
                        pending = ""
                else:
                    tail_buffer += text

                # Yield safe portion; keep last _TAIL_BUFFER_SIZE chars for trailing-fence check.
                if first_flush and len(tail_buffer) > _TAIL_BUFFER_SIZE:
                    safe = tail_buffer[:-_TAIL_BUFFER_SIZE]
                    tail_buffer = tail_buffer[-_TAIL_BUFFER_SIZE:]
                    if safe:
                        yield safe
        except (ClientError, BotoCoreError) as exc:
            elapsed = time.perf_counter() - start
            error_details = {
                "correlation_id": correlation_id,
                "model_id": self.model_id,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "elapsed_s": round(elapsed, 3),
            }
            _log(logging.ERROR, "llm_invoke_stream_failed", **error_details)
            raise BedrockAPIError(
                message="Bedrock 스트리밍 수신 중 오류가 발생했습니다.",
                details=error_details,
            ) from exc

        # End-of-stream flush.
        # If first_flush never triggered (response shorter than detection threshold),
        # process pending now.
        if pending:
            stripped_p = pending.lstrip()
            matched = None
            for prefix in _FENCE_PREFIXES:
                if stripped_p.startswith(prefix):
                    matched = prefix
                    break
            if matched:
                fence_active = True
                leading_ws = len(pending) - len(stripped_p)
                tail_buffer = pending[leading_ws + len(matched):]
            else:
                tail_buffer = pending

        # Strip trailing closing fence only when an opening fence was detected.
        final = tail_buffer.rstrip()
        if fence_active:
            for suffix in ("```", "\n```"):
                if final.endswith(suffix):
                    final = final[: -len(suffix)].rstrip()
                    break
        if final:
            yield final

        elapsed = time.perf_counter() - start
        _log(
            logging.INFO,
            "llm_invoke_stream_end",
            correlation_id=correlation_id,
            model_id=self.model_id,
            total_chunks=total_chunks,
            elapsed_s=round(elapsed, 3),
        )
