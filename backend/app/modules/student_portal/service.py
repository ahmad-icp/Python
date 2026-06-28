from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.modules.attendance.models import AttendanceRecord, AttendanceStatus
from app.modules.fees.models import FeeChallan, FeePayment
from app.modules.results.merit_models import MeritListItem
from app.modules.results.models import ResultStatus, StudentResult
from app.modules.student_portal.schemas import *
from app.modules.students.models import Student
from app.modules.timetable.models import CalendarEvent, TimetableEntry, TimetableStatus, TimetableVersion

class StudentPortalService:
    def __init__(self, db: Session, college_id: str):
        self.db = db
        self.college_id = college_id

    def get_student(self, student_id: str) -> Student:
        student = self.db.get(Student, student_id)
        if not student or student.college_id != self.college_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, 'Student not found')
        return student

    def dashboard(self, student_id: str) -> StudentPortalDashboard:
        student = self.get_student(student_id)
        challans = self._challans(student.id)
        return StudentPortalDashboard(
            profile=PortalStudentProfile.model_validate(student, from_attributes=True),
            attendance=self._attendance_summary(student.id),
            timetable=self._timetable(student),
            results=self._results(student.id),
            merit_positions=self._merit(student.id),
            challans=challans,
            payments=self._payments([c.id for c in challans]),
            calendar=self._calendar(),
            notifications=[],
            downloads=[{'title': 'Transcript', 'type': 'transcript'}, {'title': 'Report Cards', 'type': 'report_cards'}],
        )

    def _attendance_summary(self, student_id: str) -> PortalAttendanceSummary:
        rows = self.db.execute(select(AttendanceRecord.status, func.count()).where(AttendanceRecord.college_id == self.college_id, AttendanceRecord.student_id == student_id).group_by(AttendanceRecord.status)).all()
        counts = {row[0].value: row[1] for row in rows}
        total = sum(counts.values())
        present_equivalent = counts.get(AttendanceStatus.PRESENT.value, 0) + counts.get(AttendanceStatus.LATE.value, 0)
        percentage = round((present_equivalent / total) * 100, 2) if total else 0
        return PortalAttendanceSummary(total=total, present=counts.get('present', 0), absent=counts.get('absent', 0), late=counts.get('late', 0), excused=counts.get('excused', 0), percentage=percentage)

    def _timetable(self, student: Student) -> list[PortalTimetableItem]:
        rows = self.db.scalars(select(TimetableEntry).join(TimetableVersion).where(TimetableEntry.college_id == self.college_id, TimetableVersion.status == TimetableStatus.PUBLISHED).order_by(TimetableEntry.weekday).limit(50)).all()
        return [PortalTimetableItem(weekday=r.weekday, teacher_name=r.teacher_name, entry_type=r.entry_type.value, notes=r.notes) for r in rows]

    def _results(self, student_id: str) -> list[PortalResultItem]:
        rows = self.db.scalars(select(StudentResult).where(StudentResult.college_id == self.college_id, StudentResult.student_id == student_id, StudentResult.status.in_([ResultStatus.PUBLISHED, ResultStatus.LOCKED])).order_by(StudentResult.calculated_at.desc()).limit(10)).all()
        return [PortalResultItem(exam_id=r.exam_id, status=r.status.value, outcome=r.outcome.value, obtained_marks=r.obtained_marks, total_marks=r.total_marks, percentage=r.percentage) for r in rows]

    def _merit(self, student_id: str) -> list[PortalMeritPosition]:
        rows = self.db.scalars(select(MeritListItem).where(MeritListItem.college_id == self.college_id, MeritListItem.student_id == student_id).order_by(MeritListItem.rank).limit(10)).all()
        return [PortalMeritPosition(merit_list_id=r.merit_list_id, rank=r.rank, score=r.score, percentage=r.percentage, gpa=r.gpa) for r in rows]

    def _challans(self, student_id: str) -> list[PortalChallanItem]:
        rows = self.db.scalars(select(FeeChallan).where(FeeChallan.college_id == self.college_id, FeeChallan.student_id == student_id).order_by(FeeChallan.due_date.desc()).limit(12)).all()
        return [PortalChallanItem.model_validate(r, from_attributes=True) for r in rows]

    def _payments(self, challan_ids: list[str]) -> list[PortalPaymentItem]:
        if not challan_ids:
            return []
        rows = self.db.scalars(select(FeePayment).where(FeePayment.college_id == self.college_id, FeePayment.challan_id.in_(challan_ids)).order_by(FeePayment.paid_on.desc()).limit(20)).all()
        return [PortalPaymentItem.model_validate(r, from_attributes=True) for r in rows]

    def _calendar(self) -> list[PortalCalendarEvent]:
        rows = self.db.scalars(select(CalendarEvent).where(CalendarEvent.college_id == self.college_id).order_by(CalendarEvent.start_date).limit(20)).all()
        return [PortalCalendarEvent.model_validate(r, from_attributes=True) for r in rows]
