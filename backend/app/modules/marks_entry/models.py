import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Index, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MarksBatchStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    LOCKED = "locked"


class MarksAuditAction(StrEnum):
    CREATED = "created"
    UPDATED = "updated"
    SUBMITTED = "submitted"
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    MODERATED = "moderated"
    RECHECKED = "rechecked"
    IMPORTED = "imported"


def new_uuid() -> str:
    return str(uuid.uuid4())


class MarksEntryBatch(Base):
    __tablename__ = "marks_entry_batches"
    __table_args__ = (
        UniqueConstraint("college_id", "exam_id", "subject_id", "component_id", "section_id", name="uq_marks_batch_scope"),
        Index("ix_marks_batches_college_exam_status", "college_id", "exam_id", "status"),
        Index("ix_marks_batches_college_section_subject", "college_id", "section_id", "subject_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    exam_id: Mapped[str] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    section_id: Mapped[str] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False, index=True)
    component_id: Mapped[str] = mapped_column(ForeignKey("assessment_components.id", ondelete="RESTRICT"), nullable=False, index=True)
    status: Mapped[MarksBatchStatus] = mapped_column(Enum(MarksBatchStatus), default=MarksBatchStatus.DRAFT, nullable=False)
    created_by: Mapped[str] = mapped_column(String(64), nullable=False)
    submitted_by: Mapped[str | None] = mapped_column(String(64))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    locked_by: Mapped[str | None] = mapped_column(String(64))
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    unlocked_by: Mapped[str | None] = mapped_column(String(64))
    unlocked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    unlock_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    entries: Mapped[list["MarksEntry"]] = relationship(back_populates="batch", cascade="all, delete-orphan", lazy="selectin")


class MarksEntry(Base):
    __tablename__ = "marks_entries"
    __table_args__ = (
        UniqueConstraint("batch_id", "student_id", name="uq_marks_entry_batch_student"),
        UniqueConstraint("college_id", "exam_id", "subject_id", "component_id", "student_id", name="uq_marks_entry_exam_subject_component_student"),
        CheckConstraint("marks_obtained >= 0", name="ck_marks_obtained_non_negative"),
        CheckConstraint("moderation_marks >= -1000 AND moderation_marks <= 1000", name="ck_marks_moderation_range"),
        Index("ix_marks_entries_college_student_exam", "college_id", "student_id", "exam_id"),
        Index("ix_marks_entries_college_exam_subject", "college_id", "exam_id", "subject_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    batch_id: Mapped[str] = mapped_column(ForeignKey("marks_entry_batches.id", ondelete="CASCADE"), nullable=False, index=True)
    exam_id: Mapped[str] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    section_id: Mapped[str] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False, index=True)
    component_id: Mapped[str] = mapped_column(ForeignKey("assessment_components.id", ondelete="RESTRICT"), nullable=False, index=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    marks_obtained: Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)
    moderation_marks: Mapped[float] = mapped_column(Numeric(7, 2), default=0, nullable=False)
    recheck_notes: Mapped[str | None] = mapped_column(Text)
    remarks: Mapped[str | None] = mapped_column(Text)
    entered_by: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_by: Mapped[str | None] = mapped_column(String(64))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    batch: Mapped[MarksEntryBatch] = relationship(back_populates="entries")


class MarksAuditTrail(Base):
    __tablename__ = "marks_audit_trails"
    __table_args__ = (
        Index("ix_marks_audit_college_batch_created", "college_id", "batch_id", "created_at"),
        Index("ix_marks_audit_college_entry_created", "college_id", "entry_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    batch_id: Mapped[str] = mapped_column(ForeignKey("marks_entry_batches.id", ondelete="CASCADE"), nullable=False, index=True)
    entry_id: Mapped[str | None] = mapped_column(ForeignKey("marks_entries.id", ondelete="SET NULL"), index=True)
    action: Mapped[MarksAuditAction] = mapped_column(Enum(MarksAuditAction), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(64), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text)
    new_value: Mapped[str | None] = mapped_column(Text)
    reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
