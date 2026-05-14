import json
from uuid import UUID
import secrets


from sqlalchemy.orm import Session

from app.core.enums import StepStatus
from app.core.exceptions import DuplicateProjectNameError, ProjectNotFoundError
from app.core.logging import get_logger
from app.core.models.project import Project as ProjectModel
from app.core.repositories import (
    project as project_repo,
    required_step as required_step_repo,
    stage as stage_repo,
    step as step_repo,
)
from app.core.schemas.project import (
    ProjectCreateRequest,
    ProjectListItemResponse,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
)

logger = get_logger(__name__)

_ALLOWED_SORT_COLUMNS: frozenset[str] = frozenset({"created_at", "updated_at", "name"})


def create_project(
    db: Session, payload: ProjectCreateRequest, user_id: UUID
) -> ProjectResponse:
    if payload.name:
        existing = project_repo.get_active_project_by_name(db, payload.name)
        if existing:
            logger.warning(
                "project: create rejected — duplicate name",
                extra={"user_id": str(user_id), "name": payload.name},
            )
            raise DuplicateProjectNameError()

    project = project_repo.add_project(
        db,
        ProjectModel(
            name=(
                payload.name if payload.name is not None else _generate_default_name(db)
            ),
            user_id=user_id,
            duration_month=payload.duration_months,
            member_count=payload.member_count,
            description=payload.description,
            constraint_text=payload.constraint,
            prompt=payload.prompt,
        ),
    )

    stages = stage_repo.get_all_stages_ordered(db)
    project_repo.create_initial_project_stages(db, project.id, [s.id for s in stages])

    required_steps = required_step_repo.get_all_required_steps(db)
    project_repo.create_initial_project_rs_statuses(
        db, project.id, [rs.id for rs in required_steps]
    )

    _create_initial_steps_for_each_stage(db, project.id)

    db.commit()
    db.refresh(project)
    logger.info(
        "project: created",
        extra={
            "project_id": str(project.id),
            "user_id": str(user_id),
            "stage_count": len(stages),
            "required_step_count": len(required_steps),
        },
    )
    return to_project_response(db, project)


def _create_initial_steps_for_each_stage(db: Session, project_id: UUID) -> None:
    """각 Stage의 첫 번째(sequence=1) Required Step을 루트 Step으로 생성."""
    for rs in required_step_repo.get_first_rs_of_stages(db):
        step = step_repo.add_step(
            db,
            project_id=project_id,
            stage_id=rs.stage_id,
            parent_step_id=None,
            required_step_id=rs.id,
            belonging_required_step_id=None,
            name=rs.name,
            status=StepStatus.READY,
            sort_order=0,
        )
        step_repo.insert_closure_self(db, step.id)
        if rs.default_mentoring is not None or rs.default_dictionary is not None:
            step_repo.add_step_content(
                db,
                step.id,
                mentoring=(
                    json.dumps(rs.default_mentoring, ensure_ascii=False)
                    if rs.default_mentoring
                    else None
                ),
                dictionary=(
                    json.dumps(rs.default_dictionary, ensure_ascii=False)
                    if rs.default_dictionary
                    else None
                ),
            )


def list_projects(
    db: Session,
    page: int,
    size: int,
    sort_by: str,
    sort_order: str,
    keyword: str | None = None,
    user_id: UUID | None = None,
    is_deleted: bool | None = None,
) -> ProjectListResponse:
    if sort_by not in _ALLOWED_SORT_COLUMNS:
        sort_by = "created_at"

    projects, total_count = project_repo.get_projects_by_user(
        db, user_id, page, size, sort_by, sort_order, keyword, is_deleted
    )

    return ProjectListResponse(
        projects=[
            ProjectListItemResponse(
                project_id=p.id,
                name=p.name,
                current_stage_sequence=_get_current_stage_sequence(db, p.id),
                is_deleted=p.is_deleted,
                member_count=p.member_count,
                duration_month=p.duration_month,
                description=p.description,
                constraint=p.constraint_text,
                prompt=p.prompt,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in projects
        ],
        total_count=total_count,
        page=page,
        size=size,
    )


def update_project(
    db: Session, project_id: UUID, payload: ProjectUpdateRequest
) -> ProjectResponse:
    project = project_repo.get_project_by_id(db, project_id)
    if not project:
        logger.warning(
            "project: update rejected — not found",
            extra={"project_id": str(project_id)},
        )
        raise ProjectNotFoundError()

    if payload.name is not None:
        existing = project_repo.get_active_project_by_name(
            db, payload.name, exclude_id=project_id
        )
        if existing:
            logger.warning(
                "project: update rejected — duplicate name",
                extra={"project_id": str(project_id), "name": payload.name},
            )
            raise DuplicateProjectNameError()

    project_repo.update_project_fields(
        project,
        name=payload.name,
        description=payload.description,
        duration_month=payload.duration_months,
        member_count=payload.member_count,
        is_deleted=payload.is_deleted,
        constraint_text=payload.constraint,
    )

    db.commit()
    db.refresh(project)
    logger.info(
        "project: updated",
        extra={
            "project_id": str(project.id),
            "updated_fields": [
                k for k, v in payload.model_dump(exclude_none=True).items()
            ],
        },
    )
    return to_project_response(db, project)


def delete_project(db: Session, project_id: UUID) -> None:
    project = get_project_or_raise(db, project_id)
    project_repo.soft_delete_project(project)
    db.commit()
    logger.info("project: deleted", extra={"project_id": str(project_id)})


def get_project_or_raise(db: Session, project_id: UUID) -> ProjectModel:
    project = project_repo.get_active_project_by_id(db, project_id)
    if not project:
        raise ProjectNotFoundError()
    return project


def _get_current_stage_sequence(db: Session, project_id: UUID) -> int:
    seq = project_repo.get_active_stage_sequence(db, project_id)
    return seq if seq is not None else 1


def to_project_response(db: Session, project: ProjectModel) -> ProjectResponse:
    return ProjectResponse(
        project_id=project.id,
        name=project.name,
        current_stage_sequence=_get_current_stage_sequence(db, project.id),
        is_deleted=project.is_deleted,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _generate_default_name(db: Session) -> str:
    base = "새 프로젝트"
    existing_names = project_repo.get_active_names_by_prefix(db, base)

    if base not in existing_names:
        return base

    count = 2
    while f"{base} ({count})" in existing_names:
        count += 1
    return f"{base} ({count})"


def create_share_token(db: Session, project_id: UUID) -> dict:
    """프로젝트 공유 토큰 생성."""
    project = get_project_or_raise(db, project_id)
    newly_issued = project.share_token is None
    if newly_issued:
        project.share_token = secrets.token_urlsafe(32)
    db.commit()
    db.refresh(project)
    logger.info(
        "project: share token issued",
        extra={"project_id": str(project_id), "is_new_token": newly_issued},
    )
    return {"share_token": project.share_token}


def delete_share_token(db: Session, project_id: UUID) -> None:
    """프로젝트 공유 해제."""
    project = get_project_or_raise(db, project_id)
    project.share_token = None
    db.commit()
    logger.info("project: share token revoked", extra={"project_id": str(project_id)})


def get_project_by_share_token(db: Session, share_token: str) -> ProjectModel:
    """공유 토큰으로 프로젝트 조회 (인증 불필요)."""
    project = (
        db.query(ProjectModel)
        .filter(
            ProjectModel.share_token == share_token,
            ProjectModel.is_deleted == False,  # noqa: E712
        )
        .first()
    )
    if not project:
        logger.warning("project: share token lookup failed — not found")
        raise ProjectNotFoundError()
    return project
