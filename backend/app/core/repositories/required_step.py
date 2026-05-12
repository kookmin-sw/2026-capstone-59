"""RequiredStep repository."""

from __future__ import annotations

from collections.abc import Iterable
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.models.required_step import RequiredStep


def get_required_step(db: Session, rs_id: UUID) -> RequiredStep | None:
    return db.get(RequiredStep, rs_id)


def get_all_required_steps(db: Session) -> list[RequiredStep]:
    return db.query(RequiredStep).all()


def get_required_steps_in_stage(db: Session, stage_id: UUID) -> list[RequiredStep]:
    return (
        db.query(RequiredStep)
        .filter(RequiredStep.stage_id == stage_id)
        .order_by(RequiredStep.sequence)
        .all()
    )


def get_first_rs_of_stages(db: Session) -> list[RequiredStep]:
    """각 Stage 의 sequence=1 인 Required Step 들."""
    return db.query(RequiredStep).filter(RequiredStep.sequence == 1).all()


def get_required_step_ids_in_stages(
    db: Session, stage_ids: Iterable[UUID]
) -> list[UUID]:
    ids = list(stage_ids)
    if not ids:
        return []
    return [
        rs_id
        for (rs_id,) in db.query(RequiredStep.id)
        .filter(RequiredStep.stage_id.in_(ids))
        .all()
    ]


def get_required_step_ids_from_sequence(
    db: Session, stage_id: UUID, min_sequence: int
) -> list[UUID]:
    """같은 Stage 안에서 sequence >= min_sequence 인 Required Step ID 들."""
    return [
        rs_id
        for (rs_id,) in db.query(RequiredStep.id)
        .filter(
            RequiredStep.stage_id == stage_id,
            RequiredStep.sequence >= min_sequence,
        )
        .all()
    ]


def get_required_step_ids_before_sequence(
    db: Session, stage_id: UUID, max_sequence: int
) -> list[UUID]:
    """같은 Stage 안에서 sequence < max_sequence 인 Required Step ID 들."""
    return [
        rs_id
        for (rs_id,) in db.query(RequiredStep.id)
        .filter(
            RequiredStep.stage_id == stage_id,
            RequiredStep.sequence < max_sequence,
        )
        .all()
    ]
