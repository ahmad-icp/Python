from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.modules.notifications.models import NotificationChannel, NotificationPriority, NotificationStatus, RecipientType, TemplateEvent

class TemplateCreate(BaseModel):
    code: str = Field(min_length=2, max_length=80)
    name: str = Field(min_length=2, max_length=160)
    event_type: TemplateEvent
    channel: NotificationChannel
    subject_template: str | None = Field(default=None, max_length=200)
    body_template: str = Field(min_length=1)
    is_active: bool = True

class TemplateRead(TemplateCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    college_id: str
    created_at: datetime

class NotificationCreate(BaseModel):
    template_id: str | None = None
    recipient_type: RecipientType
    recipient_id: str
    recipient_address: str | None = None
    channel: NotificationChannel
    event_type: TemplateEvent = TemplateEvent.GENERAL_ANNOUNCEMENT
    priority: NotificationPriority = NotificationPriority.NORMAL
    subject: str | None = Field(default=None, max_length=200)
    body: str | None = None
    scheduled_for: datetime | None = None
    context: dict[str, str] = {}

    @model_validator(mode="after")
    def body_or_template_required(self):
        if not self.template_id and not self.body:
            raise ValueError("body is required when template_id is not provided")
        return self

class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    college_id: str
    template_id: str | None
    recipient_type: RecipientType
    recipient_id: str
    recipient_address: str | None
    channel: NotificationChannel
    event_type: TemplateEvent
    priority: NotificationPriority
    subject: str | None
    body: str
    status: NotificationStatus
    scheduled_for: datetime | None
    sent_at: datetime | None
    retry_count: int
    max_retries: int
    last_error: str | None
    created_by: str
    created_at: datetime

class NotificationList(BaseModel):
    items: list[NotificationRead]
    total: int
    limit: int
    offset: int

class AnnouncementCreate(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    message: str = Field(min_length=1)
    audience: RecipientType
    published_at: datetime | None = None
    expires_at: datetime | None = None

class AnnouncementRead(AnnouncementCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    college_id: str
    created_by: str
    created_at: datetime

class ProcessQueueResult(BaseModel):
    processed: int
    sent: int
    failed: int

class EventNotificationRequest(BaseModel):
    event_type: TemplateEvent
    recipient_type: RecipientType
    recipient_ids: list[str] = Field(min_length=1)
    channel: NotificationChannel = NotificationChannel.IN_APP
    subject: str | None = None
    body: str = Field(min_length=1)
    priority: NotificationPriority = NotificationPriority.NORMAL
