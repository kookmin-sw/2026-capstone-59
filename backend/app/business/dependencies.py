from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.auth.dependencies import get_current_user
from app.core.database import get_db
from app.core.exceptions import ProjectForbiddenError, ProjectNotFoundError, StepNotFoundError
from app.core.models.app_user import AppUser as AppUserModel
from app.core.models.project import Project as ProjectModel
from app.core.models.step import Step as StepModel


def get_owned_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: AppUserModel = Depends(get_current_user),
) -> ProjectModel:
    """project_id가 경로/쿼리 파라미터로 전달되는 엔드포인트에서
    프로젝트 존재 여부 + 소유권을 한 번에 검증한다."""
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
    if project.user_id != current_user.id:
        raise ProjectForbiddenError()
    return project


def get_owned_step(
    step_id: UUID,
    db: Session = Depends(get_db),
    current_user: AppUserModel = Depends(get_current_user),
) -> StepModel:
    """step_id만 경로 파라미터로 전달되는 엔드포인트에서
    step → project 소유권을 한 번에 검증한다."""
    step = db.get(StepModel, step_id)
    if not step:
        raise StepNotFoundError()

    project = (
        db.query(ProjectModel)
        .filter(
            ProjectModel.id == step.project_id,
            ProjectModel.is_deleted.is_(False),
        )
        .first()
    )
    if not project:
        raise ProjectNotFoundError()
    if project.user_id != current_user.id:
        raise ProjectForbiddenError()
    return step
