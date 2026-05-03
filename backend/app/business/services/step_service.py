import uuid

from sqlalchemy.orm import Session

from app.core.enums import StepStatus
from app.core.exceptions import InvalidRollbackTargetError, StepNotFoundError
from app.core.models.project_required_step_status import (
    ProjectRequiredStepStatus as ProjectRequiredStepStatusModel,
)
from app.core.models.required_step import RequiredStep as RequiredStepModel
from app.core.models.step import Step as StepModel
from app.core.models.step import StepTree as StepTreeModel
from app.core.schemas.step import (
    RequiredStepItem,
    RequiredStepListResponse,
    StepTreeNode,
    StepTreeResponse,
)


def get_step_tree(
    db: Session, project_id: uuid.UUID, stage_id: uuid.UUID
) -> StepTreeResponse:
    """Step 트리 + Footprint 경로를 조립하여 반환."""
    steps = (
        db.query(StepModel)
        .filter(StepModel.project_id == project_id, StepModel.stage_id == stage_id)
        .order_by(StepModel.sort_order)
        .all()
    )

    current_path = _build_current_path(steps)
    roots = _build_tree(steps)

    return StepTreeResponse(current_path=current_path, steps=roots)


def rollback_step(db: Session, step_id: uuid.UUID) -> None:
    step = db.get(StepModel, step_id)
    if step is None:
        raise StepNotFoundError()

    # ① children 존재 여부 검사
    has_child = (
        db.query(StepModel.id).filter(StepModel.parent_step_id == step_id).first()
        is not None
    )
    if has_child:
        raise InvalidRollbackTargetError("자식 Step이 있는 Step은 롤백할 수 없습니다.")

    # ② 클로저 테이블로 조상 + 자기 자신을 depth 오름차순으로 조회
    ancestor_rows = (
        db.query(StepTreeModel)
        .filter(StepTreeModel.descendant == step_id)
        .order_by(StepTreeModel.depth.asc())
        .all()
    )
    ancestor_ids = {row.ancestor for row in ancestor_rows}

    # ③ 프로젝트의 기존 ACCEPTED 흐름을 모두 CANCELED 처리
    previously_accepted = (
        db.query(StepModel)
        .filter(
            StepModel.project_id == step.project_id,
            StepModel.status == StepStatus.ACCEPTED,
        )
        .all()
    )
    for s in previously_accepted:
        s.status = StepStatus.CANCELED

    # ④ 롤백 대상 + 조상들을 ACCEPTED 처리
    accepted_targets = db.query(StepModel).filter(StepModel.id.in_(ancestor_ids)).all()
    for s in accepted_targets:
        s.status = StepStatus.ACCEPTED

    db.flush()

    # ⑤ 가장 가까운 Required Step 찾아 fulfilled 해제
    unfulfilled_rs_id = _find_nearest_required_step_id(accepted_targets, ancestor_rows)
    if unfulfilled_rs_id is not None:
        record = db.get(
            ProjectRequiredStepStatusModel,
            {
                "project_id": step.project_id,
                "required_step_id": unfulfilled_rs_id,
            },
        )
        if record is not None:
            record.is_fulfilled = False
            record.fulfilled_at = None

    db.commit()


def _find_nearest_required_step_id(
    ancestor_steps: list[StepModel],
    ancestor_rows: list[StepTreeModel],
) -> uuid.UUID | None:

    step_by_id = {s.id: s for s in ancestor_steps}
    for row in ancestor_rows:
        s = step_by_id.get(row.ancestor)
        if s is None:
            continue
        if s.required_step_id is not None:
            return s.required_step_id
        if s.belonging_required_step_id is not None:
            return s.belonging_required_step_id
    return None


def get_required_steps(db: Session, stage_id: uuid.UUID) -> RequiredStepListResponse:
    """특정 Stage의 Required Step 목록 조회."""
    required_steps = (
        db.query(RequiredStepModel)
        .filter(RequiredStepModel.stage_id == stage_id)
        .order_by(RequiredStepModel.sequence)
        .all()
    )
    return RequiredStepListResponse(
        required_steps=[
            RequiredStepItem(
                step_id=rs.id,
                name=rs.name,
                stage_id=rs.stage_id,
                sequence=rs.sequence,
            )
            for rs in required_steps
        ]
    )


def _build_current_path(steps: list[StepModel]) -> list[uuid.UUID]:
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


def _build_tree(steps: list[StepModel]) -> list[StepTreeNode]:
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
