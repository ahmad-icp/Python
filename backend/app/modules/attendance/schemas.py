from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.modules.attendance.models import AttendanceSessionStatus, AttendanceStatus

class AttendanceSessionCreate(BaseModel):
    session_id: str
    section_id: str
    attendance_date: date
    teacher_id: str = Field(min_length=1, max_length=64)
    teacher_name: str = Field(min_length=2, max_length=160)
    time_slot_id: str | None = None
    timetable_entry_id: str | None = None
    remarks: str | None = None

class AttendanceSessionRead(AttendanceSessionCreate):
    id: str
    college_id: str
    status: AttendanceSessionStatus
    finalized_by: str | None = None
    finalized_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)

class AttendanceRecordMark(BaseModel):
    student_id: str
    status: AttendanceStatus
    late_minutes: int = Field(default=0, ge=0, le=600)
    remarks: str | None = None

    @model_validator(mode="after")
    def validate_late_minutes(self):
        if self.status != AttendanceStatus.LATE and self.late_minutes:
            raise ValueError("late_minutes is only allowed for late attendance")
        return self

class BulkAttendanceMark(BaseModel):
    records: list[AttendanceRecordMark] = Field(min_length=1, max_length=500)

class AttendanceRecordRead(AttendanceRecordMark):
    id: str
    college_id: str
    attendance_session_id: str
    section_id: str
    attendance_date: date
    marked_by: str
    marked_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AttendanceSummary(BaseModel):
    total: int
    present: int
    absent: int
    late: int
    excused: int
    attendance_percentage: float
