"""Stage repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.models.stage import Stage


def get_all_stages_ordered(db: Session) -> list[Stage]:
    return db.query(Stage).order_by(Stage.sequence).all()


def get_stage_by_sequence(db: Session, sequence: int) -> Stage | None:
    return db.query(Stage).filter(Stage.sequence == sequence).first()


def get_stage_ids_after_sequence(db: Session, sequence: int) -> list[UUID]:
    return [
        sid for (sid,) in db.query(Stage.id).filter(Stage.sequence > sequence).all()
    ]
