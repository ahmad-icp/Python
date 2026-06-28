from fastapi import APIRouter

from app.modules.academic.router import router as academic_router
from app.modules.attendance.router import router as attendance_router
from app.modules.certificates.router import router as certificates_router
from app.modules.examination.router import router as examination_router
from app.modules.fees.router import router as fees_router
from app.modules.marks_entry.router import router as marks_entry_router
from app.modules.notifications.router import router as notifications_router
from app.modules.results.router import router as results_router
from app.modules.results.gpa_router import router as gpa_router
from app.modules.results.report_card_router import router as report_card_router
from app.modules.results.gazette_router import router as gazette_router
from app.modules.results.merit_router import router as merit_router
from app.modules.results.transcript_router import router as transcript_router
from app.modules.admissions.router import router as admissions_router
from app.modules.authentication.router import router as authentication_router
from app.modules.settings.router import router as settings_router
from app.modules.students.router import router as students_router
from app.modules.student_portal.router import router as student_portal_router
from app.modules.parent_portal.router import router as parent_portal_router
from app.modules.teacher_portal.router import router as teacher_portal_router
from app.modules.timetable.router import router as timetable_router

api_router = APIRouter()
api_router.include_router(authentication_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(academic_router, prefix="/academic", tags=["Academic Management"])
api_router.include_router(admissions_router, prefix="/admissions", tags=["Admissions Management"])
api_router.include_router(settings_router, prefix="/settings", tags=["Settings"])
api_router.include_router(students_router, prefix="/students", tags=["Student Information System"])
api_router.include_router(timetable_router, prefix="/timetable", tags=["Timetable Management"])
api_router.include_router(attendance_router, prefix="/attendance", tags=["Attendance Management"])
api_router.include_router(examination_router, prefix="/examinations", tags=["Examination Management"])
api_router.include_router(marks_entry_router, prefix="/marks-entry", tags=["Marks Entry"])
api_router.include_router(results_router, prefix="/results", tags=["Result Processing"])
api_router.include_router(gpa_router, prefix="/grade-calculations", tags=["GPA & Percentage Calculation"])
api_router.include_router(report_card_router, prefix="/report-cards", tags=["Report Cards DMC"])
api_router.include_router(gazette_router, prefix="/gazettes", tags=["Gazette Generation"])
api_router.include_router(merit_router, prefix="/merit-lists", tags=["Merit Lists"])
api_router.include_router(transcript_router, prefix="/transcripts", tags=["Transcript Generation"])
api_router.include_router(fees_router, prefix="/fees", tags=["Enterprise Finance"])
api_router.include_router(student_portal_router, prefix="/portal/student", tags=["Student Portal"])
api_router.include_router(parent_portal_router, prefix="/portal/parent", tags=["Parent Portal"])
api_router.include_router(teacher_portal_router, prefix="/portal/teacher", tags=["Teacher Portal"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["Notification Center"])
api_router.include_router(certificates_router, prefix="/certificates", tags=["Certificate & Document Management"])


@api_router.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Return API health status for load balancers and uptime checks."""
    return {"status": "ok", "service": "college-erp-platform"}
