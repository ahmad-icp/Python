from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import CurrentUser, Permission, require_permission
from app.db.session import get_db
from app.modules.notifications.models import NotificationStatus
from app.modules.notifications.schemas import (
    AnnouncementCreate,
    AnnouncementRead,
    EventNotificationRequest,
    NotificationCreate,
    NotificationList,
    NotificationRead,
    ProcessQueueResult,
    TemplateCreate,
    TemplateRead,
)
from app.modules.notifications.service import NotificationService

router = APIRouter()


def get_service(db: Session, current_user: CurrentUser) -> NotificationService:
    return NotificationService(db=db, college_id=current_user.college_id)


@router.post("/templates", response_model=TemplateRead, status_code=status.HTTP_201_CREATED)
def create_template(
    payload: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.NOTIFICATION_MANAGE)),
):
    return get_service(db, current_user).create_template(payload)


@router.get("/templates", response_model=list[TemplateRead])
def list_templates(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.NOTIFICATION_READ)),
):
    return get_service(db, current_user).list_templates()


@router.post("", response_model=NotificationRead, status_code=status.HTTP_201_CREATED)
def queue_notification(
    payload: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.NOTIFICATION_SEND)),
):
    return get_service(db, current_user).queue_notification(payload, current_user.user_id)


@router.get("", response_model=NotificationList)
def list_notifications(
    recipient_id: str | None = None,
    status_filter: NotificationStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.NOTIFICATION_READ)),
):
    items, total = get_service(db, current_user).list_notifications(recipient_id, status_filter, limit, offset)
    return NotificationList(items=items, total=total, limit=limit, offset=offset)


@router.post("/queue/process", response_model=ProcessQueueResult)
def process_queue(
    limit: int = Query(default=50, ge=1, le=250),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.NOTIFICATION_MANAGE)),
):
    return get_service(db, current_user).process_queue(limit)


@router.post("/announcements", response_model=AnnouncementRead, status_code=status.HTTP_201_CREATED)
def create_announcement(
    payload: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.NOTIFICATION_SEND)),
):
    return get_service(db, current_user).create_announcement(payload, current_user.user_id)


@router.post("/events", response_model=list[NotificationRead], status_code=status.HTTP_201_CREATED)
def broadcast_event(
    payload: EventNotificationRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.NOTIFICATION_SEND)),
):
    return get_service(db, current_user).broadcast_event(payload, current_user.user_id)
