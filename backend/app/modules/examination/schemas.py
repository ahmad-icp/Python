from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.examination.models import AssessmentComponentType, ExamStatus, ExamTypeCode


class ExamTypeCreate(BaseModel):
    code: ExamTypeCode
    name: str = Field(min_length=2, max_length=120)
    description: str | None = None
    default_weightage: float = Field(default=0, ge=0, le=100)


class ExamTypeRead(ExamTypeCreate):
    id: str
    college_id: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class ExamCreate(BaseModel):
    exam_type_id: str
    session_id: str
    class_id: str
    section_id: str
    program_id: str | None = None
    name: str = Field(min_length=2, max_length=180)
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date > self.end_date:
            raise ValueError("start_date cannot be after end_date")
        return self


class ExamRead(ExamCreate):
    id: str
    college_id: str
    status: ExamStatus
    created_by: str
    published_at: datetime | None = None
    locked_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class AssessmentComponentCreate(BaseModel):
    exam_id: str
    subject_id: str
    component_type: AssessmentComponentType
    name: str = Field(min_length=2, max_length=120)
    maximum_marks: float = Field(gt=0, le=1000)
    passing_marks: float = Field(ge=0, le=1000)
    weightage: float = Field(ge=0, le=100)
    is_internal: bool = True
    is_practical: bool = False

    @model_validator(mode="after")
    def validate_marks(self):
        if self.passing_marks > self.maximum_marks:
            raise ValueError("passing_marks cannot exceed maximum_marks")
        return self


class AssessmentComponentRead(AssessmentComponentCreate):
    id: str
    college_id: str
    model_config = ConfigDict(from_attributes=True)


class ExamHallCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    code: str = Field(min_length=1, max_length=40)
    capacity: int = Field(ge=1, le=5000)


class ExamHallRead(ExamHallCreate):
    id: str
    college_id: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class ExamScheduleCreate(BaseModel):
    exam_id: str
    subject_id: str
    hall_id: str
    component_type: AssessmentComponentType
    exam_date: date
    start_time: time
    end_time: time
    instructions: str | None = None

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")
        return self


class ExamScheduleRead(ExamScheduleCreate):
    id: str
    college_id: str
    section_id: str
    model_config = ConfigDict(from_attributes=True)


class InvigilatorAssignmentCreate(BaseModel):
    schedule_id: str
    teacher_id: str = Field(min_length=1, max_length=64)
    teacher_name: str = Field(min_length=2, max_length=160)


class InvigilatorAssignmentRead(InvigilatorAssignmentCreate):
    id: str
    college_id: str
    exam_date: date
    start_time: time
    end_time: time
    assigned_by: str
    model_config = ConfigDict(from_attributes=True)


class ListResponse(BaseModel):
    items: list
    total: int
    limit: int
    offset: int
