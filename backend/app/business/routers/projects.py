from uuid import UUID, uuid4

from fastapi import APIRouter

router = APIRouter()


def _ok(data):
    return {"status": "success", "data": data}


_DUMMY_PROJECT = {
    "id": str(uuid4()),
    "name": "샘플 프로젝트",
    "prompt": "AI 기반 일정 관리 서비스 만들기",
    "duration": "4주",
    "member_count": 3,
    "created_at": "2026-04-09T10:00:00Z",
}


@router.get("")
def list_projects():
    return _ok([_DUMMY_PROJECT])


@router.post("")
def create_project(payload: dict):
    return _ok(_DUMMY_PROJECT)


@router.get("/{project_id}")
def get_project(project_id: UUID):
    return _ok({**_DUMMY_PROJECT, "id": str(project_id)})


@router.patch("/{project_id}")
def update_project(project_id: UUID, payload: dict):
    return _ok({**_DUMMY_PROJECT, "id": str(project_id), **payload})


@router.delete("/{project_id}")
def delete_project(project_id: UUID):
    return _ok({"deleted_id": str(project_id)})
