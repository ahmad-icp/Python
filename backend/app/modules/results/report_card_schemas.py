from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.modules.results.report_card_models import ReportCardStatus

class ReportCardGenerateRequest(BaseModel):
    result_id: str
    grade_calculation_id: str | None = None
    institution_name: str = Field(min_length=2, max_length=180)
    branding: dict[str, str] = Field(default_factory=dict)
    remarks: str | None = Field(default=None, max_length=1000)

class ReportCardRead(BaseModel):
    id: str
    college_id: str
    result_id: str
    grade_calculation_id: str | None = None
    exam_id: str
    student_id: str
    status: ReportCardStatus
    verification_code: str
    institution_name: str
    remarks: str | None = None
    qr_payload: str
    printable_html: str
    pdf_file_path: str | None = None
    generated_by: str
    issued_by: str | None = None
    generated_at: datetime
    issued_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)
