from datetime import date

import pytest
from fastapi import HTTPException

from app.modules.attendance.schemas import AttendanceRecordMark, AttendanceSessionCreate, BulkAttendanceMark
from app.modules.attendance.service import AttendanceService
from app.modules.students.schemas import GuardianCreate, StudentCreate
from app.modules.students.service import StudentService
from tests.unit.test_timetable_service import seed


def create_student(db_session, section_name="A"):
    return StudentService(db_session, "college-a").create_student(StudentCreate(
        admission_number="ADM-1",
        first_name="Ali",
        last_name="Khan",
        date_of_birth=date(2014, 1, 1),
        gender="male",
        address="Main campus road",
        program="Middle Science",
        current_class="Class 6",
        current_section=section_name,
        academic_session="2026-2027",
        enrollment_date=date(2026, 4, 1),
        guardians=[GuardianCreate(full_name="Parent Khan", relationship="father", mobile="03000000000", is_primary=True)],
    ))


def test_mark_and_finalize_attendance(db_session):
    _, version, _, _, slot = seed(db_session)
    student = create_student(db_session)
    service = AttendanceService(db_session, "college-a")
    session = service.create_session(AttendanceSessionCreate(session_id=version.session_id, section_id=version.section_id, attendance_date=date(2026, 4, 6), teacher_id="t-1", teacher_name="Ada Teacher", time_slot_id=slot.id))
    records = service.mark_records(session.id, BulkAttendanceMark(records=[AttendanceRecordMark(student_id=student.id, status="present")]), "teacher-1")
    assert records[0].status == "present"
    finalized = service.finalize_session(session.id, "principal-1")
    assert finalized.status == "finalized"
    with pytest.raises(HTTPException) as exc:
        service.mark_records(session.id, BulkAttendanceMark(records=[AttendanceRecordMark(student_id=student.id, status="absent")]), "teacher-1")
    assert exc.value.status_code == 409


def test_attendance_summary_counts_late_as_present(db_session):
    _, version, _, _, slot = seed(db_session)
    student = create_student(db_session)
    service = AttendanceService(db_session, "college-a")
    session = service.create_session(AttendanceSessionCreate(session_id=version.session_id, section_id=version.section_id, attendance_date=date(2026, 4, 6), teacher_id="t-1", teacher_name="Ada Teacher", time_slot_id=slot.id))
    service.mark_records(session.id, BulkAttendanceMark(records=[AttendanceRecordMark(student_id=student.id, status="late", late_minutes=5)]), "teacher-1")
    summary = service.summary(version.section_id, None, None, None)
    assert summary.total == 1
    assert summary.late == 1
    assert summary.attendance_percentage == 100.0
