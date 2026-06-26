from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.marks_entry.models import MarksAuditAction, MarksBatchStatus


class MarksBatchCreate(BaseModel):
    exam_id: str
    section_id: str
    subject_id: str
    component_id: str


class MarksBatchRead(MarksBatchCreate):
    id: str
    college_id: str
    status: MarksBatchStatus
    created_by: str
    submitted_by: str | None = None
    submitted_at: datetime | None = None
    locked_by: str | None = None
    locked_at: datetime | None = None
    unlocked_by: str | None = None
    unlocked_at: datetime | None = None
    unlock_reason: str | None = None
    model_config = ConfigDict(from_attributes=True)


class MarksEntryUpsert(BaseModel):
    student_id: str
    marks_obtained: float = Field(ge=0, le=10000)
    moderation_marks: float = Field(default=0, ge=-1000, le=1000)
    recheck_notes: str | None = None
    remarks: str | None = None


class BulkMarksUpsert(BaseModel):
    entries: list[MarksEntryUpsert] = Field(min_length=1, max_length=1000)

    @model_validator(mode="after")
    def unique_students(self):
        student_ids = [entry.student_id for entry in self.entries]
        if len(student_ids) != len(set(student_ids)):
            raise ValueError("duplicate students are not allowed in one marks payload")
        return self


class MarksEntryRead(MarksEntryUpsert):
    id: str
    college_id: str
    batch_id: str
    exam_id: str
    section_id: str
    subject_id: str
    component_id: str
    entered_by: str
    updated_by: str | None = None
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MarksImportRequest(BaseModel):
    content: str = Field(min_length=1)
    format: str = Field(pattern="^(csv|excel)$")


class UnlockRequest(BaseModel):
    reason: str = Field(min_length=8, max_length=500)


class MarksAuditRead(BaseModel):
    id: str
    college_id: str
    batch_id: str
    entry_id: str | None = None
    action: MarksAuditAction
    actor_id: str
    old_value: str | None = None
    new_value: str | None = None
    reason: str | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ListResponse(BaseModel):
    items: list
    total: int
    limit: int
    offset: int
