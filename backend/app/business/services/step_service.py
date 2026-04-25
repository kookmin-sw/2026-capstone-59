import uuid

from sqlalchemy.orm import Session

from app.core.enums import StepStatus
from app.core.models.step import Step
from app.core.schemas.step import StepTreeNode, StepTreeResponse


def get_step_tree(
    db: Session, project_id: uuid.UUID, stage_id: uuid.UUID
) -> StepTreeResponse:
    """Step 트리 + Footprint 경로를 조립하여 반환."""
    steps = (
        db.query(Step)
        .filter(Step.project_id == project_id, Step.stage_id == stage_id)
        .order_by(Step.sort_order)
        .all()
    )

    current_path = _build_current_path(steps)
    roots = _build_tree(steps)

    return StepTreeResponse(current_path=current_path, steps=roots)


def _build_current_path(steps: list[Step]) -> list[uuid.UUID]:
    """ACCEPTED 경로의 step_id 순서 (루트→말단)."""
    accepted_ids = {s.id for s in steps if s.status == StepStatus.ACCEPTED}

    current_path: list[uuid.UUID] = []
    current = next(
        (
            s
            for s in steps
            if s.id in accepted_ids
            and (s.parent_step_id is None or s.parent_step_id not in accepted_ids)
        ),
        None,
    )
    while current is not None:
        current_path.append(current.id)
        current = next(
            (
                s
                for s in steps
                if s.parent_step_id == current.id and s.id in accepted_ids
            ),
            None,
        )
    return current_path


def _build_tree(steps: list[Step]) -> list[StepTreeNode]:
    """flat한 Step 리스트를 재귀 트리 구조로 조립."""
    node_map: dict[uuid.UUID, StepTreeNode] = {
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

    return roots


from app.core.models.required_step import RequiredStep
from app.core.schemas.step import RequiredStepItem, RequiredStepListResponse


def get_required_steps(db: Session, stage_id: uuid.UUID) -> RequiredStepListResponse:
    """특정 Stage의 Required Step 목록 조회."""
    required_steps = (
        db.query(RequiredStep)
        .filter(RequiredStep.stage_id == stage_id)
        .order_by(RequiredStep.sequence)
        .all()
    )
    return RequiredStepListResponse(
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
