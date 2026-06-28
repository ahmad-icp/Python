from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel

class PortalStudentProfile(BaseModel):
    id: str
    admission_number: str
    roll_number: str | None = None
    first_name: str
    last_name: str
    program: str
    current_class: str
    current_section: str | None = None
    academic_session: str
    status: str

class PortalAttendanceSummary(BaseModel):
    total: int = 0
    present: int = 0
    absent: int = 0
    late: int = 0
    excused: int = 0
    percentage: float = 0

class PortalTimetableItem(BaseModel):
    weekday: int
    teacher_name: str
    entry_type: str
    notes: str | None = None

class PortalResultItem(BaseModel):
    exam_id: str
    status: str
    outcome: str
    obtained_marks: Decimal
    total_marks: Decimal
    percentage: Decimal

class PortalChallanItem(BaseModel):
    id: str
    challan_number: str
    billing_period: str
    due_date: date
    status: str
    total_amount: Decimal
    paid_amount: Decimal
    balance_amount: Decimal

class PortalPaymentItem(BaseModel):
    id: str
    challan_id: str
    amount: Decimal
    method: str
    reference_number: str
    paid_on: date
    status: str

class PortalMeritPosition(BaseModel):
    merit_list_id: str
    rank: int
    score: Decimal
    percentage: Decimal
    gpa: Decimal | None = None

class PortalCalendarEvent(BaseModel):
    title: str
    start_date: date
    end_date: date
    is_holiday: bool
    description: str | None = None

class PortalNotification(BaseModel):
    id: str
    title: str
    message: str
    created_at: datetime | None = None

class StudentPortalDashboard(BaseModel):
    profile: PortalStudentProfile
    attendance: PortalAttendanceSummary
    timetable: list[PortalTimetableItem]
    results: list[PortalResultItem]
    merit_positions: list[PortalMeritPosition]
    challans: list[PortalChallanItem]
    payments: list[PortalPaymentItem]
    calendar: list[PortalCalendarEvent]
    notifications: list[PortalNotification]
    downloads: list[dict[str, str]]
