import hashlib
import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def new_uuid() -> str:
    return str(uuid.uuid4())


class CertificateType(StrEnum):
    CHARACTER = "character"
    BONAFIDE = "bonafide"
    LEAVING = "leaving"
    MIGRATION = "migration"
    EXPERIENCE = "experience"
    CUSTOM = "custom"


class CertificateStatus(StrEnum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    ISSUED = "issued"
    REVOKED = "revoked"


class RepositoryDocumentType(StrEnum):
    STUDENT_UPLOAD = "student_upload"
    CERTIFICATE = "certificate"
    IDENTITY = "identity"
    ACADEMIC = "academic"
    FINANCE = "finance"
    HR = "hr"
    OTHER = "other"


class DocumentApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class CertificateTemplate(Base):
    __tablename__ = "certificate_templates"
    __table_args__ = (
        UniqueConstraint("college_id", "code", "version", name="uq_certificate_template_code_version"),
        Index("ix_certificate_templates_college_type", "college_id", "certificate_type", "is_active"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(80), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    certificate_type: Mapped[CertificateType] = mapped_column(Enum(CertificateType), nullable=False)
    version: Mapped[int] = mapped_column(default=1, nullable=False)
    body_template: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class CertificateRequest(Base):
    __tablename__ = "certificate_requests"
    __table_args__ = (
        Index("ix_certificate_requests_college_student_status", "college_id", "student_id", "status"),
        Index("ix_certificate_requests_college_type_status", "college_id", "certificate_type", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    template_id: Mapped[str | None] = mapped_column(ForeignKey("certificate_templates.id", ondelete="SET NULL"), index=True)
    certificate_type: Mapped[CertificateType] = mapped_column(Enum(CertificateType), nullable=False)
    student_id: Mapped[str | None] = mapped_column(String(36), index=True)
    employee_id: Mapped[str | None] = mapped_column(String(64), index=True)
    purpose: Mapped[str] = mapped_column(String(240), nullable=False)
    status: Mapped[CertificateStatus] = mapped_column(Enum(CertificateStatus), default=CertificateStatus.PENDING_APPROVAL, nullable=False)
    requested_by: Mapped[str] = mapped_column(String(64), nullable=False)
    approved_by: Mapped[str | None] = mapped_column(String(64))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    issued_by: Mapped[str | None] = mapped_column(String(64))
    issued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verification_code: Mapped[str] = mapped_column(String(96), nullable=False, unique=True, index=True)
    rendered_html: Mapped[str | None] = mapped_column(Text)
    qr_payload: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    template: Mapped[CertificateTemplate | None] = relationship(lazy="selectin")


class DocumentRepositoryItem(Base):
    __tablename__ = "document_repository_items"
    __table_args__ = (
        Index("ix_documents_college_owner_status", "college_id", "owner_type", "owner_id", "approval_status"),
        Index("ix_documents_college_type", "college_id", "document_type"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    owner_type: Mapped[str] = mapped_column(String(40), nullable=False)
    owner_id: Mapped[str] = mapped_column(String(64), nullable=False)
    document_type: Mapped[RepositoryDocumentType] = mapped_column(Enum(RepositoryDocumentType), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    approval_status: Mapped[DocumentApprovalStatus] = mapped_column(Enum(DocumentApprovalStatus), default=DocumentApprovalStatus.PENDING, nullable=False)
    uploaded_by: Mapped[str] = mapped_column(String(64), nullable=False)
    approved_by: Mapped[str | None] = mapped_column(String(64))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


def verification_code_for(college_id: str, request_id: str) -> str:
    digest = hashlib.sha256(f"{college_id}:{request_id}".encode()).hexdigest()[:24].upper()
    return f"CERT-{digest}"
