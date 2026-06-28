import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def new_uuid() -> str:
    return str(uuid.uuid4())


class GradingSystemType(StrEnum):
    GPA = "gpa"
    PERCENTAGE = "percentage"


class RoundingMode(StrEnum):
    STANDARD = "standard"
    FLOOR = "floor"
    CEIL = "ceil"


class AcademicStanding(StrEnum):
    EXCELLENT = "excellent"
    GOOD = "good"
    SATISFACTORY = "satisfactory"
    PROBATION = "probation"
    FAILING = "failing"


class GradeSystem(Base):
    __tablename__ = "grade_systems"
    __table_args__ = (
        UniqueConstraint("college_id", "scope_type", "scope_id", "name", "version", name="uq_grade_system_scope_version"),
        CheckConstraint("gpa_scale > 0 AND gpa_scale <= 10", name="ck_grade_system_gpa_scale"),
        CheckConstraint("passing_percentage >= 0 AND passing_percentage <= 100", name="ck_grade_system_passing_percentage"),
        CheckConstraint("passing_gpa >= 0", name="ck_grade_system_passing_gpa"),
        CheckConstraint("decimal_places >= 0 AND decimal_places <= 4", name="ck_grade_system_decimal_places"),
        Index("ix_grade_systems_college_scope_active", "college_id", "scope_type", "scope_id", "is_active"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    system_type: Mapped[GradingSystemType] = mapped_column(Enum(GradingSystemType), nullable=False)
    scope_type: Mapped[str] = mapped_column(String(40), default="institution", nullable=False)
    scope_id: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    gpa_scale: Mapped[float] = mapped_column(Numeric(4, 2), default=4, nullable=False)
    passing_percentage: Mapped[float] = mapped_column(Numeric(5, 2), default=40, nullable=False)
    passing_gpa: Mapped[float] = mapped_column(Numeric(4, 2), default=2, nullable=False)
    decimal_places: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    rounding_mode: Mapped[RoundingMode] = mapped_column(Enum(RoundingMode), default=RoundingMode.STANDARD, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    mappings: Mapped[list["GradeMapping"]] = relationship(back_populates="system", cascade="all, delete-orphan", lazy="selectin")


class GradeMapping(Base):
    __tablename__ = "grade_mappings"
    __table_args__ = (
        UniqueConstraint("system_id", "grade", name="uq_grade_mapping_grade"),
        CheckConstraint("min_percentage >= 0 AND min_percentage <= 100", name="ck_grade_mapping_min_pct"),
        CheckConstraint("max_percentage >= 0 AND max_percentage <= 100", name="ck_grade_mapping_max_pct"),
        CheckConstraint("min_percentage <= max_percentage", name="ck_grade_mapping_pct_range"),
        CheckConstraint("grade_point >= 0", name="ck_grade_mapping_grade_point"),
        Index("ix_grade_mappings_system_range", "system_id", "min_percentage", "max_percentage"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    system_id: Mapped[str] = mapped_column(ForeignKey("grade_systems.id", ondelete="CASCADE"), nullable=False, index=True)
    grade: Mapped[str] = mapped_column(String(12), nullable=False)
    min_percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    max_percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    grade_point: Mapped[float] = mapped_column(Numeric(4, 2), default=0, nullable=False)
    remark: Mapped[str | None] = mapped_column(String(160))
    is_passing: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    system: Mapped[GradeSystem] = relationship(back_populates="mappings")


class StudentGradeCalculation(Base):
    __tablename__ = "student_grade_calculations"
    __table_args__ = (
        UniqueConstraint("college_id", "result_id", name="uq_grade_calc_result"),
        CheckConstraint("percentage >= 0 AND percentage <= 100", name="ck_grade_calc_percentage"),
        CheckConstraint("gpa IS NULL OR gpa >= 0", name="ck_grade_calc_gpa"),
        CheckConstraint("cgpa IS NULL OR cgpa >= 0", name="ck_grade_calc_cgpa"),
        Index("ix_grade_calc_college_student", "college_id", "student_id", "calculated_at"),
        Index("ix_grade_calc_college_exam", "college_id", "exam_id", "percentage"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    result_id: Mapped[str] = mapped_column(ForeignKey("student_results.id", ondelete="CASCADE"), nullable=False, index=True)
    exam_id: Mapped[str] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    system_id: Mapped[str] = mapped_column(ForeignKey("grade_systems.id", ondelete="RESTRICT"), nullable=False, index=True)
    percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    grade: Mapped[str] = mapped_column(String(12), nullable=False)
    gpa: Mapped[float | None] = mapped_column(Numeric(4, 2))
    cgpa: Mapped[float | None] = mapped_column(Numeric(4, 2))
    total_credit_hours: Mapped[int | None] = mapped_column(Integer)
    earned_credit_hours: Mapped[int | None] = mapped_column(Integer)
    academic_standing: Mapped[AcademicStanding] = mapped_column(Enum(AcademicStanding), nullable=False)
    is_promotion_eligible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    calculated_by: Mapped[str] = mapped_column(String(64), nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text)
