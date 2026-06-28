import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, Index, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def new_uuid() -> str:
    return str(uuid.uuid4())


class ReportType(StrEnum):
    ACADEMIC = "academic"
    ATTENDANCE = "attendance"
    EXAMINATION = "examination"
    RESULT = "result"
    MERIT = "merit"
    FINANCIAL = "financial"
    STUDENT = "student"
    TEACHER = "teacher"


class ExportFormat(StrEnum):
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    EXCEL = "excel"


class ScheduleStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class ScheduledReport(Base):
    __tablename__ = "scheduled_reports"
    __table_args__ = (
        UniqueConstraint("college_id", "name", name="uq_scheduled_report_name_college"),
        Index("ix_scheduled_reports_college_type_status", "college_id", "report_type", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    report_type: Mapped[ReportType] = mapped_column(Enum(ReportType), nullable=False)
    cron_expression: Mapped[str] = mapped_column(String(80), nullable=False)
    export_format: Mapped[ExportFormat] = mapped_column(Enum(ExportFormat), default=ExportFormat.PDF, nullable=False)
    recipients: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    filters_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    status: Mapped[ScheduleStatus] = mapped_column(Enum(ScheduleStatus), default=ScheduleStatus.ACTIVE, nullable=False)
    created_by: Mapped[str] = mapped_column(String(64), nullable=False)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
