from datetime import date, time

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.timetable.models import RoomType, TimetableEntryType, TimetableStatus, Weekday


class ClassroomCreate(BaseModel):
    campus_id: str | None = None
    name: str = Field(min_length=2, max_length=160)
    code: str = Field(min_length=1, max_length=40)
    room_type: RoomType = RoomType.CLASSROOM
    capacity: int = Field(ge=1, le=1000)


class ClassroomRead(ClassroomCreate):
    id: str
    college_id: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class TimeSlotCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    start_time: time
    end_time: time
    sort_order: int = 0
    is_break: bool = False

    @model_validator(mode="after")
    def validate_range(self):
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")
        return self


class TimeSlotRead(TimeSlotCreate):
    id: str
    college_id: str
    model_config = ConfigDict(from_attributes=True)


class WorkingDayCreate(BaseModel):
    session_id: str
    weekday: Weekday
    is_working: bool = True


class WorkingDayRead(BaseModel):
    id: str
    college_id: str
    session_id: str
    weekday: int
    is_working: bool
    model_config = ConfigDict(from_attributes=True)


class CalendarEventCreate(BaseModel):
    session_id: str
    title: str = Field(min_length=2, max_length=180)
    start_date: date
    end_date: date
    is_holiday: bool = False
    description: str | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date > self.end_date:
            raise ValueError("start_date cannot be after end_date")
        return self


class CalendarEventRead(CalendarEventCreate):
    id: str
    college_id: str
    model_config = ConfigDict(from_attributes=True)


class TimetableVersionCreate(BaseModel):
    session_id: str
    section_id: str
    effective_from: date
    effective_to: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.effective_from > self.effective_to:
            raise ValueError("effective_from cannot be after effective_to")
        return self


class TimetableVersionRead(TimetableVersionCreate):
    id: str
    college_id: str
    version_number: int
    status: TimetableStatus
    created_by: str
    model_config = ConfigDict(from_attributes=True)


class TimetableEntryCreate(BaseModel):
    version_id: str
    subject_id: str
    teacher_id: str = Field(min_length=1, max_length=64)
    teacher_name: str = Field(min_length=2, max_length=160)
    classroom_id: str
    time_slot_id: str
    weekday: Weekday
    entry_type: TimetableEntryType = TimetableEntryType.LECTURE
    notes: str | None = None


class TimetableEntryRead(BaseModel):
    id: str
    college_id: str
    version_id: str
    session_id: str
    section_id: str
    subject_id: str
    teacher_id: str
    teacher_name: str
    classroom_id: str
    time_slot_id: str
    weekday: int
    entry_type: TimetableEntryType
    notes: str | None = None
    model_config = ConfigDict(from_attributes=True)


class AutoGenerateRequest(BaseModel):
    version_id: str
    teacher_id: str = Field(min_length=1, max_length=64)
    teacher_name: str = Field(min_length=2, max_length=160)
    classroom_id: str


class TimetableView(BaseModel):
    entries: list[TimetableEntryRead]
    total: int


class ListResponse(BaseModel):
    items: list
    total: int
    limit: int
    offset: int
