from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.modules.results.gpa_models import AcademicStanding, GradingSystemType, RoundingMode

class GradeMappingCreate(BaseModel):
    grade: str = Field(min_length=1, max_length=12)
    min_percentage: float = Field(ge=0, le=100)
    max_percentage: float = Field(ge=0, le=100)
    grade_point: float = Field(default=0, ge=0, le=10)
    remark: str | None = Field(default=None, max_length=160)
    is_passing: bool = True
    @model_validator(mode="after")
    def valid_range(self):
        if self.min_percentage > self.max_percentage:
            raise ValueError("min_percentage cannot exceed max_percentage")
        return self

class GradeSystemCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    system_type: GradingSystemType
    scope_type: str = Field(default="institution", pattern="^(institution|program|class|section)$")
    scope_id: str | None = None
    version: int = Field(default=1, ge=1)
    gpa_scale: float = Field(default=4, gt=0, le=10)
    passing_percentage: float = Field(default=40, ge=0, le=100)
    passing_gpa: float = Field(default=2, ge=0, le=10)
    decimal_places: int = Field(default=2, ge=0, le=4)
    rounding_mode: RoundingMode = RoundingMode.STANDARD
    is_active: bool = True
    mappings: list[GradeMappingCreate] = Field(min_length=1, max_length=50)
    @model_validator(mode="after")
    def validate_gpa_fields(self):
        if self.system_type == GradingSystemType.PERCENTAGE:
            self.passing_gpa = 0
        if self.scope_id is None:
            self.scope_id = ""
        return self

class GradeMappingRead(GradeMappingCreate):
    id: str
    college_id: str
    system_id: str
    model_config = ConfigDict(from_attributes=True)

class GradeSystemRead(BaseModel):
    id: str
    college_id: str
    name: str
    system_type: GradingSystemType
    scope_type: str
    scope_id: str | None = None
    version: int
    gpa_scale: float
    passing_percentage: float
    passing_gpa: float
    decimal_places: int
    rounding_mode: RoundingMode
    is_active: bool
    created_at: datetime
    mappings: list[GradeMappingRead] = []
    model_config = ConfigDict(from_attributes=True)

class GradeCalculationRequest(BaseModel):
    result_ids: list[str] = Field(min_length=1, max_length=500)
    system_id: str | None = None
    force_recalculate: bool = False

class StudentGradeCalculationRead(BaseModel):
    id: str
    college_id: str
    result_id: str
    exam_id: str
    student_id: str
    system_id: str
    percentage: float
    grade: str
    gpa: float | None = None
    cgpa: float | None = None
    total_credit_hours: int | None = None
    earned_credit_hours: int | None = None
    academic_standing: AcademicStanding
    is_promotion_eligible: bool
    calculated_by: str
    calculated_at: datetime
    remarks: str | None = None
    model_config = ConfigDict(from_attributes=True)
