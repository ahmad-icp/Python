import uuid
from datetime import date, datetime, time
from enum import IntEnum, StrEnum

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, Enum, ForeignKey, Index, Integer, String, Text, Time, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Weekday(IntEnum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class RoomType(StrEnum):
    CLASSROOM = "classroom"
    LAB = "lab"
    AUDITORIUM = "auditorium"


class TimetableStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class TimetableEntryType(StrEnum):
    LECTURE = "lecture"
    PRACTICAL = "practical"
    LAB = "lab"


def new_uuid() -> str:
    return str(uuid.uuid4())


class Classroom(Base):
    __tablename__ = "classrooms"
    __table_args__ = (
        UniqueConstraint("college_id", "code", name="uq_classroom_code_per_college"),
        CheckConstraint("capacity > 0", name="ck_classroom_capacity_positive"),
        Index("ix_classrooms_college_type", "college_id", "room_type"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    campus_id: Mapped[str | None] = mapped_column(ForeignKey("campuses.id", ondelete="SET NULL"), index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    room_type: Mapped[RoomType] = mapped_column(Enum(RoomType), default=RoomType.CLASSROOM, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class TimeSlot(Base):
    __tablename__ = "time_slots"
    __table_args__ = (
        UniqueConstraint("college_id", "name", name="uq_time_slot_name_per_college"),
        CheckConstraint("start_time < end_time", name="ck_time_slot_range"),
        Index("ix_time_slots_college_order", "college_id", "sort_order"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_break: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class WorkingDay(Base):
    __tablename__ = "working_days"
    __table_args__ = (UniqueConstraint("college_id", "session_id", "weekday", name="uq_working_day_session_weekday"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("academic_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)
    is_working: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    __table_args__ = (
        CheckConstraint("start_date <= end_date", name="ck_calendar_event_date_range"),
        Index("ix_calendar_events_college_session_dates", "college_id", "session_id", "start_date", "end_date"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("academic_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_holiday: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class TimetableVersion(Base):
    __tablename__ = "timetable_versions"
    __table_args__ = (
        UniqueConstraint("college_id", "section_id", "version_number", name="uq_timetable_version_section_number"),
        CheckConstraint("effective_from <= effective_to", name="ck_timetable_effective_range"),
        Index("ix_timetable_versions_college_section_status", "college_id", "section_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("academic_sessions.id", ondelete="RESTRICT"), nullable=False, index=True)
    section_id: Mapped[str] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[TimetableStatus] = mapped_column(Enum(TimetableStatus), default=TimetableStatus.DRAFT, nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date] = mapped_column(Date, nullable=False)
    created_by: Mapped[str] = mapped_column(String(64), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    entries: Mapped[list["TimetableEntry"]] = relationship(back_populates="version", cascade="all, delete-orphan", lazy="selectin")


class TimetableEntry(Base):
    __tablename__ = "timetable_entries"
    __table_args__ = (
        UniqueConstraint("version_id", "weekday", "time_slot_id", name="uq_entry_version_day_slot"),
        Index("ix_timetable_entries_teacher_day_slot", "college_id", "teacher_id", "weekday", "time_slot_id"),
        Index("ix_timetable_entries_room_day_slot", "college_id", "classroom_id", "weekday", "time_slot_id"),
        Index("ix_timetable_entries_section_day_slot", "college_id", "section_id", "weekday", "time_slot_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    version_id: Mapped[str] = mapped_column(ForeignKey("timetable_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("academic_sessions.id", ondelete="RESTRICT"), nullable=False, index=True)
    section_id: Mapped[str] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False, index=True)
    teacher_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    teacher_name: Mapped[str] = mapped_column(String(160), nullable=False)
    classroom_id: Mapped[str] = mapped_column(ForeignKey("classrooms.id", ondelete="RESTRICT"), nullable=False, index=True)
    time_slot_id: Mapped[str] = mapped_column(ForeignKey("time_slots.id", ondelete="RESTRICT"), nullable=False, index=True)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)
    entry_type: Mapped[TimetableEntryType] = mapped_column(Enum(TimetableEntryType), default=TimetableEntryType.LECTURE, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    version: Mapped[TimetableVersion] = relationship(back_populates="entries")
    classroom: Mapped[Classroom] = relationship(lazy="selectin")
    time_slot: Mapped[TimeSlot] = relationship(lazy="selectin")
