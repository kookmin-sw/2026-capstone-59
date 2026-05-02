import json

from app.core.aws.bedrock import bedrock_runtime
from app.core.config import settings
from app.core.schemas.step import AcceptRequest, GenerateRequest, SidePanelRequest


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


ACCEPT_PROMPT = """\
당신은 소프트웨어 개발 방법론 전문가입니다.
아래 데이터를 바탕으로 현재 필수 Step의 목표 달성 여부를 판단하세요.

반드시 아래 JSON 형식만 출력하세요:
{"is_current_required_step_completed": true 또는 false}
"""


def call_accept(request: AcceptRequest) -> dict:
    message = (
        ACCEPT_PROMPT + "\n\n" + json.dumps(request.model_dump(), ensure_ascii=False)
    )
    raw = _invoke_claude(message)
    return json.loads(raw)


GENERATE_PROMPT = """\
당신은 소프트웨어 개발 방법론 전문가입니다.
아래 데이터를 바탕으로 현재 프로젝트 상황에 적합한 다음 액션 Step 3개를 제안하세요.
Step 이름은 구체적이고 실행 가능한 동사형으로 작성하세요.

반드시 아래 JSON 형식만 출력하세요:
{"generated_steps": [{"name": "Step 이름1"}, {"name": "Step 이름2"}, {"name": "Step 이름3"}]}
"""


def call_generate(request: GenerateRequest) -> dict:
    message = (
        GENERATE_PROMPT + "\n\n" + json.dumps(request.model_dump(), ensure_ascii=False)
    )
    raw = _invoke_claude(message)
    return json.loads(raw)


SIDE_PANEL_PROMPT = """\
당신은 소프트웨어 개발 방법론 전문가입니다.
아래 데이터를 바탕으로 사용자가 클릭한 Step에 대한 멘토링과 용어 사전을 생성하세요.
이미 진행된 decision_history를 참고해 중복되지 않는 가이드를 제공하세요.

반드시 아래 JSON 형식만 출력하세요:
{
  "mentoring": {
    "description": "이 Step이 왜 필요한지, 무엇을 해야 하는지",
    "recommended_methods": [{ "title": "...", "content": "..." }],
    "common_mistakes": [{ "mistake": "...", "bad_example": "...", "good_example": "..." }],
    "one_line_tip": "..."
  },
  "dictionary": [
    { "term": "...", "definition": "..." }
  ]
}
"""


def call_side_panel(request: SidePanelRequest) -> dict:
    message = (
        SIDE_PANEL_PROMPT
        + "\n\n"
        + json.dumps(request.model_dump(), ensure_ascii=False)
    )
    raw = _invoke_claude(message)
    return json.loads(raw)
