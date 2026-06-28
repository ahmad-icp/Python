from fastapi import APIRouter, Depends, status

from app.core.security import CurrentUser, Permission, require_permission
from app.modules.platform.schemas import AuditEvent, BackupManifest, BackupRequest, RestorePlan, RestoreRequest, TenantSettings
from app.modules.platform.service import PlatformService

router = APIRouter()


def get_service(current_user: CurrentUser) -> PlatformService:
    return PlatformService(college_id=current_user.college_id, actor_id=current_user.user_id)


@router.get("/audit-logs", response_model=list[AuditEvent])
def audit_logs(current_user: CurrentUser = Depends(require_permission(Permission.PLATFORM_AUDIT_READ))):
    service = get_service(current_user)
    return [service.record_audit("audit.read", "platform")]


@router.get("/activity-history")
def activity_history(current_user: CurrentUser = Depends(require_permission(Permission.PLATFORM_AUDIT_READ))):
    return get_service(current_user).activity_history()


@router.post("/backups", response_model=BackupManifest, status_code=status.HTTP_202_ACCEPTED)
def create_backup(payload: BackupRequest, current_user: CurrentUser = Depends(require_permission(Permission.PLATFORM_BACKUP_MANAGE))):
    return get_service(current_user).create_backup(payload)


@router.post("/restore", response_model=RestorePlan, status_code=status.HTTP_202_ACCEPTED)
def restore(payload: RestoreRequest, current_user: CurrentUser = Depends(require_permission(Permission.PLATFORM_BACKUP_MANAGE))):
    return get_service(current_user).restore_plan(payload)


@router.get("/tenant-settings", response_model=TenantSettings)
def tenant_settings(current_user: CurrentUser = Depends(require_permission(Permission.PLATFORM_SETTINGS_READ))):
    return get_service(current_user).settings()
