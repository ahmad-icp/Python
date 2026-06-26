import uuid
from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint, Date, DateTime, Enum, ForeignKey, Index, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AttendanceStatus(StrEnum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class AttendanceSessionStatus(StrEnum):
    DRAFT = "draft"
    FINALIZED = "finalized"


def new_uuid() -> str:
    return str(uuid.uuid4())


class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"
    __table_args__ = (
        UniqueConstraint("college_id", "section_id", "attendance_date", "time_slot_id", name="uq_attendance_session_section_date_slot"),
        Index("ix_attendance_sessions_college_section_date", "college_id", "section_id", "attendance_date"),
        Index("ix_attendance_sessions_college_teacher_date", "college_id", "teacher_id", "attendance_date"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("academic_sessions.id", ondelete="RESTRICT"), nullable=False, index=True)
    section_id: Mapped[str] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True)
    time_slot_id: Mapped[str | None] = mapped_column(ForeignKey("time_slots.id", ondelete="SET NULL"), index=True)
    timetable_entry_id: Mapped[str | None] = mapped_column(ForeignKey("timetable_entries.id", ondelete="SET NULL"), index=True)
    attendance_date: Mapped[date] = mapped_column(Date, nullable=False)
    teacher_id: Mapped[str] = mapped_column(String(64), nullable=False)
    teacher_name: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[AttendanceSessionStatus] = mapped_column(Enum(AttendanceSessionStatus), default=AttendanceSessionStatus.DRAFT, nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text)
    finalized_by: Mapped[str | None] = mapped_column(String(64))
    finalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    records: Mapped[list["AttendanceRecord"]] = relationship(back_populates="attendance_session", cascade="all, delete-orphan", lazy="selectin")


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint("attendance_session_id", "student_id", name="uq_attendance_record_session_student"),
        CheckConstraint("late_minutes >= 0", name="ck_attendance_late_minutes_non_negative"),
        Index("ix_attendance_records_college_student_date", "college_id", "student_id", "attendance_date"),
        Index("ix_attendance_records_college_status_date", "college_id", "status", "attendance_date"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    attendance_session_id: Mapped[str] = mapped_column(ForeignKey("attendance_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    section_id: Mapped[str] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True)
    attendance_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[AttendanceStatus] = mapped_column(Enum(AttendanceStatus), nullable=False)
    late_minutes: Mapped[int] = mapped_column(default=0, nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text)
    marked_by: Mapped[str] = mapped_column(String(64), nullable=False)
    marked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    attendance_session: Mapped[AttendanceSession] = relationship(back_populates="records")
