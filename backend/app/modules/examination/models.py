import uuid
from datetime import date, datetime, time
from enum import StrEnum

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, Text, Time, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ExamTypeCode(StrEnum):
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    SESSIONAL_I = "sessional_i"
    SESSIONAL_II = "sessional_ii"
    MIDTERM = "midterm"
    FINAL = "final"
    PRACTICAL = "practical"
    VIVA = "viva"
    MAKEUP = "makeup"


class ExamStatus(StrEnum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    LOCKED = "locked"
    CANCELLED = "cancelled"


class AssessmentComponentType(StrEnum):
    THEORY = "theory"
    PRACTICAL = "practical"
    VIVA = "viva"
    INTERNAL = "internal"
    EXTERNAL = "external"


def new_uuid() -> str:
    return str(uuid.uuid4())


class ExamType(Base):
    __tablename__ = "exam_types"
    __table_args__ = (
        UniqueConstraint("college_id", "code", name="uq_exam_type_code_per_college"),
        Index("ix_exam_types_college_active", "college_id", "is_active"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    code: Mapped[ExamTypeCode] = mapped_column(Enum(ExamTypeCode), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    default_weightage: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Exam(Base):
    __tablename__ = "exams"
    __table_args__ = (
        UniqueConstraint("college_id", "session_id", "section_id", "exam_type_id", "name", name="uq_exam_name_scope"),
        CheckConstraint("start_date <= end_date", name="ck_exam_date_range"),
        Index("ix_exams_college_session_status", "college_id", "session_id", "status"),
        Index("ix_exams_college_section_dates", "college_id", "section_id", "start_date", "end_date"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    exam_type_id: Mapped[str] = mapped_column(ForeignKey("exam_types.id", ondelete="RESTRICT"), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("academic_sessions.id", ondelete="RESTRICT"), nullable=False, index=True)
    program_id: Mapped[str | None] = mapped_column(ForeignKey("programs.id", ondelete="RESTRICT"), index=True)
    class_id: Mapped[str] = mapped_column(ForeignKey("academic_classes.id", ondelete="CASCADE"), nullable=False, index=True)
    section_id: Mapped[str] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[ExamStatus] = mapped_column(Enum(ExamStatus), default=ExamStatus.DRAFT, nullable=False)
    created_by: Mapped[str] = mapped_column(String(64), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    exam_type: Mapped[ExamType] = relationship(lazy="selectin")
    components: Mapped[list["AssessmentComponent"]] = relationship(back_populates="exam", cascade="all, delete-orphan", lazy="selectin")
    schedules: Mapped[list["ExamSchedule"]] = relationship(back_populates="exam", cascade="all, delete-orphan", lazy="selectin")


class AssessmentComponent(Base):
    __tablename__ = "assessment_components"
    __table_args__ = (
        UniqueConstraint("exam_id", "subject_id", "component_type", name="uq_assessment_component_exam_subject_type"),
        CheckConstraint("maximum_marks > 0", name="ck_component_max_positive"),
        CheckConstraint("passing_marks >= 0", name="ck_component_pass_non_negative"),
        CheckConstraint("passing_marks <= maximum_marks", name="ck_component_pass_lte_max"),
        CheckConstraint("weightage >= 0 AND weightage <= 100", name="ck_component_weightage_range"),
        Index("ix_components_college_exam_subject", "college_id", "exam_id", "subject_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    exam_id: Mapped[str] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False, index=True)
    component_type: Mapped[AssessmentComponentType] = mapped_column(Enum(AssessmentComponentType), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    maximum_marks: Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)
    passing_marks: Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)
    weightage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_practical: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    exam: Mapped[Exam] = relationship(back_populates="components")


class ExamHall(Base):
    __tablename__ = "exam_halls"
    __table_args__ = (
        UniqueConstraint("college_id", "code", name="uq_exam_hall_code_per_college"),
        CheckConstraint("capacity > 0", name="ck_exam_hall_capacity_positive"),
        Index("ix_exam_halls_college_active", "college_id", "is_active"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ExamSchedule(Base):
    __tablename__ = "exam_schedules"
    __table_args__ = (
        UniqueConstraint("exam_id", "subject_id", "component_type", name="uq_exam_schedule_subject_component"),
        CheckConstraint("start_time < end_time", name="ck_exam_schedule_time_range"),
        Index("ix_exam_schedules_college_date_hall", "college_id", "exam_date", "hall_id", "start_time", "end_time"),
        Index("ix_exam_schedules_college_section_date", "college_id", "section_id", "exam_date"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    exam_id: Mapped[str] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    section_id: Mapped[str] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False, index=True)
    hall_id: Mapped[str] = mapped_column(ForeignKey("exam_halls.id", ondelete="RESTRICT"), nullable=False, index=True)
    component_type: Mapped[AssessmentComponentType] = mapped_column(Enum(AssessmentComponentType), nullable=False)
    exam_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text)

    exam: Mapped[Exam] = relationship(back_populates="schedules")
    hall: Mapped[ExamHall] = relationship(lazy="selectin")
    invigilators: Mapped[list["InvigilatorAssignment"]] = relationship(back_populates="schedule", cascade="all, delete-orphan", lazy="selectin")


class InvigilatorAssignment(Base):
    __tablename__ = "invigilator_assignments"
    __table_args__ = (
        UniqueConstraint("schedule_id", "teacher_id", name="uq_invigilator_schedule_teacher"),
        Index("ix_invigilators_college_teacher_date", "college_id", "teacher_id", "exam_date"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    schedule_id: Mapped[str] = mapped_column(ForeignKey("exam_schedules.id", ondelete="CASCADE"), nullable=False, index=True)
    teacher_id: Mapped[str] = mapped_column(String(64), nullable=False)
    teacher_name: Mapped[str] = mapped_column(String(160), nullable=False)
    exam_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    assigned_by: Mapped[str] = mapped_column(String(64), nullable=False)

    schedule: Mapped[ExamSchedule] = relationship(back_populates="invigilators")
