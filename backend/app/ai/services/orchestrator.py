import json
from uuid import UUID

from app.ai.services.rag import retrieve
from app.core.aws.bedrock import bedrock_runtime
from app.core.config import settings

STEP_GENERATION_PROMPT = """\
당신은 소프트웨어 개발 방법론 전문가입니다. 아래 프로젝트 컨텍스트를 바탕으로,
사용자가 다음에 수행할 수 있는 Step 후보 3개를 제안하세요.

프로젝트 컨텍스트:
{context}

관련 자료:
{references}

JSON 배열 형식으로만 답하세요. 각 원소는 {{"name": str, "guide": str}} 형태입니다.
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


def generate_next_steps(payload: dict) -> dict:
    context = payload.get("context", "")
    refs = retrieve(context) if context else []
    ref_text = "\n".join(r.get("content", {}).get("text", "") for r in refs)

    prompt = STEP_GENERATION_PROMPT.format(context=context, references=ref_text)
    # TODO: remove stub guard once Bedrock is wired
    try:
        raw = _invoke_claude(prompt)
    except Exception as e:  # noqa: BLE001
        return {"error": str(e), "steps": []}

    return {"raw": raw}


def generate_step_details(step_id: UUID, payload: dict) -> dict:
    # TODO: implement guide/dictionary/mentoring/template 생성
    return {"step_id": str(step_id), "todo": [], "dictionary": [], "recommendations": [], "references": []}
