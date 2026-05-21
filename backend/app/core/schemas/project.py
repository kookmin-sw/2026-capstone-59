from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectCreateRequest(BaseModel):
    name: str | None = None
    duration_months: int
    member_count: int
    description: str | None = None
    constraints: list[str] | None = None
    prompt: str


class ProjectUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = Field(default=None, max_length=100)
    new_constraints: list[str] | None = None  
    is_deleted: bool | None = None
    
    

class ProjectResponse(BaseModel):
    project_id: UUID
    name: str
    current_stage_sequence: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    prompt: str
    duration_month: int
    member_count: int
    description: str | None = None
    constraints: list[str] | None = None


class ProjectListItemResponse(BaseModel):
    project_id: UUID
    name: str
    current_stage_sequence: int
    is_deleted: bool
    member_count: int | None = None
    duration_month: int | None = None
    description: str | None = None
    constraints: list[str] | None = None
    prompt: str | None = None
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    projects: list[ProjectListItemResponse]
    total_count: int
    page: int
    size: int


class DesignExportStartRequest(BaseModel):
    """POST /projects/{project_id}/design-export-start 요청."""
    job_id: UUID  # 클라이언트가 생성 — 응답 안 기다리고 곧장 폴링 가능
    selected_step_ids: list[UUID]


class DesignExportStartResponse(BaseModel):
    """POST /projects/{project_id}/design-export-start 응답."""
    job_id: UUID
    status: str  # pending / done / error


class DesignExportJobResponse(BaseModel):
    """GET /projects/{project_id}/design-export-jobs/{job_id} 폴링 응답."""
    status: str  # pending / done / error
    markdown: str | None = None
    filename: str | None = None
    error_code: str | None = None
    is_complete: bool
