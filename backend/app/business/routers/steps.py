from uuid import UUID, uuid4

from fastapi import APIRouter

router = APIRouter()


def _ok(data):
    return {"status": "success", "data": data}


_DUMMY_STEP = {
    "id": str(uuid4()),
    "project_id": str(uuid4()),
    "stage_id": str(uuid4()),
    "name": "브레인스토밍",
    "status": "Ready",
    "sort_order": 1,
    "content": {
        "dictionary": "브레인스토밍: 자유롭게 아이디어를 쏟아내는 발상 기법",
        "mentoring": "판단은 나중에, 양을 먼저 확보하세요",
        "template_url": "https://notion.so/template/brainstorming",
    },
}


@router.get("")
def list_steps(project_id: UUID | None = None):
    return _ok([_DUMMY_STEP])


@router.get("/{step_id}")
def get_step(step_id: UUID):
    return _ok({**_DUMMY_STEP, "id": str(step_id)})


@router.patch("/{step_id}/status")
def update_step_status(step_id: UUID, payload: dict):
    return _ok({"id": str(step_id), "status": payload.get("status", "Current")})


@router.delete("/{step_id}")
def delete_step(step_id: UUID):
    return _ok({"deleted_id": str(step_id)})
