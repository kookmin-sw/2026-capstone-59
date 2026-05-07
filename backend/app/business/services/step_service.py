import uuid

from sqlalchemy.orm import Session

from app.core.enums import StepStatus
from app.core.exceptions import InvalidRollbackTargetError, StepNotFoundError
from app.core.models.project import ProjectStage as ProjectStageModel
from app.core.models.project_required_step_status import (
    ProjectRequiredStepStatus as ProjectRequiredStepStatusModel,
)
from app.core.models.required_step import RequiredStep as RequiredStepModel
from app.core.models.stage import Stage as StageModel
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

    # ⓪ 롤백 대상이 현재 진행 Stage보다 낮은 Stage이면 윗 Stage들을 모두 정리
    _wipe_upper_stages_if_needed(db, step)

    # ② 클로저 테이블로 조상 + 자기 자신을 depth 오름차순으로 조회
    #    depth=0(자기 자신)은 ACCEPTED 처리에서 제외 — Accept API에서 별도로 처리.
    ancestor_rows = (
        db.query(StepTreeModel)
        .filter(StepTreeModel.descendant == step_id)
        .order_by(StepTreeModel.depth.asc())
        .all()
    )
    ancestor_ids = {row.ancestor for row in ancestor_rows if row.depth > 0}

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

    # ④ 조상들만 ACCEPTED 처리 (롤백 대상은 Accept API에서 처리)
    accepted_targets: list[StepModel] = []
    if ancestor_ids:
        accepted_targets = (
            db.query(StepModel).filter(StepModel.id.in_(ancestor_ids)).all()
        )
        for s in accepted_targets:
            s.status = StepStatus.ACCEPTED

    db.flush()

    # ⑤ Belonging Required Step 이후의 모든 Required Step 상태 fulfilled 해제
    _unfulfill_required_steps_from(db, step)

    db.commit()


def _wipe_upper_stages_if_needed(db: Session, target_step: StepModel) -> None:
    """롤백 대상이 현재 진행 중인 Stage보다 낮은 Stage라면 윗 Stage들의
    Step / StepTree / ProjectRequiredStepStatus를 모두 삭제하고,
    ProjectStage.is_active를 롤백 대상 Stage로 옮긴다."""
    target_stage = target_step.stage
    target_seq = target_stage.sequence

    current_active_seq = (
        db.query(StageModel.sequence)
        .join(ProjectStageModel, ProjectStageModel.stage_id == StageModel.id)
        .filter(
            ProjectStageModel.project_id == target_step.project_id,
            ProjectStageModel.is_active.is_(True),
        )
        .scalar()
    )
    if current_active_seq is None or current_active_seq <= target_seq:
        return  # 윗 Stage가 없으므로 정리할 게 없음

    upper_stage_ids = [
        sid
        for (sid,) in db.query(StageModel.id)
        .filter(StageModel.sequence > target_seq)
        .all()
    ]
    if not upper_stage_ids:
        return

    # ① 윗 Stage의 모든 Step 삭제 — parent_step_id FK가 자기 참조라
    #    먼저 NULL 처리로 끊은 뒤 일괄 DELETE. StepTree는 ondelete=CASCADE로 자동 정리.
    db.query(StepModel).filter(
        StepModel.project_id == target_step.project_id,
        StepModel.stage_id.in_(upper_stage_ids),
    ).update({"parent_step_id": None}, synchronize_session=False)
    db.flush()

    db.query(StepModel).filter(
        StepModel.project_id == target_step.project_id,
        StepModel.stage_id.in_(upper_stage_ids),
    ).delete(synchronize_session=False)

    # ② 윗 Stage의 Required Step Status는 삭제하지 않고 fulfilled 만 해제
    upper_rs_ids_subq = (
        db.query(RequiredStepModel.id)
        .filter(RequiredStepModel.stage_id.in_(upper_stage_ids))
        .subquery()
    )
    db.query(ProjectRequiredStepStatusModel).filter(
        ProjectRequiredStepStatusModel.project_id == target_step.project_id,
        ProjectRequiredStepStatusModel.required_step_id.in_(
            db.query(upper_rs_ids_subq)
        ),
    ).update(
        {"is_fulfilled": False, "fulfilled_at": None},
        synchronize_session=False,
    )

    # ③ ProjectStage.is_active 이동: 윗 Stage → False, 롤백 대상 Stage → True
    db.query(ProjectStageModel).filter(
        ProjectStageModel.project_id == target_step.project_id,
        ProjectStageModel.stage_id.in_(upper_stage_ids),
    ).update({"is_active": False}, synchronize_session=False)
    db.query(ProjectStageModel).filter(
        ProjectStageModel.project_id == target_step.project_id,
        ProjectStageModel.stage_id == target_stage.id,
    ).update({"is_active": True}, synchronize_session=False)
    db.flush()


def _unfulfill_required_steps_from(db: Session, step: StepModel) -> None:
    """롤백 대상의 Belonging Required Step부터 같은 Stage의 이후(sequence ≥) 모든
    Required Step의 ProjectRequiredStepStatus를 is_fulfilled=False로 되돌린다.

    belonging_required_step_id가 없으면 step 자신의 required_step_id를 사용.
    둘 다 없으면 (필수 Step 영역 밖) 아무 작업도 하지 않는다."""
    base_rs_id = step.belonging_required_step_id or step.required_step_id
    if base_rs_id is None:
        return

    base_rs = db.get(RequiredStepModel, base_rs_id)
    if base_rs is None:
        return

    # 같은 Stage에서 sequence가 base 이상인 Required Step의 status 레코드 일괄 해제
    target_rs_ids_subq = (
        db.query(RequiredStepModel.id)
        .filter(
            RequiredStepModel.stage_id == base_rs.stage_id,
            RequiredStepModel.sequence >= base_rs.sequence,
        )
        .subquery()
    )
    records = (
        db.query(ProjectRequiredStepStatusModel)
        .filter(
            ProjectRequiredStepStatusModel.project_id == step.project_id,
            ProjectRequiredStepStatusModel.required_step_id.in_(
                db.query(target_rs_ids_subq)
            ),
        )
        .all()
    )
    for record in records:
        record.is_fulfilled = False
        record.fulfilled_at = None


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
