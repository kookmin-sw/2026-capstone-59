import uuid

from sqlalchemy.orm import Session

from app.core.enums import StepStatus
from app.core.exceptions import InvalidRollbackError, StepNotFoundError
from app.core.models.step import Step as StepModel
from app.core.repositories import (
    project as project_repo,
    required_step as required_step_repo,
    stage as stage_repo,
    step as step_repo,
)
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
    steps = step_repo.get_steps_by_stage(db, project_id, stage_id)
    return StepTreeResponse(
        current_path=_build_current_path(steps),
        steps=_build_tree(steps),
    )


def rollback_step(db: Session, step_id: uuid.UUID) -> None:
    step = step_repo.get_step(db, step_id)
    if step is None:
        raise StepNotFoundError()

    # ① 자식 Step이 있으면 Rollback 불가
    if step_repo.has_children(db, step_id):
        raise InvalidRollbackError()

    # ⓪ 롤백 대상이 현재 진행 Stage보다 낮은 Stage이면 윗 Stage 정리
    _wipe_upper_stages_if_needed(db, step)

    # ② 클로저 테이블로 조상 조회 (depth=0 자기 자신은 제외)
    ancestor_rows = step_repo.get_ancestors_ordered(db, step_id)
    ancestor_ids = {row.ancestor for row in ancestor_rows if row.depth > 0}

    # ③ 프로젝트의 기존 ACCEPTED 흐름을 모두 CANCELED 처리
    step_repo.set_status_bulk(
        step_repo.get_accepted_steps_by_project(db, step.project_id),
        StepStatus.CANCELED,
    )

    # ④ 조상들만 ACCEPTED 처리 (롤백 대상은 Accept API에서 처리)
    if ancestor_ids:
        step_repo.set_status_bulk(
            step_repo.get_steps_by_ids(db, ancestor_ids),
            StepStatus.ACCEPTED,
        )

    db.flush()

    # ⑤ Belonging Required Step 기준 이전 RS는 fulfilled True, 이후는 fulfilled False
    _realign_required_step_fulfillment(db, step)

    db.commit()


def _wipe_upper_stages_if_needed(db: Session, target_step: StepModel) -> None:
    """롤백 대상이 현재 진행 중인 Stage보다 낮으면 윗 Stage들의 Step / Required Step Status를 정리."""
    target_stage = target_step.stage
    target_seq = target_stage.sequence

    current_active_seq = project_repo.get_active_stage_sequence(
        db, target_step.project_id
    )
    if current_active_seq is None or current_active_seq <= target_seq:
        return

    upper_stage_ids = stage_repo.get_stage_ids_after_sequence(db, target_seq)
    if not upper_stage_ids:
        return

    # ① 윗 Stage Step 정리 (자기참조 FK 회피용 NULL → DELETE)
    step_repo.detach_steps_from_parent_in_stages(
        db, target_step.project_id, upper_stage_ids
    )
    db.flush()
    step_repo.delete_steps_in_stages(db, target_step.project_id, upper_stage_ids)

    # ② 윗 Stage Required Step Status fulfilled 해제
    upper_rs_ids = required_step_repo.get_required_step_ids_in_stages(
        db, upper_stage_ids
    )
    project_repo.unfulfill_by_required_step_ids(
        db, target_step.project_id, upper_rs_ids
    )

    # ③ ProjectStage.is_active 이동
    project_repo.deactivate_project_stages(db, target_step.project_id, upper_stage_ids)
    project_repo.activate_project_stage(db, target_step.project_id, target_stage.id)
    db.flush()


def _realign_required_step_fulfillment(db: Session, step: StepModel) -> None:
    """롤백 대상의 Belonging Required Step 기준으로 fulfilled 상태를 재정렬.

    - base_rs.sequence 이상: is_fulfilled = False
    - base_rs.sequence 미만: is_fulfilled = True
    """
    base_rs_id = step.belonging_required_step_id or step.required_step_id
    if base_rs_id is None:
        return

    base_rs = required_step_repo.get_required_step(db, base_rs_id)
    if base_rs is None:
        return

    # sequence >= base_rs.sequence → unfulfill
    target_rs_ids = required_step_repo.get_required_step_ids_from_sequence(
        db, base_rs.stage_id, base_rs.sequence
    )
    project_repo.unfulfill_by_required_step_ids(db, step.project_id, target_rs_ids)

    # sequence < base_rs.sequence → fulfill
    prior_rs_ids = required_step_repo.get_required_step_ids_before_sequence(
        db, base_rs.stage_id, base_rs.sequence
    )
    project_repo.fulfill_by_required_step_ids(db, step.project_id, prior_rs_ids)


def get_required_steps(db: Session, stage_id: uuid.UUID) -> RequiredStepListResponse:
    required_steps = required_step_repo.get_required_steps_in_stage(db, stage_id)
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
