from datetime import date, time

import pytest
from fastapi import HTTPException

from app.modules.academic.models import Section
from app.modules.examination.schemas import AssessmentComponentCreate, ExamCreate, ExamHallCreate, ExamScheduleCreate, ExamTypeCreate, InvigilatorAssignmentCreate
from app.modules.examination.service import ExaminationService
from tests.unit.test_timetable_service import seed


def setup_exam(db_session):
    _, version, subject, _, _ = seed(db_session)
    section = db_session.get(Section, version.section_id)
    service = ExaminationService(db_session, "college-a")
    exam_type = service.create_exam_type(ExamTypeCreate(code="midterm", name="Midterm"))
    exam = service.create_exam(ExamCreate(exam_type_id=exam_type.id, session_id=version.session_id, class_id=section.class_id, section_id=section.id, name="Midterm Class 6A", start_date=date(2026, 4, 6), end_date=date(2026, 4, 10)), "principal-1")
    component = service.add_component(AssessmentComponentCreate(exam_id=exam.id, subject_id=subject.id, component_type="theory", name="Theory", maximum_marks=100, passing_marks=40, weightage=100))
    hall = service.create_hall(ExamHallCreate(name="Main Hall", code="HALL-1", capacity=60))
    return service, exam, subject, component, hall


def test_schedule_publish_and_lock_exam(db_session):
    service, exam, subject, _, hall = setup_exam(db_session)
    schedule = service.schedule_exam(ExamScheduleCreate(exam_id=exam.id, subject_id=subject.id, hall_id=hall.id, component_type="theory", exam_date=date(2026, 4, 6), start_time=time(9, 0), end_time=time(11, 0)))
    assignment = service.assign_invigilator(InvigilatorAssignmentCreate(schedule_id=schedule.id, teacher_id="t-1", teacher_name="Ada Teacher"), "principal-1")
    assert assignment.id
    published = service.publish_exam(exam.id)
    assert published.status == "published"
    locked = service.lock_exam(exam.id)
    assert locked.status == "locked"


def test_schedule_rejects_hall_conflict(db_session):
    service, exam, subject, _, hall = setup_exam(db_session)
    payload = ExamScheduleCreate(exam_id=exam.id, subject_id=subject.id, hall_id=hall.id, component_type="theory", exam_date=date(2026, 4, 6), start_time=time(9, 0), end_time=time(11, 0))
    service.schedule_exam(payload)
    with pytest.raises(HTTPException) as exc:
        service.schedule_exam(payload)
    assert exc.value.status_code == 409


def test_component_weightage_validation(db_session):
    service, exam, subject, _, _ = setup_exam(db_session)
    with pytest.raises(HTTPException) as exc:
        service.add_component(AssessmentComponentCreate(exam_id=exam.id, subject_id=subject.id, component_type="practical", name="Practical", maximum_marks=50, passing_marks=20, weightage=1))
    assert exc.value.status_code == 409
