from datetime import date, time

import pytest
from fastapi import HTTPException

from app.modules.examination.schemas import ExamScheduleCreate
from app.modules.marks_entry.schemas import BulkMarksUpsert, MarksBatchCreate, MarksEntryUpsert, MarksImportRequest, UnlockRequest
from app.modules.marks_entry.service import MarksEntryService
from tests.unit.test_attendance_service import create_student
from tests.unit.test_examination_service import setup_exam


def prepared_batch(db_session):
    exam_service, exam, subject, component, hall = setup_exam(db_session)
    exam_service.schedule_exam(ExamScheduleCreate(exam_id=exam.id, subject_id=subject.id, hall_id=hall.id, component_type="theory", exam_date=date(2026, 4, 6), start_time=time(9, 0), end_time=time(11, 0)))
    exam_service.publish_exam(exam.id)
    student = create_student(db_session)
    service = MarksEntryService(db_session, "college-a")
    batch = service.create_batch(MarksBatchCreate(exam_id=exam.id, section_id=exam.section_id, subject_id=subject.id, component_id=component.id), "teacher-1")
    return service, batch, student


def test_bulk_submit_lock_and_unlock_marks(db_session):
    service, batch, student = prepared_batch(db_session)
    entries = service.bulk_upsert(batch.id, BulkMarksUpsert(entries=[MarksEntryUpsert(student_id=student.id, marks_obtained=88)]), "teacher-1")
    assert entries[0].marks_obtained == 88
    submitted = service.submit_batch(batch.id, "teacher-1")
    assert submitted.status == "submitted"
    locked = service.lock_batch(batch.id, "principal-1")
    assert locked.status == "locked"
    unlocked = service.unlock_batch(batch.id, UnlockRequest(reason="Approved correction request"), "principal-1")
    assert unlocked.status == "draft"


def test_marks_validation_rejects_above_maximum(db_session):
    service, batch, student = prepared_batch(db_session)
    with pytest.raises(HTTPException) as exc:
        service.upsert_entry(batch.id, MarksEntryUpsert(student_id=student.id, marks_obtained=101), "teacher-1")
    assert exc.value.status_code == 409


def test_csv_import_and_audit(db_session):
    service, batch, student = prepared_batch(db_session)
    imported = service.import_marks(batch.id, MarksImportRequest(format="csv", content=f"student_id,marks_obtained,remarks\n{student.id},77,Good"), "teacher-1")
    assert imported[0].marks_obtained == 77
    audit, total = service.list_audit(batch.id, 20, 0)
    assert total >= 2
    assert audit
