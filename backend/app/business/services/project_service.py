from uuid import UUID

from sqlalchemy.orm import Session

from app.core.models.project import Project
from app.core.schemas.project import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectResponse,
    ProjectListItemResponse,
)


# Project 생성
def create_project(db: Session, payload: ProjectCreateRequest) -> dict:
    project = Project(
        name=payload.name if payload.name is not None else "새 프로젝트",
        duration_month=payload.duration_months,
        member_count=payload.member_count,
        description=payload.description,
        constraint_text=payload.constraint,
        prompt=payload.prompt,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectResponse(
        project_id=project.id,
        name=project.name,
        current_stage_number=1,
        is_completed=project.is_completed,
        is_deleted=project.is_deleted,
        created_at=project.created_at,
        updated_at=project.updated_at,
    ).model_dump()


# Project 목록 조회
def list_projects(db: Session, page: int, size: int, sort_by: str, sort_order: str, keyword: str | None = None) -> dict:
    ALLOWED_SORT = {"created_at", "updated_at", "name"}
    if sort_by not in ALLOWED_SORT:
        sort_by = "created_at"

    query = db.query(Project).filter(Project.is_deleted == False)  # noqa: E712

    if keyword:
        query = query.filter(Project.name.ilike(f"%{keyword}%"))

    sort_col = getattr(Project, sort_by)
    query = query.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc())

    total_count = query.count()
    projects = query.offset((page - 1) * size).limit(size).all()

    return {
        "projects": [
            ProjectListItemResponse(
                project_id=p.id,
                name=p.name,
                current_stage_number=1,
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


# Project 수정
def update_project(db: Session, project_id: UUID, payload: ProjectUpdateRequest) -> dict | None:
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.is_deleted == False,  # noqa: E712
    ).first()
    if not project:
        return None

    project.name = payload.name if payload.name is not None else project.name
    project.description = payload.description if payload.description is not None else project.description

    db.commit()
    db.refresh(project)
    return ProjectResponse(
        project_id=project.id,
        name=project.name,
        current_stage_number=1,
        is_completed=project.is_completed,
        is_deleted=project.is_deleted,
        created_at=project.created_at,
        updated_at=project.updated_at,
    ).model_dump()

# Project 삭제
def delete_project(db: Session, project_id: UUID) -> bool:
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.is_deleted == False,  # noqa: E712
    ).first()
    if not project:
        return None

    project.is_deleted = True
    db.commit()
    return True