from pydantic import BaseModel

class TeacherTimetableItem(BaseModel):
    weekday: int
    section_id: str
    subject_id: str
    classroom_id: str
    entry_type: str

class TeacherAttendanceWorkItem(BaseModel):
    id: str
    section_id: str
    attendance_date: str
    status: str

class TeacherPortalDashboard(BaseModel):
    teacher_id: str
    timetable: list[TeacherTimetableItem]
    attendance_sessions: list[TeacherAttendanceWorkItem]
    marks_entry: list[dict[str, str]]
    result_review: list[dict[str, str]]
    student_performance: list[dict[str, str]]
    announcements: list[dict[str, str]]
    class_management: list[dict[str, str]]
