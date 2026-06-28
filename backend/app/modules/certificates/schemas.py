from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.modules.certificates.models import CertificateStatus, CertificateType, DocumentApprovalStatus, RepositoryDocumentType

class CertificateTemplateCreate(BaseModel):
    code: str = Field(min_length=2, max_length=80)
    name: str = Field(min_length=2, max_length=160)
    certificate_type: CertificateType
    version: int = Field(default=1, ge=1)
    body_template: str = Field(min_length=10)
    is_active: bool = True

class CertificateTemplateRead(CertificateTemplateCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    college_id: str
    created_at: datetime

class CertificateRequestCreate(BaseModel):
    template_id: str | None = None
    certificate_type: CertificateType
    student_id: str | None = None
    employee_id: str | None = None
    purpose: str = Field(min_length=3, max_length=240)
    context: dict[str, str] = {}

    @model_validator(mode="after")
    def owner_required(self):
        if not self.student_id and not self.employee_id:
            raise ValueError("student_id or employee_id is required")
        if self.student_id and self.employee_id:
            raise ValueError("Only one of student_id or employee_id may be provided")
        return self

class CertificateApprovalUpdate(BaseModel):
    status: CertificateStatus
    rejection_reason: str | None = None

    @model_validator(mode="after")
    def valid_status(self):
        if self.status not in {CertificateStatus.APPROVED, CertificateStatus.REJECTED}:
            raise ValueError("status must be approved or rejected")
        if self.status == CertificateStatus.REJECTED and not self.rejection_reason:
            raise ValueError("rejection_reason is required when rejecting")
        return self

class CertificateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    college_id: str
    template_id: str | None
    certificate_type: CertificateType
    student_id: str | None
    employee_id: str | None
    purpose: str
    status: CertificateStatus
    requested_by: str
    approved_by: str | None
    approved_at: datetime | None
    rejection_reason: str | None
    issued_by: str | None
    issued_at: datetime | None
    verification_code: str
    rendered_html: str | None
    qr_payload: str | None
    created_at: datetime

class CertificateList(BaseModel):
    items: list[CertificateRead]
    total: int
    limit: int
    offset: int

class DocumentCreate(BaseModel):
    owner_type: str = Field(min_length=2, max_length=40)
    owner_id: str = Field(min_length=1, max_length=64)
    document_type: RepositoryDocumentType
    title: str = Field(min_length=2, max_length=180)
    file_path: str = Field(min_length=3, max_length=500)
    mime_type: str = Field(min_length=3, max_length=120)
    checksum_sha256: str = Field(min_length=64, max_length=64)

class DocumentApprovalUpdate(BaseModel):
    status: DocumentApprovalStatus
    rejection_reason: str | None = None

    @model_validator(mode="after")
    def valid_document_status(self):
        if self.status == DocumentApprovalStatus.REJECTED and not self.rejection_reason:
            raise ValueError("rejection_reason is required when rejecting")
        return self

class DocumentRead(DocumentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    college_id: str
    approval_status: DocumentApprovalStatus
    uploaded_by: str
    approved_by: str | None
    approved_at: datetime | None
    rejection_reason: str | None
    created_at: datetime

class VerificationResponse(BaseModel):
    valid: bool
    certificate: CertificateRead | None = None
