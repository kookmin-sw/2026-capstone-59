from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.models.project import Project


def _project_to_dict(p: Project) -> dict:
    return {
        "project_id": str(p.id),
        "name": p.name,
        "current_stage_number": 1,
        "is_completed": p.is_completed,
        "is_deleted": p.is_deleted,
        "created_at": p.created_at.isoformat(),
        "updated_at": p.updated_at.isoformat(),
    }


def get_project_or_404(db: Session, project_id: UUID) -> Project:
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.is_deleted == False,  # noqa: E712
    ).first()
    if not project:
        raise HTTPException(
            status_code=404,
            detail={"code": "PROJECT_NOT_FOUND", "message": "프로젝트 없음"},
        )
    return project


def create_project(db: Session, payload: dict) -> dict:
    project = Project(
        name=payload["name"],
        duration_month=payload.get("duration_months"),
        member_count=payload.get("member_count"),
        description=payload.get("description"),
        constraint_text=payload.get("constraint"),
        prompt=payload.get("prompt"),
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return _project_to_dict(project)


def list_projects(db: Session, page: int, size: int, sort_by: str, sort_order: str) -> dict:
    ALLOWED_SORT = {"created_at", "updated_at", "name"}
    if sort_by not in ALLOWED_SORT:
        sort_by = "created_at"

    query = db.query(Project).filter(Project.is_deleted == False)  # noqa: E712
    sort_col = getattr(Project, sort_by)
    query = query.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc())

    total_count = query.count()
    projects = query.offset((page - 1) * size).limit(size).all()

    return {
        "projects": [
            {
                **_project_to_dict(p),
                "member_count": p.member_count,
                "duration_month": p.duration_month,
                "description": p.description,
                "constraint": p.constraint_text,
                "prompt": p.prompt,
            }
            for p in projects
        ],
        "total_count": total_count,
        "page": page,
        "size": size,
    }


def update_project(db: Session, project_id: UUID, payload: dict) -> dict:
    project = get_project_or_404(db, project_id)

    field_map = {"duration_months": "duration_month", "constraint": "constraint_text"}
    for key, value in payload.items():
        setattr(project, field_map.get(key, key), value)

    db.commit()
    db.refresh(project)
    return _project_to_dict(project)


def delete_project(db: Session, project_id: UUID) -> None:
    project = get_project_or_404(db, project_id)
    project.is_deleted = True
    db.commit()