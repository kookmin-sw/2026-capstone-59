"""Project / ProjectStage / ProjectRequiredStepStatus repository."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.models.project import Project, ProjectStage
from app.core.models.project_required_step_status import ProjectRequiredStepStatus
from app.core.models.stage import Stage

# ── Project ────────────────────────────────────────────────────────────


def get_active_project_by_id(db: Session, project_id: UUID) -> Project | None:
    return (
        db.query(Project)
        .filter(Project.id == project_id, Project.is_deleted.is_(False))
        .first()
    )


def get_active_project_by_name(
    db: Session, name: str, exclude_id: UUID | None = None
) -> Project | None:
    query = db.query(Project).filter(
        Project.name == name, Project.is_deleted.is_(False)
    )
    if exclude_id is not None:
        query = query.filter(Project.id != exclude_id)
    return query.first()


def get_active_names_by_prefix(db: Session, prefix: str) -> set[str]:
    rows = (
        db.query(Project.name)
        .filter(Project.name.ilike(f"{prefix}%"), Project.is_deleted.is_(False))
        .all()
    )
    return {row[0] for row in rows}


def get_projects_by_user(
    db: Session,
    user_id: UUID | None,
    page: int,
    size: int,
    sort_by: str,
    sort_order: str,
    keyword: str | None = None,
) -> tuple[list[Project], int]:
    query = db.query(Project).filter(
        Project.is_deleted.is_(False),
        Project.user_id == user_id,
    )
    if keyword:
        query = query.filter(Project.name.ilike(f"%{keyword}%"))

    sort_col = getattr(Project, sort_by)
    query = query.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc())

    total_count = query.count()
    projects = query.offset((page - 1) * size).limit(size).all()
    return projects, total_count


def add_project(db: Session, project: Project) -> Project:
    db.add(project)
    db.flush()
    return project


def soft_delete_project(project: Project) -> None:
    project.is_deleted = True


def update_project_fields(project: Project, **fields: Any) -> Project:
    for k, v in fields.items():
        if v is not None:
            setattr(project, k, v)
    return project


# ── ProjectStage ───────────────────────────────────────────────────────


def get_project_stage(
    db: Session, project_id: UUID, stage_id: UUID
) -> ProjectStage | None:
    return db.get(ProjectStage, {"project_id": project_id, "stage_id": stage_id})


def get_active_stage_sequence(db: Session, project_id: UUID) -> int | None:
    """프로젝트의 현재 진행 중인 Stage sequence (is_active=True 중 가장 높은 sequence)."""
    row = (
        db.query(Stage.sequence)
        .join(ProjectStage, ProjectStage.stage_id == Stage.id)
        .filter(
            ProjectStage.project_id == project_id,
            ProjectStage.is_active.is_(True),
        )
        .order_by(Stage.sequence.desc())
        .first()
    )
    return row[0] if row else None


def get_project_stages_with_stage(
    db: Session, project_id: UUID
) -> list[tuple[ProjectStage, Stage]]:
    return (
        db.query(ProjectStage, Stage)
        .join(Stage, Stage.id == ProjectStage.stage_id)
        .filter(ProjectStage.project_id == project_id)
        .order_by(Stage.sequence)
        .all()
    )


def create_initial_project_stages(
    db: Session, project_id: UUID, stage_ids_in_order: Iterable[UUID]
) -> None:
    """첫 번째 Stage만 is_active=True로 일괄 생성."""
    for i, stage_id in enumerate(stage_ids_in_order):
        db.add(
            ProjectStage(
                project_id=project_id,
                stage_id=stage_id,
                is_active=(i == 0),
            )
        )


def deactivate_project_stages(
    db: Session, project_id: UUID, stage_ids: Iterable[UUID]
) -> None:
    db.query(ProjectStage).filter(
        ProjectStage.project_id == project_id,
        ProjectStage.stage_id.in_(list(stage_ids)),
    ).update({"is_active": False}, synchronize_session=False)


def activate_project_stage(db: Session, project_id: UUID, stage_id: UUID) -> None:
    db.query(ProjectStage).filter(
        ProjectStage.project_id == project_id,
        ProjectStage.stage_id == stage_id,
    ).update({"is_active": True}, synchronize_session=False)


# ── ProjectRequiredStepStatus ──────────────────────────────────────────


def get_required_step_status(
    db: Session, project_id: UUID, required_step_id: UUID
) -> ProjectRequiredStepStatus | None:
    return db.get(
        ProjectRequiredStepStatus,
        {"project_id": project_id, "required_step_id": required_step_id},
    )


def get_fulfilled_required_step_ids(db: Session, project_id: UUID) -> set[UUID]:
    return {
        row.required_step_id
        for row in db.query(ProjectRequiredStepStatus).filter_by(
            project_id=project_id, is_fulfilled=True
        )
    }


def create_initial_project_rs_statuses(
    db: Session, project_id: UUID, required_step_ids: Iterable[UUID]
) -> None:
    for rs_id in required_step_ids:
        db.add(
            ProjectRequiredStepStatus(
                project_id=project_id,
                required_step_id=rs_id,
                is_fulfilled=False,
            )
        )


def upsert_required_step_fulfilled(
    db: Session, project_id: UUID, required_step_id: UUID
) -> ProjectRequiredStepStatus:
    record = get_required_step_status(db, project_id, required_step_id)
    if record is None:
        record = ProjectRequiredStepStatus(
            project_id=project_id,
            required_step_id=required_step_id,
        )
        db.add(record)
    record.is_fulfilled = True
    record.fulfilled_at = datetime.now(timezone.utc)
    return record


def unfulfill_by_required_step_ids(
    db: Session, project_id: UUID, required_step_ids: Iterable[UUID]
) -> None:
    """주어진 required_step_id 들의 status 를 일괄 미충족 처리."""
    ids = list(required_step_ids)
    if not ids:
        return
    db.query(ProjectRequiredStepStatus).filter(
        ProjectRequiredStepStatus.project_id == project_id,
        ProjectRequiredStepStatus.required_step_id.in_(ids),
    ).update(
        {"is_fulfilled": False, "fulfilled_at": None},
        synchronize_session=False,
    )
