from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.modules.notifications.models import (
    Announcement,
    Notification,
    NotificationDeliveryAttempt,
    NotificationStatus,
    NotificationTemplate,
)
from app.modules.notifications.schemas import (
    AnnouncementCreate,
    EventNotificationRequest,
    NotificationCreate,
    ProcessQueueResult,
    TemplateCreate,
)


class NotificationService:
    def __init__(self, db: Session, college_id: str) -> None:
        self.db = db
        self.college_id = college_id

    def create_template(self, payload: TemplateCreate) -> NotificationTemplate:
        template = NotificationTemplate(college_id=self.college_id, **payload.model_dump())
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def list_templates(self) -> list[NotificationTemplate]:
        return list(
            self.db.scalars(
                select(NotificationTemplate)
                .where(NotificationTemplate.college_id == self.college_id)
                .order_by(NotificationTemplate.name)
            ).all()
        )

    def queue_notification(self, payload: NotificationCreate, created_by: str) -> Notification:
        subject = payload.subject
        body = payload.body
        template = None
        if payload.template_id:
            template = self.db.get(NotificationTemplate, payload.template_id)
            if not template or template.college_id != self.college_id or not template.is_active:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification template not found")
            subject = self._render(template.subject_template, payload.context) if template.subject_template else subject
            body = self._render(template.body_template, payload.context)
        if not body:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Notification body is required")
        notification = Notification(
            college_id=self.college_id,
            template_id=template.id if template else None,
            recipient_type=payload.recipient_type,
            recipient_id=payload.recipient_id,
            recipient_address=payload.recipient_address,
            channel=payload.channel,
            event_type=payload.event_type if not template else template.event_type,
            priority=payload.priority,
            subject=subject,
            body=body,
            scheduled_for=payload.scheduled_for,
            status=NotificationStatus.SCHEDULED if payload.scheduled_for else NotificationStatus.QUEUED,
            created_by=created_by,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def list_notifications(
        self,
        recipient_id: str | None,
        status_filter: NotificationStatus | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Notification], int]:
        query = select(Notification).where(Notification.college_id == self.college_id)
        if recipient_id:
            query = query.where(Notification.recipient_id == recipient_id)
        if status_filter:
            query = query.where(Notification.status == status_filter)
        total = self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
        items = self.db.scalars(query.order_by(Notification.created_at.desc()).limit(limit).offset(offset)).unique().all()
        return list(items), total

    def process_queue(self, limit: int = 50) -> ProcessQueueResult:
        now = datetime.now(UTC)
        queued = self.db.scalars(
            select(Notification)
            .where(
                Notification.college_id == self.college_id,
                Notification.status.in_([NotificationStatus.QUEUED, NotificationStatus.SCHEDULED, NotificationStatus.FAILED]),
                Notification.retry_count < Notification.max_retries,
                or_(Notification.scheduled_for.is_(None), Notification.scheduled_for <= now),
            )
            .order_by(Notification.priority.desc(), Notification.created_at)
            .limit(limit)
        ).all()
        sent = 0
        failed = 0
        for notification in queued:
            provider = self._provider_for(notification.channel.value)
            if notification.recipient_address or notification.channel.value == "in_app":
                notification.status = NotificationStatus.SENT
                notification.sent_at = now
                notification.last_error = None
                sent += 1
                attempt_status = NotificationStatus.SENT
                response_message = "Accepted by local delivery adapter"
            else:
                notification.retry_count += 1
                notification.status = NotificationStatus.FAILED
                notification.last_error = "Recipient address is required for external delivery channels"
                failed += 1
                attempt_status = NotificationStatus.FAILED
                response_message = notification.last_error
            self.db.add(
                NotificationDeliveryAttempt(
                    notification_id=notification.id,
                    provider=provider,
                    status=attempt_status,
                    response_code="LOCAL-ACCEPTED" if attempt_status == NotificationStatus.SENT else "LOCAL-VALIDATION-FAILED",
                    response_message=response_message,
                )
            )
        self.db.commit()
        return ProcessQueueResult(processed=len(queued), sent=sent, failed=failed)

    def create_announcement(self, payload: AnnouncementCreate, created_by: str) -> Announcement:
        announcement = Announcement(college_id=self.college_id, created_by=created_by, **payload.model_dump())
        self.db.add(announcement)
        self.db.commit()
        self.db.refresh(announcement)
        return announcement

    def broadcast_event(self, payload: EventNotificationRequest, created_by: str) -> list[Notification]:
        notifications: list[Notification] = []
        for recipient_id in payload.recipient_ids:
            notifications.append(
                self.queue_notification(
                    NotificationCreate(
                        recipient_type=payload.recipient_type,
                        recipient_id=recipient_id,
                        channel=payload.channel,
                        event_type=payload.event_type,
                        priority=payload.priority,
                        subject=payload.subject,
                        body=payload.body,
                    ),
                    created_by,
                )
            )
        return notifications

    def _render(self, template: str | None, context: dict[str, str]) -> str | None:
        if template is None:
            return None
        rendered = template
        for key, value in context.items():
            rendered = rendered.replace("{{" + key + "}}", value)
        return rendered

    def _provider_for(self, channel: str) -> str:
        return {
            "email": "smtp",
            "sms": "sms-gateway",
            "whatsapp": "whatsapp-business",
            "push": "web-push",
            "in_app": "in-app",
        }[channel]
