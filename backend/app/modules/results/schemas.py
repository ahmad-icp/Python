from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.modules.results.models import ResultOutcome, ResultStatus

class GradingPolicyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    version: int = Field(default=1, ge=1)
    minimum_percentage: float = Field(default=40, ge=0, le=100)
    grace_marks: float = Field(default=0, ge=0, le=1000)
    promotion_minimum_percentage: float = Field(default=40, ge=0, le=100)
    is_active: bool = True

class GradingPolicyRead(GradingPolicyCreate):
    id: str
    college_id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CalculateRequest(BaseModel):
    exam_id: str
    student_ids: list[str] | None = None
    policy_id: str | None = None
    force_recalculate: bool = False

class SubjectResultRead(BaseModel):
    id: str
    subject_id: str
    credit_hours: int
    maximum_marks: float
    obtained_marks: float
    grace_awarded: float
    percentage: float
    outcome: ResultOutcome
    remarks: str | None = None
    model_config = ConfigDict(from_attributes=True)

class StudentResultRead(BaseModel):
    id: str
    college_id: str
    exam_id: str
    student_id: str
    policy_id: str | None = None
    status: ResultStatus
    outcome: ResultOutcome
    total_marks: float
    obtained_marks: float
    grace_awarded: float
    percentage: float
    is_promotion_eligible: bool
    calculated_by: str
    calculated_at: datetime
    published_by: str | None = None
    published_at: datetime | None = None
    locked_by: str | None = None
    locked_at: datetime | None = None
    subjects: list[SubjectResultRead] = []
    model_config = ConfigDict(from_attributes=True)
