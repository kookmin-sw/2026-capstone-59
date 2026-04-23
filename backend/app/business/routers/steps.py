from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.business.dependency import get_db
from app.business.services import step_service
from app.core.schemas.step import RequiredStepItem, RequiredStepListResponse, StepTreeNode, StepTreeResponse

router = APIRouter()


def _ok(data):
    return {"status": "success", "data": data}


@router.get("/tree")
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


@router.get("/{stage_id}/required")
def get_required_steps(stage_id: UUID, db: Session = Depends(get_db)) -> dict:
    """특정 Stage의 Required Step 목록 조회."""
    required_steps = step_service.get_required_steps(db, stage_id)
    response = RequiredStepListResponse(
        required_step=[
            RequiredStepItem(
                step_id=rs.id,
                name=rs.name,
                stage_id=rs.stage_id,
                sequence=rs.sequence,
            )
            for rs in required_steps
        ]
    )
    return _ok(response.model_dump())
