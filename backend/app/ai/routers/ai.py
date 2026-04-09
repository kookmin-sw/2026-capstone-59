from uuid import UUID, uuid4

from fastapi import APIRouter

router = APIRouter()


def _ok(data):
    return {"status": "success", "data": data}


@router.post("/steps")
def generate_steps(payload: dict):
    """프로젝트 프롬프트/현재 step 기반으로 다음 후보 step들을 생성."""
    return _ok({
        "candidates": [
            {"id": str(uuid4()), "name": "아이디에이션", "guide": "자유롭게 아이디어 발상"},
            {"id": str(uuid4()), "name": "브레인스토밍", "guide": "팀과 함께 아이디어 확장"},
            {"id": str(uuid4()), "name": "이벤트 스토밍", "guide": "도메인 이벤트 정리"},
        ]
    })


@router.post("/steps/{step_id}/details")
def step_details(step_id: UUID, payload: dict):
    """Step 상세 정보: To-Do, 용어, 추천 행위, Reference 생성."""
    return _ok({
        "step_id": str(step_id),
        "todo": ["아이디어 10개 이상 작성", "핵심 3개 선정"],
        "dictionary": [{"term": "MVP", "desc": "Minimum Viable Product"}],
        "recommendations": ["유사 서비스 3개 조사해보기"],
        "references": [{"title": "IDEO 브레인스토밍 가이드", "url": "https://ideo.com"}],
    })
