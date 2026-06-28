from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.modules.results.merit_models import MeritBasis, MeritScope, MeritStatus, TieBreaker
class MeritListGenerateRequest(BaseModel):
    exam_id: str
    scope_type: MeritScope
    scope_id: str | None = None
    basis: MeritBasis
    title: str = Field(min_length=2,max_length=180)
    tie_breakers: list[TieBreaker] = [TieBreaker.ADMISSION_NUMBER]
    publish_immediately: bool = False
class MeritItemRead(BaseModel):
    id: str; result_id: str; grade_calculation_id: str|None=None; student_id: str; rank: int; score: float; percentage: float; gpa: float|None=None; tie_breaker_value: str|None=None; is_certificate_issued: bool
    model_config=ConfigDict(from_attributes=True)
class MeritListRead(BaseModel):
    id: str; college_id: str; exam_id: str; scope_type: MeritScope; scope_id: str; basis: MeritBasis; status: MeritStatus; title: str; tie_breakers: str; analytics_json: str; generated_by: str; published_by: str|None=None; generated_at: datetime; published_at: datetime|None=None; items: list[MeritItemRead]=[]
    model_config=ConfigDict(from_attributes=True)
class MeritCertificateRead(BaseModel):
    id: str; college_id: str; merit_item_id: str; verification_code: str; printable_html: str; issued_by: str; issued_at: datetime
    model_config=ConfigDict(from_attributes=True)
