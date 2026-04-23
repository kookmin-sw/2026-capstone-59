from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import status as http_status

from app.ai.services import step_service
from app.core.database import get_db
from app.core.schemas.step import GeneratedStep, StepGenerateResponse, StepTreeNode, StepTreeResponse

router = APIRouter()


def _ok(data):
    return {"status": "success", "data": data}


@router.get("/steps/tree")
def get_step_tree(project_id: UUID, stage_id: UUID, db: Session = Depends(get_db)) -> dict:
    """project_id + stage_id 기준 Step 트리 + Footprint 경로 반환."""
    current_path, steps = step_service.get_step_tree(db, project_id, stage_id)

    node_map: dict[UUID, StepTreeNode] = {
        s.id: StepTreeNode(
            step_id=s.id,
            name=s.name,
            status=s.status,
            is_required=s.required_step_id is not None,
            parent_step_id=s.parent_step_id,
        )
        for s in steps
    }
    roots: list[StepTreeNode] = []
    for s in steps:
        node = node_map[s.id]
        if s.parent_step_id is not None and s.parent_step_id in node_map:
            node_map[s.parent_step_id].children.append(node)
        else:
            roots.append(node)

    response = StepTreeResponse(current_path=current_path, steps=roots)
    return _ok(response.model_dump())


@router.post("/steps/{step_id}/generate", status_code=http_status.HTTP_201_CREATED)
def generate_steps(step_id: UUID, db: Session = Depends(get_db)) -> dict:
    """현재 Step 기반으로 다음 후보 Step 3개를 AI로 생성."""
    steps = step_service.generate_steps(db, step_id)
    response = StepGenerateResponse(
        generated_steps=[
            GeneratedStep(
                step_id=s.id,
                name=s.name,
                status=s.status,
                is_required=s.required_step_id is not None,
                parent_step_id=s.parent_step_id,
            )
            for s in steps
        ]
    )
    return _ok(response.model_dump())


@router.post("/steps/{step_id}/details")
def step_details(step_id: UUID) -> dict:
    """Step 상세 정보: To-Do, 용어, 추천 행위, Reference 생성."""
    return _ok({
        "step_id": str(step_id),
        "todo": ["아이디어 10개 이상 작성", "핵심 3개 선정"],
        "dictionary": [{"term": "MVP", "desc": "Minimum Viable Product"}],
        "recommendations": ["유사 서비스 3개 조사해보기"],
        "references": [{"title": "IDEO 브레인스토밍 가이드", "url": "https://ideo.com"}],
    })
