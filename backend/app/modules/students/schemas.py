from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modules.students.models import DocumentType, GuardianRelationship, StudentStatus, VerificationStatus


class GuardianBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    relationship: GuardianRelationship
    mobile: str = Field(min_length=7, max_length=32)
    email: str | None = Field(default=None, max_length=255)
    occupation: str | None = Field(default=None, max_length=120)
    is_primary: bool = False


class GuardianCreate(GuardianBase):
    pass


class GuardianRead(GuardianBase):
    id: str
    model_config = ConfigDict(from_attributes=True)


class DocumentCreate(BaseModel):
    document_type: DocumentType
    title: str = Field(min_length=2, max_length=160)
    file_path: str = Field(min_length=3, max_length=500)


class DocumentRead(DocumentCreate):
    id: str
    verification_status: VerificationStatus
    verified_by: str | None = None
    verified_at: datetime | None = None
    rejection_reason: str | None = None
    model_config = ConfigDict(from_attributes=True)


class StudentBase(BaseModel):
    admission_number: str = Field(min_length=1, max_length=64)
    roll_number: str | None = Field(default=None, max_length=64)
    first_name: str = Field(min_length=2, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    date_of_birth: date
    gender: str = Field(min_length=1, max_length=32)
    email: str | None = Field(default=None, max_length=255)
    mobile: str | None = Field(default=None, max_length=32)
    address: str = Field(min_length=5)
    program: str = Field(min_length=1, max_length=120)
    current_class: str = Field(min_length=1, max_length=80)
    current_section: str | None = Field(default=None, max_length=80)
    academic_session: str = Field(min_length=4, max_length=40)
    enrollment_date: date

    @field_validator("admission_number", "first_name", "last_name", "gender", "program", "current_class", "academic_session")
    @classmethod
    def strip_required(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("value cannot be blank")
        return value


class StudentCreate(StudentBase):
    guardians: list[GuardianCreate] = Field(min_length=1)
    documents: list[DocumentCreate] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_one_primary_guardian(self) -> "StudentCreate":
        if sum(guardian.is_primary for guardian in self.guardians) != 1:
            raise ValueError("exactly one primary guardian is required")
        return self


class StudentUpdate(BaseModel):
    roll_number: str | None = Field(default=None, max_length=64)
    first_name: str | None = Field(default=None, min_length=2, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=255)
    mobile: str | None = Field(default=None, max_length=32)
    address: str | None = Field(default=None, min_length=5)
    current_section: str | None = Field(default=None, max_length=80)
    status: StudentStatus | None = None


class StudentRead(StudentBase):
    id: str
    college_id: str
    status: StudentStatus
    guardians: list[GuardianRead]
    documents: list[DocumentRead]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class StudentList(BaseModel):
    items: list[StudentRead]
    total: int
    limit: int
    offset: int


class PromotionCreate(BaseModel):
    to_class: str = Field(min_length=1, max_length=80)
    to_section: str | None = Field(default=None, max_length=80)
    to_session: str = Field(min_length=4, max_length=40)
    promoted_on: date
    remarks: str | None = None


class PromotionRead(PromotionCreate):
    id: str
    from_class: str
    from_section: str | None
    from_session: str
    promoted_by: str
    model_config = ConfigDict(from_attributes=True)


class AlumniCreate(BaseModel):
    graduation_date: date
    remarks: str | None = None


class DocumentVerification(BaseModel):
    status: VerificationStatus
    rejection_reason: str | None = None

    @model_validator(mode="after")
    def require_reason_for_rejection(self) -> "DocumentVerification":
        if self.status == VerificationStatus.REJECTED and not self.rejection_reason:
            raise ValueError("rejection_reason is required when rejecting a document")
        return self
