from uuid import UUID, uuid4

from fastapi import APIRouter

router = APIRouter()


def _ok(data):
    return {"status": "success", "data": data}


_DUMMY_STAGES = [
    {"id": str(uuid4()), "name": "아이디에이션", "sequence": 1},
    {"id": str(uuid4()), "name": "요구사항 분석", "sequence": 2},
    {"id": str(uuid4()), "name": "설계", "sequence": 3},
    {"id": str(uuid4()), "name": "개발", "sequence": 4},
    {"id": str(uuid4()), "name": "테스트 및 배포", "sequence": 5},
]


@router.get("")
def list_stages():
    return _ok(_DUMMY_STAGES)


@router.post("/project/{project_id}/complete")
def complete_stage(project_id: UUID, stage_id: UUID, payload: dict):
    return _ok({
        "project_id": str(project_id),
        "stage_id": str(stage_id),
        "status": "Completed",
        "completed_at": "2026-04-09T12:00:00Z",
    })
