from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modules.admissions.models import AdmissionMode, AdmissionStatus, MeritListStatus
from app.modules.students.models import DocumentType, VerificationStatus


class AdmissionDocumentCreate(BaseModel):
    document_type: DocumentType
    title: str = Field(min_length=2, max_length=160)
    file_path: str = Field(min_length=3, max_length=500)


class AdmissionDocumentRead(AdmissionDocumentCreate):
    id: str
    verification_status: VerificationStatus
    verified_by: str | None = None
    verified_at: datetime | None = None
    rejection_reason: str | None = None
    model_config = ConfigDict(from_attributes=True)


class AdmissionApplicationBase(BaseModel):
    application_number: str = Field(min_length=1, max_length=64)
    mode: AdmissionMode
    applicant_first_name: str = Field(min_length=2, max_length=100)
    applicant_last_name: str = Field(min_length=1, max_length=100)
    date_of_birth: date
    gender: str = Field(min_length=1, max_length=32)
    email: str | None = Field(default=None, max_length=255)
    mobile: str | None = Field(default=None, max_length=32)
    address: str = Field(min_length=5)
    guardian_name: str = Field(min_length=2, max_length=160)
    guardian_mobile: str = Field(min_length=7, max_length=32)
    guardian_email: str | None = Field(default=None, max_length=255)
    previous_school: str | None = Field(default=None, max_length=180)
    previous_class: str | None = Field(default=None, max_length=80)
    program: str = Field(min_length=1, max_length=120)
    applying_for_class: str = Field(min_length=1, max_length=80)
    preferred_section: str | None = Field(default=None, max_length=80)
    academic_session: str = Field(min_length=4, max_length=40)
    obtained_marks: float | None = Field(default=None, ge=0)
    total_marks: float | None = Field(default=None, gt=0)

    @field_validator(
        "application_number",
        "applicant_first_name",
        "applicant_last_name",
        "gender",
        "guardian_name",
        "program",
        "applying_for_class",
        "academic_session",
    )
    @classmethod
    def strip_required(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("value cannot be blank")
        return value

    @model_validator(mode="after")
    def validate_marks(self) -> "AdmissionApplicationBase":
        if (self.obtained_marks is None) ^ (self.total_marks is None):
            raise ValueError("obtained_marks and total_marks must be provided together")
        if self.obtained_marks is not None and self.total_marks is not None and self.obtained_marks > self.total_marks:
            raise ValueError("obtained_marks cannot be greater than total_marks")
        return self


class AdmissionApplicationCreate(AdmissionApplicationBase):
    documents: list[AdmissionDocumentCreate] = Field(default_factory=list)


class AdmissionApplicationUpdate(BaseModel):
    email: str | None = Field(default=None, max_length=255)
    mobile: str | None = Field(default=None, max_length=32)
    address: str | None = Field(default=None, min_length=5)
    guardian_name: str | None = Field(default=None, min_length=2, max_length=160)
    guardian_mobile: str | None = Field(default=None, min_length=7, max_length=32)
    guardian_email: str | None = Field(default=None, max_length=255)
    previous_school: str | None = Field(default=None, max_length=180)
    previous_class: str | None = Field(default=None, max_length=80)
    preferred_section: str | None = Field(default=None, max_length=80)
    obtained_marks: float | None = Field(default=None, ge=0)
    total_marks: float | None = Field(default=None, gt=0)


class AdmissionApplicationRead(AdmissionApplicationBase):
    id: str
    college_id: str
    status: AdmissionStatus
    merit_score: float | None = None
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    decision_reason: str | None = None
    admitted_student_id: str | None = None
    submitted_at: datetime
    documents: list[AdmissionDocumentRead]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AdmissionApplicationList(BaseModel):
    items: list[AdmissionApplicationRead]
    total: int
    limit: int
    offset: int


class AdmissionDecision(BaseModel):
    status: AdmissionStatus
    reason: str | None = None

    @model_validator(mode="after")
    def validate_decision(self) -> "AdmissionDecision":
        allowed = {
            AdmissionStatus.UNDER_REVIEW,
            AdmissionStatus.DOCUMENTS_PENDING,
            AdmissionStatus.ELIGIBLE,
            AdmissionStatus.OFFERED,
            AdmissionStatus.REJECTED,
            AdmissionStatus.CANCELLED,
        }
        if self.status not in allowed:
            raise ValueError("status is not a valid manual admission decision")
        if self.status in {AdmissionStatus.REJECTED, AdmissionStatus.CANCELLED} and not self.reason:
            raise ValueError("reason is required for rejected or cancelled applications")
        return self


class AdmissionDocumentVerification(BaseModel):
    status: VerificationStatus
    rejection_reason: str | None = None

    @model_validator(mode="after")
    def require_rejection_reason(self) -> "AdmissionDocumentVerification":
        if self.status == VerificationStatus.REJECTED and not self.rejection_reason:
            raise ValueError("rejection_reason is required when rejecting a document")
        return self


class MeritListCreate(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    program: str = Field(min_length=1, max_length=120)
    academic_session: str = Field(min_length=4, max_length=40)
    list_number: int = Field(ge=1)
    capacity: int = Field(ge=1, le=500)
    minimum_score: float | None = Field(default=None, ge=0, le=100)
    offer_expires_on: date | None = None


class MeritListEntryRead(BaseModel):
    id: str
    application_id: str
    position: int
    score: float
    offer_expires_on: date | None = None
    model_config = ConfigDict(from_attributes=True)


class MeritListRead(BaseModel):
    id: str
    college_id: str
    title: str
    program: str
    academic_session: str
    list_number: int
    minimum_score: float | None = None
    status: MeritListStatus
    published_at: datetime | None = None
    created_by: str
    created_at: datetime
    entries: list[MeritListEntryRead]
    model_config = ConfigDict(from_attributes=True)


class EnrollApplicant(BaseModel):
    admission_number: str = Field(min_length=1, max_length=64)
    roll_number: str | None = Field(default=None, max_length=64)
    section: str | None = Field(default=None, max_length=80)
    enrollment_date: date
