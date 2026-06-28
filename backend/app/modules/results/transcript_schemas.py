from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.modules.results.transcript_models import TranscriptStatus
class TranscriptGenerateRequest(BaseModel):
    student_id: str
    institution_name: str = Field(min_length=2,max_length=180)
    remarks: str | None = Field(default=None,max_length=1000)
class TranscriptRead(BaseModel):
    id: str; college_id: str; student_id: str; status: TranscriptStatus; verification_code: str; institution_name: str; academic_history_json: str; summary_json: str; printable_html: str; generated_by: str; issued_by: str|None=None; generated_at: datetime; issued_at: datetime|None=None
    model_config=ConfigDict(from_attributes=True)
