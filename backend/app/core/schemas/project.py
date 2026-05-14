from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProjectCreateRequest(BaseModel):
    name: str | None = None
    duration_months: int
    member_count: int
    description: str | None = None
    constraint: str | None = None
    prompt: str


class ProjectUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    duration_months: int | None = None
    member_count: int | None = None
    is_deleted: bool | None = None
    constraint: str | None = None
    
    


class ProjectResponse(BaseModel):
    project_id: UUID
    name: str
    current_stage_sequence: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class ProjectListItemResponse(BaseModel):
    project_id: UUID
    name: str
    current_stage_sequence: int
    is_deleted: bool
    member_count: int | None = None
    duration_month: int | None = None
    description: str | None = None
    constraint: str | None = None
    prompt: str | None = None
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    projects: list[ProjectListItemResponse]
    total_count: int
    page: int
    size: int
