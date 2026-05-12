"""Step / StepContent / StepTree repository."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.enums import StepStatus
from app.core.models.step import Step, StepContent, StepTree

# ── Step ───────────────────────────────────────────────────────────────


def get_step(db: Session, step_id: UUID) -> Step | None:
    return db.get(Step, step_id)


def get_steps_by_ids(db: Session, step_ids: Iterable[UUID]) -> list[Step]:
    ids = list(step_ids)
    if not ids:
        return []
    return db.query(Step).filter(Step.id.in_(ids)).all()


def get_steps_by_stage(db: Session, project_id: UUID, stage_id: UUID) -> list[Step]:
    return (
        db.query(Step)
        .filter(Step.project_id == project_id, Step.stage_id == stage_id)
        .order_by(Step.sort_order)
        .all()
    )


def get_accepted_steps_in_stage(
    db: Session, project_id: UUID, stage_id: UUID
) -> list[Step]:
    return (
        db.query(Step)
        .filter(
            Step.project_id == project_id,
            Step.stage_id == stage_id,
            Step.status == StepStatus.ACCEPTED,
        )
        .all()
    )


def get_accepted_steps_in_required(
    db: Session, project_id: UUID, belonging_required_step_id: UUID
) -> list[Step]:
    return (
        db.query(Step)
        .filter(
            Step.project_id == project_id,
            Step.belonging_required_step_id == belonging_required_step_id,
            Step.status == StepStatus.ACCEPTED,
        )
        .all()
    )


def get_ready_siblings(
    db: Session, parent_step_id: UUID, exclude_step_id: UUID
) -> list[Step]:
    return (
        db.query(Step)
        .filter(
            Step.parent_step_id == parent_step_id,
            Step.id != exclude_step_id,
            Step.status == StepStatus.READY,
        )
        .all()
    )


def has_children(db: Session, step_id: UUID) -> bool:
    return db.query(Step.id).filter(Step.parent_step_id == step_id).first() is not None


def get_existing_pending_required_step(
    db: Session, project_id: UUID, stage_id: UUID, required_step_id: UUID
) -> Step | None:
    return (
        db.query(Step)
        .filter(
            Step.project_id == project_id,
            Step.stage_id == stage_id,
            Step.required_step_id == required_step_id,
            Step.status == StepStatus.READY,
        )
        .first()
    )


def get_steps_with_required_step_id_no_content(
    db: Session,
) -> list[Step]:
    """required_step_id IS NOT NULL 이면서 StepContent가 없는 Step 들."""
    existing = {row.step_id for row in db.query(StepContent.step_id).all()}
    query = db.query(Step).filter(Step.required_step_id.isnot(None))
    if existing:
        query = query.filter(Step.id.not_in(existing))
    return query.all()


def add_step(db: Session, **fields: Any) -> Step:
    step = Step(**fields)
    db.add(step)
    db.flush()
    return step


def detach_steps_from_parent_in_stages(
    db: Session,
    project_id: UUID,
    stage_ids: Iterable[UUID],
    exclude_step_ids: Iterable[UUID] | None = None,
) -> None:
    """Step.parent_step_id 를 NULL 로 끊는다 (FK 자기참조 회피용)."""
    ids = list(stage_ids)
    if not ids:
        return
    query = db.query(Step).filter(
        Step.project_id == project_id,
        Step.stage_id.in_(ids),
    )
    if exclude_step_ids:
        exc = list(exclude_step_ids)
        if exc:
            query = query.filter(Step.id.notin_(exc))
    query.update({"parent_step_id": None}, synchronize_session=False)


def delete_steps_in_stages(
    db: Session,
    project_id: UUID,
    stage_ids: Iterable[UUID],
    exclude_step_ids: Iterable[UUID] | None = None,
) -> None:
    ids = list(stage_ids)
    if not ids:
        return
    query = db.query(Step).filter(
        Step.project_id == project_id,
        Step.stage_id.in_(ids),
    )
    if exclude_step_ids:
        exc = list(exclude_step_ids)
        if exc:
            query = query.filter(Step.id.notin_(exc))
    query.delete(synchronize_session=False)


def get_first_rs_step_ids_in_stages(
    db: Session, project_id: UUID, stage_ids: Iterable[UUID]
) -> list[UUID]:
    """각 Stage의 첫 번째 Required Step(sequence=1)에 해당하는 Step ID 목록."""
    from app.core.models.required_step import RequiredStep

    ids = list(stage_ids)
    if not ids:
        return []
    return [
        step_id
        for (step_id,) in db.query(Step.id)
        .join(RequiredStep, Step.required_step_id == RequiredStep.id)
        .filter(
            Step.project_id == project_id,
            Step.stage_id.in_(ids),
            RequiredStep.sequence == 1,
        )
        .all()
    ]


def set_status_bulk(steps: Iterable[Step], status: str) -> None:
    for s in steps:
        s.status = status


# ── StepContent ────────────────────────────────────────────────────────


def get_step_content(db: Session, step_id: UUID) -> StepContent | None:
    return db.get(StepContent, step_id)


def add_step_content(
    db: Session,
    step_id: UUID,
    *,
    mentoring: str | None = None,
    dictionary: str | None = None,
) -> StepContent:
    content = StepContent(
        step_id=step_id,
        mentoring=mentoring,
        dictionary=dictionary,
    )
    db.add(content)
    return content


# ── StepTree (closure table) ───────────────────────────────────────────


def insert_closure_self(db: Session, step_id: UUID) -> None:
    db.add(StepTree(ancestor=step_id, descendant=step_id, depth=0))


def insert_closure_with_parent(
    db: Session, step_id: UUID, parent_step_id: UUID | None
) -> None:
    insert_closure_self(db, step_id)
    if parent_step_id is None:
        return
    parent_ancestors = (
        db.query(StepTree).filter(StepTree.descendant == parent_step_id).all()
    )
    for row in parent_ancestors:
        db.add(StepTree(ancestor=row.ancestor, descendant=step_id, depth=row.depth + 1))


def delete_closure_for_descendant(db: Session, step_id: UUID) -> None:
    db.query(StepTree).filter(StepTree.descendant == step_id).delete()


def get_ancestors_ordered(db: Session, step_id: UUID) -> list[StepTree]:
    """depth 오름차순. depth=0(자기 자신) 포함."""
    return (
        db.query(StepTree)
        .filter(StepTree.descendant == step_id)
        .order_by(StepTree.depth.asc())
        .all()
    )
