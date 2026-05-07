import json
import uuid
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateProjectNameError, ProjectNotFoundError
from app.core.models.project import Project as ProjectModel
from app.core.models.project import ProjectStage as ProjectStageModel
from app.core.models.project_required_step_status import (
    ProjectRequiredStepStatus as ProjectRequiredStepStatusModel,
)
from app.core.models.required_step import RequiredStep as RequiredStepModel
from app.core.models.stage import Stage as StageModel
from app.core.models.step import Step as StepModel
from app.core.models.step import StepContent as StepContentModel
from app.core.models.step import StepTree as StepTreeModel
from app.core.enums import StepStatus
from app.core.schemas.project import (
    ProjectCreateRequest,
    ProjectListItemResponse,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
)

_ALLOWED_SORT_COLUMNS: frozenset[str] = frozenset({"created_at", "updated_at", "name"})


def create_project(
    db: Session, payload: ProjectCreateRequest, user_id: UUID
) -> ProjectResponse:
    if payload.name:
        existing = (
            db.query(ProjectModel)
            .filter(
                ProjectModel.name == payload.name,
                ProjectModel.is_deleted.is_(False),
            )
            .first()
        )
        if existing:
            raise DuplicateProjectNameError()

    project = ProjectModel(
        name=payload.name if payload.name is not None else _generate_default_name(db),
        user_id=user_id,
        duration_month=payload.duration_months,
        member_count=payload.member_count,
        description=payload.description,
        constraint_text=payload.constraint,
        prompt=payload.prompt,
    )
    db.add(project)
    db.flush()

    stages = db.query(StageModel).order_by(StageModel.sequence).all()
    for i, stage in enumerate(stages):
        db.add(
            ProjectStageModel(
                project_id=project.id,
                stage_id=stage.id,
                is_active=(i == 0),
            )
        )

    required_steps = db.query(RequiredStepModel).all()
    for rs in required_steps:
        db.add(
            ProjectRequiredStepStatusModel(
                project_id=project.id,
                required_step_id=rs.id,
                is_fulfilled=False,
            )
        )

    _create_initial_steps_for_each_stage(db, project.id)

    db.commit()
    db.refresh(project)
    return _to_project_response(db, project)


def _create_initial_steps_for_each_stage(db: Session, project_id: UUID) -> None:
    """각 Stage의 첫 번째(sequence=1) Required Step을 루트 Step으로 생성."""
    first_required_steps = (
        db.query(RequiredStepModel).filter(RequiredStepModel.sequence == 1).all()
    )
    for rs in first_required_steps:
        step = StepModel(
            id=uuid.uuid4(),
            project_id=project_id,
            stage_id=rs.stage_id,
            parent_step_id=None,
            required_step_id=rs.id,
            belonging_required_step_id=None,
            name=rs.name,
            status=StepStatus.READY,
            sort_order=0,
        )
        db.add(step)
        db.flush()
        db.add(StepTreeModel(ancestor=step.id, descendant=step.id, depth=0))
        if rs.default_mentoring is not None or rs.default_dictionary is not None:
            db.add(StepContentModel(
                step_id=step.id,
                mentoring=json.dumps(rs.default_mentoring, ensure_ascii=False) if rs.default_mentoring else None,
                dictionary=json.dumps(rs.default_dictionary, ensure_ascii=False) if rs.default_dictionary else None,
            ))


def list_projects(
    db: Session,
    page: int,
    size: int,
    sort_by: str,
    sort_order: str,
    keyword: str | None = None,
    user_id: UUID | None = None,
) -> ProjectListResponse:
    if sort_by not in _ALLOWED_SORT_COLUMNS:
        sort_by = "created_at"

    query = db.query(ProjectModel).filter(
        ProjectModel.is_deleted.is_(False),
        ProjectModel.user_id == user_id,
    )

    if keyword:
        query = query.filter(ProjectModel.name.ilike(f"%{keyword}%"))

    sort_col = getattr(ProjectModel, sort_by)
    query = query.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc())

    total_count = query.count()
    projects = query.offset((page - 1) * size).limit(size).all()

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
    project = _get_project_or_raise(db, project_id)

    if payload.name is not None:
        existing = (
            db.query(ProjectModel)
            .filter(
                ProjectModel.name == payload.name,
                ProjectModel.id != project_id,
                ProjectModel.is_deleted.is_(False),
            )
            .first()
        )
        if existing:
            raise DuplicateProjectNameError()
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    if payload.duration_months is not None:
        project.duration_month = payload.duration_months
    if payload.member_count is not None:
        project.member_count = payload.member_count

    db.commit()
    db.refresh(project)
    return _to_project_response(db, project)


def delete_project(db: Session, project_id: UUID) -> None:
    project = _get_project_or_raise(db, project_id)
    project.is_deleted = True
    db.commit()


def _get_project_or_raise(db: Session, project_id: UUID) -> ProjectModel:
    project = (
        db.query(ProjectModel)
        .filter(
            ProjectModel.id == project_id,
            ProjectModel.is_deleted.is_(False),
        )
        .first()
    )
    if not project:
        raise ProjectNotFoundError()
    return project


def _get_current_stage_sequence(db: Session, project_id: UUID) -> int:
    """is_active=True인 Stage의 sequence를 반환."""
    row = (
        db.query(StageModel.sequence)
        .join(ProjectStageModel, ProjectStageModel.stage_id == StageModel.id)
        .filter(
            ProjectStageModel.project_id == project_id,
            ProjectStageModel.is_active.is_(True),
        )
        .order_by(StageModel.sequence)
        .first()
    )
    return row[0] if row else 1


def _to_project_response(db: Session, project: ProjectModel) -> ProjectResponse:
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
    existing_names = (
        db.query(ProjectModel.name)
        .filter(
            ProjectModel.name.ilike(f"{base}%"),
            ProjectModel.is_deleted.is_(False),
        )
        .all()
    )
    existing_names = {row[0] for row in existing_names}

    if base not in existing_names:
        return base

    count = 2
    while f"{base} ({count})" in existing_names:
        count += 1
    return f"{base} ({count})"
