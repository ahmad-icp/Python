import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def new_uuid() -> str:
    return str(uuid.uuid4())


class ResultStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    LOCKED = "locked"


class ResultOutcome(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    ABSENT = "absent"
    WITHDRAWN = "withdrawn"
    INCOMPLETE = "incomplete"


class ResultAuditAction(StrEnum):
    CALCULATED = "calculated"
    RECALCULATED = "recalculated"
    PUBLISHED = "published"
    LOCKED = "locked"


class GradingPolicy(Base):
    __tablename__ = "grading_policies"
    __table_args__ = (
        UniqueConstraint("college_id", "name", "version", name="uq_grading_policy_name_version"),
        CheckConstraint("minimum_percentage >= 0 AND minimum_percentage <= 100", name="ck_policy_min_percentage"),
        CheckConstraint("grace_marks >= 0", name="ck_policy_grace_non_negative"),
        CheckConstraint("promotion_minimum_percentage >= 0 AND promotion_minimum_percentage <= 100", name="ck_policy_promotion_percentage"),
        Index("ix_grading_policies_college_active", "college_id", "is_active"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    minimum_percentage: Mapped[float] = mapped_column(Numeric(5, 2), default=40, nullable=False)
    grace_marks: Mapped[float] = mapped_column(Numeric(7, 2), default=0, nullable=False)
    promotion_minimum_percentage: Mapped[float] = mapped_column(Numeric(5, 2), default=40, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class StudentResult(Base):
    __tablename__ = "student_results"
    __table_args__ = (
        UniqueConstraint("college_id", "exam_id", "student_id", name="uq_student_result_exam"),
        CheckConstraint("total_marks >= 0 AND obtained_marks >= 0", name="ck_result_marks_non_negative"),
        CheckConstraint("percentage >= 0 AND percentage <= 100", name="ck_result_percentage_range"),
        Index("ix_results_college_exam_status", "college_id", "exam_id", "status"),
        Index("ix_results_college_student_exam", "college_id", "student_id", "exam_id"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    exam_id: Mapped[str] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    policy_id: Mapped[str | None] = mapped_column(ForeignKey("grading_policies.id", ondelete="SET NULL"), index=True)
    status: Mapped[ResultStatus] = mapped_column(Enum(ResultStatus), default=ResultStatus.DRAFT, nullable=False)
    outcome: Mapped[ResultOutcome] = mapped_column(Enum(ResultOutcome), default=ResultOutcome.INCOMPLETE, nullable=False)
    total_marks: Mapped[float] = mapped_column(Numeric(9, 2), default=0, nullable=False)
    obtained_marks: Mapped[float] = mapped_column(Numeric(9, 2), default=0, nullable=False)
    grace_awarded: Mapped[float] = mapped_column(Numeric(7, 2), default=0, nullable=False)
    percentage: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    is_promotion_eligible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    calculated_by: Mapped[str] = mapped_column(String(64), nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    published_by: Mapped[str | None] = mapped_column(String(64))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    locked_by: Mapped[str | None] = mapped_column(String(64))
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    subjects: Mapped[list["SubjectResult"]] = relationship(back_populates="result", cascade="all, delete-orphan", lazy="selectin")


class SubjectResult(Base):
    __tablename__ = "subject_results"
    __table_args__ = (
        UniqueConstraint("result_id", "subject_id", name="uq_subject_result_per_result"),
        Index("ix_subject_results_college_exam_subject", "college_id", "exam_id", "subject_id"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    result_id: Mapped[str] = mapped_column(ForeignKey("student_results.id", ondelete="CASCADE"), nullable=False, index=True)
    exam_id: Mapped[str] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False, index=True)
    credit_hours: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    maximum_marks: Mapped[float] = mapped_column(Numeric(9, 2), nullable=False)
    obtained_marks: Mapped[float] = mapped_column(Numeric(9, 2), nullable=False)
    grace_awarded: Mapped[float] = mapped_column(Numeric(7, 2), default=0, nullable=False)
    percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    outcome: Mapped[ResultOutcome] = mapped_column(Enum(ResultOutcome), nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text)
    result: Mapped[StudentResult] = relationship(back_populates="subjects")


class ResultAuditTrail(Base):
    __tablename__ = "result_audit_trails"
    __table_args__ = (Index("ix_result_audit_college_result_created", "college_id", "result_id", "created_at"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    result_id: Mapped[str | None] = mapped_column(ForeignKey("student_results.id", ondelete="SET NULL"), index=True)
    action: Mapped[ResultAuditAction] = mapped_column(Enum(ResultAuditAction), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(64), nullable=False)
    details: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
