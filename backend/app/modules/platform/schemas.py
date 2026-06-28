from datetime import datetime
from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    id: str
    college_id: str
    actor_id: str
    action: str
    resource: str
    resource_id: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
    created_at: datetime


class ActivityEvent(BaseModel):
    id: str
    college_id: str
    actor_id: str
    summary: str
    module: str
    created_at: datetime


class BackupRequest(BaseModel):
    destination: str = Field(pattern="^(local|google_drive)$")
    encrypt: bool = True
    include_uploads: bool = True


class BackupManifest(BaseModel):
    id: str
    college_id: str
    destination: str
    encrypted: bool
    status: str
    object_path: str
    created_at: datetime


class RestoreRequest(BaseModel):
    backup_id: str
    dry_run: bool = True
    restore_uploads: bool = True


class RestorePlan(BaseModel):
    backup_id: str
    dry_run: bool
    steps: list[str]
    status: str


class TenantSettings(BaseModel):
    college_id: str
    name: str
    legal_name: str | None = None
    logo_url: str | None = None
    primary_color: str = "#0f766e"
    locale: str = "en"
    timezone: str = "UTC"
    modules: list[str] = Field(default_factory=list)
    security: dict[str, object] = Field(default_factory=dict)
