from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import CurrentUser, Permission, require_permission
from app.db.session import get_db
from app.modules.attendance.models import AttendanceSession
from app.modules.teacher_portal.schemas import TeacherAttendanceWorkItem, TeacherPortalDashboard, TeacherTimetableItem
from app.modules.timetable.models import TimetableEntry, TimetableStatus, TimetableVersion

router = APIRouter()

@router.get('/dashboard', response_model=TeacherPortalDashboard)
def teacher_dashboard(db: Session = Depends(get_db), current_user: CurrentUser = Depends(require_permission(Permission.TEACHER_PORTAL_READ))):
    entries = db.scalars(select(TimetableEntry).join(TimetableVersion).where(TimetableEntry.college_id == current_user.college_id, TimetableEntry.teacher_id == current_user.user_id, TimetableVersion.status == TimetableStatus.PUBLISHED).order_by(TimetableEntry.weekday).limit(50)).all()
    sessions = db.scalars(select(AttendanceSession).where(AttendanceSession.college_id == current_user.college_id, AttendanceSession.teacher_id == current_user.user_id).order_by(AttendanceSession.attendance_date.desc()).limit(20)).all()
    return TeacherPortalDashboard(
        teacher_id=current_user.user_id,
        timetable=[TeacherTimetableItem(weekday=e.weekday, section_id=e.section_id, subject_id=e.subject_id, classroom_id=e.classroom_id, entry_type=e.entry_type.value) for e in entries],
        attendance_sessions=[TeacherAttendanceWorkItem(id=s.id, section_id=s.section_id, attendance_date=str(s.attendance_date), status=s.status.value) for s in sessions],
        marks_entry=[], result_review=[], student_performance=[], announcements=[], class_management=[]
    )
