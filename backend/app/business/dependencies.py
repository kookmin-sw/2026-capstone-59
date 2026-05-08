from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.business.services import project_service
from app.core.auth.dependencies import get_current_user
from app.core.database import get_db
from app.core.exceptions import ProjectForbiddenError, StepNotFoundError
from app.core.models.app_user import AppUser as AppUserModel
from app.core.models.project import Project as ProjectModel
from app.core.models.step import Step as StepModel
from app.core.repositories import step as step_repo


def get_owned_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: AppUserModel = Depends(get_current_user),
) -> ProjectModel:
    """프로젝트 존재 여부 + 소유권 검증."""
    project = project_service.get_project_or_raise(db, project_id)
    if project.user_id != current_user.id:
        raise ProjectForbiddenError()
    return project


def get_owned_step(
    step_id: UUID,
    db: Session = Depends(get_db),
    current_user: AppUserModel = Depends(get_current_user),
) -> StepModel:
    """step → project 소유권 검증."""
    step = step_repo.get_step(db, step_id)
    if not step:
        raise StepNotFoundError()

    project = project_service.get_project_or_raise(db, step.project_id)
    if project.user_id != current_user.id:
        raise ProjectForbiddenError()
    return step
