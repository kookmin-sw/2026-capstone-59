import json
import uuid

from sqlalchemy.orm import Session

from app.core.enums import StepStatus
from app.core.exceptions import (
    InvalidInputError,
    InvalidRollbackError,
    StageNotFoundError,
    StepNotFoundError,
)
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
    StepDetailResponse,
    StepKeepResponse,
    StepTreeNode,
    StepTreeResponse,
    AcceptedRequiredStepItem,
    AcceptedRequiredStepListResponse
)

from app.core.logging import get_logger

logger = get_logger(__name__)


def get_step_tree(
    db: Session,
    project_id: uuid.UUID,
    stage_id: uuid.UUID | None = None,
    stage_sequence: int | None = None,
) -> StepTreeResponse:
    """Step 트리 + Footprint 경로를 조립하여 반환.

    stage_id 또는 stage_sequence 중 정확히 하나가 제공되어야 한다.
    stage_sequence 가 주어지면 시드 Stage 테이블에서 해당 Stage 를 조회한다.
    """
    if (stage_id is None) == (stage_sequence is None):
        raise InvalidInputError(
            "stage_id 또는 stage_sequence 중 정확히 하나만 제공해야 합니다."
        )

    if stage_sequence is not None:
        stage = stage_repo.get_stage_by_sequence(db, stage_sequence)
        if stage is None:
            raise StageNotFoundError()
        stage_id = stage.id

    steps = step_repo.get_steps_by_stage(db, project_id, stage_id)
    return StepTreeResponse(
        current_path=_build_current_path(steps),
        steps=_build_tree(steps),
    )


def get_step_content(
    db: Session, project_id: uuid.UUID, step_id: uuid.UUID
) -> StepDetailResponse:
    """DB에 저장된 StepContent를 그대로 반환 (read-only, AI 호출 없음)."""
    step = step_repo.get_step(db, step_id)
    if step is None or step.project_id != project_id:
        logger.warning(
            "step: shared content lookup failed — not found or project mismatch",
            extra={"project_id": str(project_id), "step_id": str(step_id)},
        )
        raise StepNotFoundError()

    content = step_repo.get_step_content(db, step_id)

    template_url: str | None = None
    if step.required_step_id is not None:
        rs = required_step_repo.get_required_step(db, step.required_step_id)
        template_url = rs.template_url if rs else None

    return StepDetailResponse(
        is_required=step.required_step_id is not None,
        step_id=step.id,
        name=step.name,
        mentoring=(
            json.loads(content.mentoring) if content and content.mentoring else None
        ),
        dictionary=(
            json.loads(content.dictionary) if content and content.dictionary else None
        ),
        template_url=template_url,
        is_keep=step.is_keep,
    )


def update_step_keep(
    db: Session, step_id: uuid.UUID, is_keep: bool
) -> StepKeepResponse:
    """Step.is_keep 값을 갱신한다."""
    step = step_repo.get_step(db, step_id)
    if step is None:
        logger.warning(
            "step: keep update rejected — not found",
            extra={"step_id": str(step_id)},
        )
        raise StepNotFoundError()

    step_repo.update_step_is_keep(step, is_keep)
    db.commit()
    db.refresh(step)

    logger.info(
        "step: keep updated",
        extra={
            "project_id": str(step.project_id),
            "step_id": str(step.id),
            "is_keep": is_keep,
        },
    )
    return StepKeepResponse(id=step.id, is_keep=step.is_keep)


def rollback_step(db: Session, step_id: uuid.UUID) -> None:
    logger.debug("step: rollback start", extra={"step_id": str(step_id)})

    step = step_repo.get_step(db, step_id)
    if step is None:
        logger.warning(
            "step: rollback rejected — not found",
            extra={"step_id": str(step_id)},
        )
        raise StepNotFoundError()

    # ① 자식 Step이 있으면 Rollback 불가
    if step_repo.has_children(db, step_id):
        logger.warning(
            "step: rollback rejected — has children",
            extra={
                "project_id": str(step.project_id),
                "stage_id": str(step.stage_id),
                "step_id": str(step_id),
            },
        )
        raise InvalidRollbackError()

    # ⓪ 롤백 대상이 현재 진행 Stage보다 낮은 Stage이면 윗 Stage 정리
    _wipe_upper_stages_if_needed(db, step)

    # ② 클로저 테이블로 조상 조회 (depth=0 자기 자신은 제외)
    ancestor_rows = step_repo.get_ancestors_ordered(db, step_id)
    ancestor_ids = {row.ancestor for row in ancestor_rows if row.depth > 0}

    # ③ 같은 Stage 내 ACCEPTED Step만 CANCELED 처리 (이전 Stage는 유지)
    accepted_steps_in_stage = step_repo.get_accepted_steps_in_stage(
        db, step.project_id, step.stage_id
    )
    logger.debug(
        "rollback: canceling accepted steps in stage",
        extra={
            "project_id": str(step.project_id),
            "stage_id": str(step.stage_id),
            "rollback_target_step_id": str(step.id),
            "canceled_count": len(accepted_steps_in_stage),
            "canceled_step_ids": [str(s.id) for s in accepted_steps_in_stage],
            "canceled_step_names": [s.name for s in accepted_steps_in_stage],
        },
    )
    step_repo.set_status_bulk(
        accepted_steps_in_stage,
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
    logger.info(
        "step: rollback completed",
        extra={
            "project_id": str(step.project_id),
            "stage_id": str(step.stage_id),
            "step_id": str(step.id),
            "canceled_count": len(accepted_steps_in_stage),
            "restored_ancestor_count": len(ancestor_ids),
        },
    )


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
    # 각 Stage의 첫 번째 Required Step에 해당하는 Step은 보존
    first_rs_step_ids = step_repo.get_first_rs_step_ids_in_stages(
        db, target_step.project_id, upper_stage_ids
    )
    step_repo.detach_steps_from_parent_in_stages(
        db, target_step.project_id, upper_stage_ids, exclude_step_ids=first_rs_step_ids
    )
    db.flush()
    step_repo.delete_steps_in_stages(
        db, target_step.project_id, upper_stage_ids, exclude_step_ids=first_rs_step_ids
    )

    # 보존된 첫 번째 RS Step은 status를 READY로 리셋
    if first_rs_step_ids:
        preserved_steps = step_repo.get_steps_by_ids(db, first_rs_step_ids)
        step_repo.set_status_bulk(preserved_steps, StepStatus.READY)

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

    logger.info(
        "stage: rolled back to lower sequence",
        extra={
            "project_id": str(target_step.project_id),
            "target_stage_id": str(target_stage.id),
            "target_stage_sequence": target_seq,
            "wiped_stage_count": len(upper_stage_ids),
            "preserved_step_count": len(first_rs_step_ids),
        },
    )


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
            is_keep=s.is_keep,
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

def get_accepted_required_steps(db: Session, project_id: uuid.UUID) -> AcceptedRequiredStepListResponse:
    steps = step_repo.get_accepted_required_steps(db, project_id)
    return AcceptedRequiredStepListResponse(
        required_steps=[
            AcceptedRequiredStepItem(
                step_id=s.id,
                name=s.name,
                stage_sequence=s.stage.sequence,
            )
            for s in steps
        ]
    )
