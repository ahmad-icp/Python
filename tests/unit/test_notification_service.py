from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.modules.notifications.models import NotificationChannel, NotificationStatus, RecipientType, TemplateEvent
from app.modules.notifications.schemas import EventNotificationRequest, NotificationCreate, TemplateCreate
from app.modules.notifications.service import NotificationService


def db_session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    return Session()


def test_template_rendering_and_queue_processing():
    service = NotificationService(db_session(), "college-a")
    template = service.create_template(
        TemplateCreate(
            code="RESULT_EMAIL",
            name="Result Email",
            event_type=TemplateEvent.RESULT_PUBLISHED,
            channel=NotificationChannel.EMAIL,
            subject_template="Result for {{student}}",
            body_template="Dear {{student}}, your result is published.",
        )
    )
    notification = service.queue_notification(
        NotificationCreate(
            template_id=template.id,
            recipient_type=RecipientType.PARENT,
            recipient_id="parent-1",
            recipient_address="parent@example.edu",
            channel=NotificationChannel.EMAIL,
            context={"student": "Ayesha"},
        ),
        "admin-1",
    )
    assert notification.subject == "Result for Ayesha"
    result = service.process_queue()
    assert result.sent == 1
    assert notification.status == NotificationStatus.SENT


def test_external_delivery_without_address_is_failed_and_retry_counted():
    service = NotificationService(db_session(), "college-a")
    notification = service.queue_notification(
        NotificationCreate(
            recipient_type=RecipientType.PARENT,
            recipient_id="parent-1",
            channel=NotificationChannel.SMS,
            event_type=TemplateEvent.ATTENDANCE_MARKED,
            body="Attendance has been marked.",
        ),
        "admin-1",
    )
    result = service.process_queue()
    assert result.failed == 1
    assert notification.status == NotificationStatus.FAILED
    assert notification.retry_count == 1


def test_event_broadcast_queues_one_notification_per_recipient():
    service = NotificationService(db_session(), "college-a")
    notifications = service.broadcast_event(
        EventNotificationRequest(
            event_type=TemplateEvent.FEE_CHALLAN_ISSUED,
            recipient_type=RecipientType.STUDENT,
            recipient_ids=["student-1", "student-2"],
            body="Your challan is ready.",
        ),
        "admin-1",
    )
    assert len(notifications) == 2
