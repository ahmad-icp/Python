from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.modules.results.gazette_models import GazetteScope, GazetteStatus
class GazetteGenerateRequest(BaseModel):
    exam_id: str
    scope_type: GazetteScope
    scope_id: str | None = None
    title: str = Field(min_length=2, max_length=180)
class GazetteRead(BaseModel):
    id: str; college_id: str; exam_id: str; scope_type: GazetteScope; scope_id: str; status: GazetteStatus; title: str; summary_json: str; rows_json: str; generated_by: str; generated_at: datetime
    model_config = ConfigDict(from_attributes=True)
