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
from app.core.schemas.project import (
    ProjectCreateRequest,
    ProjectListItemResponse,
    ProjectResponse,
    ProjectUpdateRequest,
)


def create_project(db: Session, payload: ProjectCreateRequest) -> dict:
    if payload.name:
        existing = (
            db.query(ProjectModel)
            .filter(
                ProjectModel.name == payload.name,
                ProjectModel.is_deleted == False,
            )
            .first()
        )
        if existing:
            raise DuplicateProjectNameError()

    project = ProjectModel(
        name=payload.name if payload.name is not None else "새 프로젝트",
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

    db.commit()
    db.refresh(project)
    return _to_project_response(project)


def list_projects(
    db: Session,
    page: int,
    size: int,
    sort_by: str,
    sort_order: str,
    keyword: str | None = None,
) -> dict:
    ALLOWED_SORT = {"created_at", "updated_at", "name"}
    if sort_by not in ALLOWED_SORT:
        sort_by = "created_at"

    query = db.query(ProjectModel).filter(
        ProjectModel.is_deleted == False
    )  # noqa: E712

    if keyword:
        query = query.filter(ProjectModel.name.ilike(f"%{keyword}%"))

    sort_col = getattr(Project, sort_by)
    query = query.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc())

    total_count = query.count()
    projects = query.offset((page - 1) * size).limit(size).all()

    return {
        "projects": [
            ProjectListItemResponse(
                project_id=p.id,
                name=p.name,
                current_stage_number=_get_current_stage_number(db, p.id),
                is_completed=p.is_completed,
                is_deleted=p.is_deleted,
                member_count=p.member_count,
                duration_month=p.duration_month,
                description=p.description,
                constraint=p.constraint_text,
                prompt=p.prompt,
                created_at=p.created_at,
                updated_at=p.updated_at,
            ).model_dump()
            for p in projects
        ],
        "total_count": total_count,
        "page": page,
        "size": size,
    }


def update_project(
    db: Session, project_id: UUID, payload: ProjectUpdateRequest
) -> dict:
    project = _get_project_or_raise(db, project_id)

    if payload.name is not None:
        # 이름 중복 체크
        existing = (
            db.query(ProjectModel)
            .filter(
                ProjectModel.name == payload.name,
                ProjectModel.id != project_id,
                ProjectModel.is_deleted == False,  # noqa: E712
            )
            .first()
        )
        if existing:
            raise DuplicateProjectNameError()
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description

    db.commit()
    db.refresh(project)
    return _to_project_response(project)


def delete_project(db: Session, project_id: UUID) -> None:
    project = _get_project_or_raise(db, project_id)
    project.is_deleted = True
    db.commit()


def _get_project_or_raise(db: Session, project_id: UUID) -> Project:
    project = (
        db.query(ProjectModel)
        .filter(
            ProjectModel.id == project_id,
            ProjectModel.is_deleted == False,  # noqa: E712
        )
        .first()
    )
    if not project:
        raise ProjectNotFoundError()
    return project


def _get_current_stage_number(db: Session, project_id: UUID) -> int:
    """is_active=True인 Stage의 sequence를 반환."""
    row = (
        db.query(StageModel.sequence)
        .join(ProjectStage, ProjectStageModel.stage_id == Stage.id)
        .filter(
            ProjectStageModel.project_id == project_id,
            ProjectStageModel.is_active == True,  # noqa: E712
        )
        .order_by(StageModel.sequence)
        .first()
    )
    return row[0] if row else 1


def _to_project_response(project: Project) -> dict:
    return ProjectResponse(
        project_id=project.id,
        name=project.name,
        current_stage_number=1,
        is_completed=project.is_completed,
        is_deleted=project.is_deleted,
        created_at=project.created_at,
        updated_at=project.updated_at,
    ).model_dump()
