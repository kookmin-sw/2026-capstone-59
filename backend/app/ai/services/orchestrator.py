import json

from app.core.aws.bedrock import bedrock_runtime
from app.core.config import settings
from app.core.schemas.bedrock import AcceptPayload


ACCEPT_PROMPT = """\
당신은 소프트웨어 개발 방법론 전문가입니다.
아래 데이터를 바탕으로 현재 필수 Step의 목표 달성 여부를 판단하세요.

반드시 아래 JSON 형식만 출력하세요:
{"is_current_required_step_completed": true 또는 false}
"""



def _invoke_claude(prompt: str) -> str:
    client = bedrock_runtime()
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2048,
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = client.invoke_model(
        modelId=settings.BEDROCK_MODEL_ID,
        body=json.dumps(body),
        contentType="application/json",
    )
    payload = json.loads(resp["body"].read())
    return payload["content"][0]["text"]


def call_accept(payload: AcceptPayload) -> dict:
    message = ACCEPT_PROMPT + "\n\n" + json.dumps(payload.model_dump(), ensure_ascii=False)
    raw = _invoke_claude(message)
    return json.loads(raw)