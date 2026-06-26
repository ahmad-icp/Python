import uuid
from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, Enum, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SessionStatus(StrEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    ARCHIVED = "archived"


class AssignmentStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


def new_uuid() -> str:
    return str(uuid.uuid4())


class Institution(Base):
    __tablename__ = "institutions"
    __table_args__ = (UniqueConstraint("college_id", "code", name="uq_institution_code_per_college"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    address: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    campuses: Mapped[list["Campus"]] = relationship(back_populates="institution", cascade="all, delete-orphan", lazy="selectin")
    departments: Mapped[list["Department"]] = relationship(back_populates="institution", cascade="all, delete-orphan", lazy="selectin")


class Campus(Base):
    __tablename__ = "campuses"
    __table_args__ = (UniqueConstraint("institution_id", "code", name="uq_campus_code_per_institution"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    institution_id: Mapped[str] = mapped_column(ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    address: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    institution: Mapped[Institution] = relationship(back_populates="campuses")
    departments: Mapped[list["Department"]] = relationship(back_populates="campus", lazy="selectin")


class Department(Base):
    __tablename__ = "departments"
    __table_args__ = (UniqueConstraint("college_id", "code", name="uq_department_code_per_college"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    institution_id: Mapped[str] = mapped_column(ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    campus_id: Mapped[str | None] = mapped_column(ForeignKey("campuses.id", ondelete="SET NULL"), index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    institution: Mapped[Institution] = relationship(back_populates="departments")
    campus: Mapped[Campus | None] = relationship(back_populates="departments")
    programs: Mapped[list["Program"]] = relationship(back_populates="department", lazy="selectin")


class AcademicSession(Base):
    __tablename__ = "academic_sessions"
    __table_args__ = (
        UniqueConstraint("college_id", "name", name="uq_academic_session_name_per_college"),
        CheckConstraint("start_date < end_date", name="ck_academic_session_date_range"),
        Index("ix_academic_sessions_college_status", "college_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[SessionStatus] = mapped_column(Enum(SessionStatus), nullable=False, default=SessionStatus.PLANNED)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Program(Base):
    __tablename__ = "programs"
    __table_args__ = (UniqueConstraint("college_id", "code", name="uq_program_code_per_college"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    department_id: Mapped[str] = mapped_column(ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    duration_years: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    department: Mapped[Department] = relationship(back_populates="programs")
    classes: Mapped[list["AcademicClass"]] = relationship(back_populates="program", lazy="selectin")


class AcademicClass(Base):
    __tablename__ = "academic_classes"
    __table_args__ = (
        UniqueConstraint("college_id", "program_id", "session_id", "name", name="uq_class_name_program_session"),
        Index("ix_classes_college_program_session", "college_id", "program_id", "session_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    program_id: Mapped[str] = mapped_column(ForeignKey("programs.id", ondelete="RESTRICT"), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("academic_sessions.id", ondelete="RESTRICT"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    program: Mapped[Program] = relationship(back_populates="classes")
    session: Mapped[AcademicSession] = relationship(lazy="selectin")
    sections: Mapped[list["Section"]] = relationship(back_populates="academic_class", cascade="all, delete-orphan", lazy="selectin")


class Section(Base):
    __tablename__ = "sections"
    __table_args__ = (
        UniqueConstraint("class_id", "name", name="uq_section_name_per_class"),
        CheckConstraint("capacity > 0", name="ck_section_capacity_positive"),
        CheckConstraint("enrolled_count >= 0", name="ck_section_enrolled_non_negative"),
        CheckConstraint("enrolled_count <= capacity", name="ck_section_capacity_not_exceeded"),
        Index("ix_sections_college_class", "college_id", "class_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    class_id: Mapped[str] = mapped_column(ForeignKey("academic_classes.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    enrolled_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    room: Mapped[str | None] = mapped_column(String(80))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    academic_class: Mapped[AcademicClass] = relationship(back_populates="sections")


class Subject(Base):
    __tablename__ = "subjects"
    __table_args__ = (UniqueConstraint("college_id", "code", name="uq_subject_code_per_college"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    department_id: Mapped[str | None] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"), index=True)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    credit_hours: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    weekly_periods: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_elective: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    prerequisites: Mapped[list["SubjectPrerequisite"]] = relationship(
        foreign_keys="SubjectPrerequisite.subject_id", cascade="all, delete-orphan", lazy="selectin"
    )


class SubjectPrerequisite(Base):
    __tablename__ = "subject_prerequisites"
    __table_args__ = (UniqueConstraint("subject_id", "prerequisite_subject_id", name="uq_subject_prerequisite"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    prerequisite_subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False, index=True)


class SubjectGroup(Base):
    __tablename__ = "subject_groups"
    __table_args__ = (UniqueConstraint("college_id", "name", name="uq_subject_group_name_per_college"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class ElectiveGroup(Base):
    __tablename__ = "elective_groups"
    __table_args__ = (UniqueConstraint("class_id", "name", name="uq_elective_group_name_per_class"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    class_id: Mapped[str] = mapped_column(ForeignKey("academic_classes.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    min_subjects: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    max_subjects: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class SubjectAllocation(Base):
    __tablename__ = "subject_allocations"
    __table_args__ = (UniqueConstraint("class_id", "subject_id", name="uq_subject_allocation_class_subject"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    class_id: Mapped[str] = mapped_column(ForeignKey("academic_classes.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False, index=True)
    subject_group_id: Mapped[str | None] = mapped_column(ForeignKey("subject_groups.id", ondelete="SET NULL"), index=True)
    elective_group_id: Mapped[str | None] = mapped_column(ForeignKey("elective_groups.id", ondelete="SET NULL"), index=True)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    weekly_periods: Mapped[int] = mapped_column(Integer, nullable=False)

    academic_class: Mapped[AcademicClass] = relationship(lazy="selectin")
    subject: Mapped[Subject] = relationship(lazy="selectin")


class TeacherAssignment(Base):
    __tablename__ = "teacher_assignments"
    __table_args__ = (
        UniqueConstraint("section_id", "subject_id", "teacher_id", name="uq_teacher_assignment_section_subject_teacher"),
        Index("ix_teacher_assignments_teacher_status", "college_id", "teacher_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    teacher_id: Mapped[str] = mapped_column(String(64), nullable=False)
    teacher_name: Mapped[str] = mapped_column(String(160), nullable=False)
    section_id: Mapped[str] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False, index=True)
    weekly_periods: Mapped[int] = mapped_column(Integer, nullable=False)
    max_weekly_periods: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    status: Mapped[AssignmentStatus] = mapped_column(Enum(AssignmentStatus), default=AssignmentStatus.ACTIVE, nullable=False)

    section: Mapped[Section] = relationship(lazy="selectin")
    subject: Mapped[Subject] = relationship(lazy="selectin")


class PromotionRule(Base):
    __tablename__ = "promotion_rules"
    __table_args__ = (UniqueConstraint("from_class_id", "to_class_id", name="uq_promotion_rule_from_to"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    from_class_id: Mapped[str] = mapped_column(ForeignKey("academic_classes.id", ondelete="CASCADE"), nullable=False, index=True)
    to_class_id: Mapped[str] = mapped_column(ForeignKey("academic_classes.id", ondelete="CASCADE"), nullable=False, index=True)
    minimum_attendance_percentage: Mapped[int] = mapped_column(Integer, default=75, nullable=False)
    minimum_passing_percentage: Mapped[int] = mapped_column(Integer, default=40, nullable=False)
    require_all_mandatory_subjects: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class AcademicArchive(Base):
    __tablename__ = "academic_archives"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    session_id: Mapped[str | None] = mapped_column(String(36), index=True)
    snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    archived_by: Mapped[str] = mapped_column(String(64), nullable=False)
    archived_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
