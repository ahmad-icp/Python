import uuid
from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class StudentStatus(StrEnum):
    APPLICANT = "applicant"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    WITHDRAWN = "withdrawn"
    GRADUATED = "graduated"
    ALUMNI = "alumni"


class GuardianRelationship(StrEnum):
    FATHER = "father"
    MOTHER = "mother"
    GUARDIAN = "guardian"
    OTHER = "other"


class DocumentType(StrEnum):
    PHOTO = "photo"
    CNIC = "cnic"
    B_FORM = "b_form"
    CERTIFICATE = "certificate"
    TRANSCRIPT = "transcript"
    OTHER = "other"


class VerificationStatus(StrEnum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


def new_uuid() -> str:
    return str(uuid.uuid4())


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint("college_id", "admission_number", name="uq_student_admission_number_per_college"),
        UniqueConstraint("college_id", "normalized_identity", name="uq_student_identity_per_college"),
        Index("ix_students_college_status", "college_id", "status"),
        Index("ix_students_college_class_section", "college_id", "current_class", "current_section"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    admission_number: Mapped[str] = mapped_column(String(64), nullable=False)
    roll_number: Mapped[str | None] = mapped_column(String(64))
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    normalized_identity: Mapped[str] = mapped_column(String(160), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(32), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    mobile: Mapped[str | None] = mapped_column(String(32))
    address: Mapped[str] = mapped_column(Text, nullable=False)
    program: Mapped[str] = mapped_column(String(120), nullable=False)
    current_class: Mapped[str] = mapped_column(String(80), nullable=False)
    current_section: Mapped[str | None] = mapped_column(String(80))
    academic_session: Mapped[str] = mapped_column(String(40), nullable=False)
    enrollment_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[StudentStatus] = mapped_column(Enum(StudentStatus), nullable=False, default=StudentStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    guardians: Mapped[list["StudentGuardian"]] = relationship(
        back_populates="student", cascade="all, delete-orphan", lazy="selectin"
    )
    documents: Mapped[list["StudentDocument"]] = relationship(
        back_populates="student", cascade="all, delete-orphan", lazy="selectin"
    )
    promotions: Mapped[list["StudentPromotion"]] = relationship(
        back_populates="student", cascade="all, delete-orphan", lazy="selectin"
    )


class StudentGuardian(Base):
    __tablename__ = "student_guardians"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    relationship: Mapped[GuardianRelationship] = mapped_column(Enum(GuardianRelationship), nullable=False)
    mobile: Mapped[str] = mapped_column(String(32), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    occupation: Mapped[str | None] = mapped_column(String(120))
    is_primary: Mapped[bool] = mapped_column(default=False, nullable=False)

    student: Mapped[Student] = relationship(back_populates="guardians")


class StudentDocument(Base):
    __tablename__ = "student_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    document_type: Mapped[DocumentType] = mapped_column(Enum(DocumentType), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    verification_status: Mapped[VerificationStatus] = mapped_column(Enum(VerificationStatus), default=VerificationStatus.PENDING, nullable=False)
    verified_by: Mapped[str | None] = mapped_column(String(64))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[str | None] = mapped_column(Text)

    student: Mapped[Student] = relationship(back_populates="documents")


class StudentPromotion(Base):
    __tablename__ = "student_promotions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    from_class: Mapped[str] = mapped_column(String(80), nullable=False)
    from_section: Mapped[str | None] = mapped_column(String(80))
    to_class: Mapped[str] = mapped_column(String(80), nullable=False)
    to_section: Mapped[str | None] = mapped_column(String(80))
    from_session: Mapped[str] = mapped_column(String(40), nullable=False)
    to_session: Mapped[str] = mapped_column(String(40), nullable=False)
    promoted_on: Mapped[date] = mapped_column(Date, nullable=False)
    promoted_by: Mapped[str] = mapped_column(String(64), nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text)

    student: Mapped[Student] = relationship(back_populates="promotions")
