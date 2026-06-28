import uuid
from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.students.models import DocumentType, VerificationStatus


class AdmissionMode(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"


class AdmissionStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    DOCUMENTS_PENDING = "documents_pending"
    ELIGIBLE = "eligible"
    MERIT_LISTED = "merit_listed"
    OFFERED = "offered"
    ADMITTED = "admitted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class MeritListStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    LOCKED = "locked"


def new_uuid() -> str:
    return str(uuid.uuid4())


class AdmissionApplication(Base):
    __tablename__ = "admission_applications"
    __table_args__ = (
        UniqueConstraint("college_id", "application_number", name="uq_admission_application_number_per_college"),
        UniqueConstraint("college_id", "normalized_identity", name="uq_admission_identity_per_college"),
        Index("ix_admission_college_status", "college_id", "status"),
        Index("ix_admission_program_session", "college_id", "program", "academic_session"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    application_number: Mapped[str] = mapped_column(String(64), nullable=False)
    mode: Mapped[AdmissionMode] = mapped_column(Enum(AdmissionMode), nullable=False)
    status: Mapped[AdmissionStatus] = mapped_column(Enum(AdmissionStatus), nullable=False, default=AdmissionStatus.SUBMITTED)
    applicant_first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    applicant_last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    normalized_identity: Mapped[str] = mapped_column(String(160), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(32), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    mobile: Mapped[str | None] = mapped_column(String(32))
    address: Mapped[str] = mapped_column(Text, nullable=False)
    guardian_name: Mapped[str] = mapped_column(String(160), nullable=False)
    guardian_mobile: Mapped[str] = mapped_column(String(32), nullable=False)
    guardian_email: Mapped[str | None] = mapped_column(String(255))
    previous_school: Mapped[str | None] = mapped_column(String(180))
    previous_class: Mapped[str | None] = mapped_column(String(80))
    program: Mapped[str] = mapped_column(String(120), nullable=False)
    applying_for_class: Mapped[str] = mapped_column(String(80), nullable=False)
    preferred_section: Mapped[str | None] = mapped_column(String(80))
    academic_session: Mapped[str] = mapped_column(String(40), nullable=False)
    obtained_marks: Mapped[float | None] = mapped_column(Numeric(8, 2))
    total_marks: Mapped[float | None] = mapped_column(Numeric(8, 2))
    merit_score: Mapped[float | None] = mapped_column(Numeric(8, 4))
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    reviewed_by: Mapped[str | None] = mapped_column(String(64))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    decision_reason: Mapped[str | None] = mapped_column(Text)
    admitted_student_id: Mapped[str | None] = mapped_column(String(36), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    documents: Mapped[list["AdmissionDocument"]] = relationship(
        back_populates="application", cascade="all, delete-orphan", lazy="selectin"
    )
    merit_entries: Mapped[list["AdmissionMeritListEntry"]] = relationship(back_populates="application", lazy="selectin")


class AdmissionDocument(Base):
    __tablename__ = "admission_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    application_id: Mapped[str] = mapped_column(ForeignKey("admission_applications.id", ondelete="CASCADE"), nullable=False, index=True)
    document_type: Mapped[DocumentType] = mapped_column(Enum(DocumentType), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    verification_status: Mapped[VerificationStatus] = mapped_column(Enum(VerificationStatus), default=VerificationStatus.PENDING, nullable=False)
    verified_by: Mapped[str | None] = mapped_column(String(64))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[str | None] = mapped_column(Text)

    application: Mapped[AdmissionApplication] = relationship(back_populates="documents")


class AdmissionMeritList(Base):
    __tablename__ = "admission_merit_lists"
    __table_args__ = (
        UniqueConstraint("college_id", "program", "academic_session", "list_number", name="uq_admission_merit_list_program_session_number"),
        Index("ix_admission_merit_list_college_status", "college_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    program: Mapped[str] = mapped_column(String(120), nullable=False)
    academic_session: Mapped[str] = mapped_column(String(40), nullable=False)
    list_number: Mapped[int] = mapped_column(nullable=False)
    minimum_score: Mapped[float | None] = mapped_column(Numeric(8, 4))
    status: Mapped[MeritListStatus] = mapped_column(Enum(MeritListStatus), nullable=False, default=MeritListStatus.DRAFT)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    entries: Mapped[list["AdmissionMeritListEntry"]] = relationship(
        back_populates="merit_list", cascade="all, delete-orphan", lazy="selectin", order_by="AdmissionMeritListEntry.position"
    )


class AdmissionMeritListEntry(Base):
    __tablename__ = "admission_merit_list_entries"
    __table_args__ = (UniqueConstraint("merit_list_id", "application_id", name="uq_admission_merit_list_application"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    merit_list_id: Mapped[str] = mapped_column(ForeignKey("admission_merit_lists.id", ondelete="CASCADE"), nullable=False, index=True)
    application_id: Mapped[str] = mapped_column(ForeignKey("admission_applications.id", ondelete="CASCADE"), nullable=False, index=True)
    position: Mapped[int] = mapped_column(nullable=False)
    score: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False)
    offer_expires_on: Mapped[date | None] = mapped_column(Date)

    merit_list: Mapped[AdmissionMeritList] = relationship(back_populates="entries")
    application: Mapped[AdmissionApplication] = relationship(back_populates="merit_entries")
