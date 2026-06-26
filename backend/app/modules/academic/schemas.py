from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.academic.models import AssignmentStatus, SessionStatus


class InstitutionCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    code: str = Field(min_length=1, max_length=40)
    address: str | None = None

class InstitutionRead(InstitutionCreate):
    id: str
    college_id: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class CampusCreate(BaseModel):
    institution_id: str
    name: str = Field(min_length=2, max_length=180)
    code: str = Field(min_length=1, max_length=40)
    address: str | None = None

class CampusRead(CampusCreate):
    id: str
    college_id: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class DepartmentCreate(BaseModel):
    institution_id: str
    campus_id: str | None = None
    name: str = Field(min_length=2, max_length=180)
    code: str = Field(min_length=1, max_length=40)

class DepartmentRead(DepartmentCreate):
    id: str
    college_id: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class AcademicSessionCreate(BaseModel):
    name: str = Field(min_length=4, max_length=80)
    start_date: date
    end_date: date
    status: SessionStatus = SessionStatus.PLANNED

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date")
        return self

class AcademicSessionRead(AcademicSessionCreate):
    id: str
    college_id: str
    is_locked: bool
    model_config = ConfigDict(from_attributes=True)

class ProgramCreate(BaseModel):
    department_id: str
    name: str = Field(min_length=2, max_length=180)
    code: str = Field(min_length=1, max_length=40)
    duration_years: int = Field(ge=1, le=10)

class ProgramRead(ProgramCreate):
    id: str
    college_id: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class AcademicClassCreate(BaseModel):
    program_id: str
    session_id: str
    name: str = Field(min_length=1, max_length=100)
    display_order: int = 0

class AcademicClassRead(AcademicClassCreate):
    id: str
    college_id: str
    is_archived: bool
    model_config = ConfigDict(from_attributes=True)

class SectionCreate(BaseModel):
    class_id: str
    name: str = Field(min_length=1, max_length=80)
    capacity: int = Field(ge=1, le=500)
    enrolled_count: int = Field(default=0, ge=0)
    room: str | None = Field(default=None, max_length=80)

    @model_validator(mode="after")
    def validate_capacity(self):
        if self.enrolled_count > self.capacity:
            raise ValueError("enrolled_count cannot exceed capacity")
        return self

class SectionRead(SectionCreate):
    id: str
    college_id: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class SubjectCreate(BaseModel):
    department_id: str | None = None
    code: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=2, max_length=180)
    credit_hours: int = Field(default=1, ge=1, le=10)
    weekly_periods: int = Field(default=1, ge=1, le=40)
    is_elective: bool = False
    prerequisite_subject_ids: list[str] = Field(default_factory=list)

class SubjectRead(BaseModel):
    id: str
    college_id: str
    department_id: str | None = None
    code: str
    name: str
    credit_hours: int
    weekly_periods: int
    is_elective: bool
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class SubjectGroupCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    description: str | None = None

class SubjectGroupRead(SubjectGroupCreate):
    id: str
    college_id: str
    model_config = ConfigDict(from_attributes=True)

class ElectiveGroupCreate(BaseModel):
    class_id: str
    name: str = Field(min_length=2, max_length=160)
    min_subjects: int = Field(default=1, ge=0)
    max_subjects: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def validate_bounds(self):
        if self.min_subjects > self.max_subjects:
            raise ValueError("min_subjects cannot exceed max_subjects")
        return self

class ElectiveGroupRead(ElectiveGroupCreate):
    id: str
    college_id: str
    model_config = ConfigDict(from_attributes=True)

class SubjectAllocationCreate(BaseModel):
    class_id: str
    subject_id: str
    subject_group_id: str | None = None
    elective_group_id: str | None = None
    is_mandatory: bool = True
    weekly_periods: int = Field(ge=1, le=40)

class SubjectAllocationRead(SubjectAllocationCreate):
    id: str
    college_id: str
    model_config = ConfigDict(from_attributes=True)

class TeacherAssignmentCreate(BaseModel):
    teacher_id: str = Field(min_length=1, max_length=64)
    teacher_name: str = Field(min_length=2, max_length=160)
    section_id: str
    subject_id: str
    weekly_periods: int = Field(ge=1, le=40)
    max_weekly_periods: int = Field(default=30, ge=1, le=60)

class TeacherAssignmentRead(TeacherAssignmentCreate):
    id: str
    college_id: str
    status: AssignmentStatus
    model_config = ConfigDict(from_attributes=True)

class TeacherWorkloadRead(BaseModel):
    teacher_id: str
    teacher_name: str
    assigned_periods: int
    max_weekly_periods: int
    remaining_periods: int
    assignment_count: int

class PromotionRuleCreate(BaseModel):
    from_class_id: str
    to_class_id: str
    minimum_attendance_percentage: int = Field(default=75, ge=0, le=100)
    minimum_passing_percentage: int = Field(default=40, ge=0, le=100)
    require_all_mandatory_subjects: bool = True

    @model_validator(mode="after")
    def validate_classes(self):
        if self.from_class_id == self.to_class_id:
            raise ValueError("from_class_id and to_class_id must differ")
        return self

class PromotionRuleRead(PromotionRuleCreate):
    id: str
    college_id: str
    model_config = ConfigDict(from_attributes=True)

class ArchiveRequest(BaseModel):
    entity_type: str = Field(min_length=2, max_length=80)
    entity_id: str
    session_id: str | None = None
    snapshot: str = Field(min_length=2)

class AcademicArchiveRead(ArchiveRequest):
    id: str
    college_id: str
    archived_by: str
    model_config = ConfigDict(from_attributes=True)

class ListResponse(BaseModel):
    items: list
    total: int
    limit: int
    offset: int
