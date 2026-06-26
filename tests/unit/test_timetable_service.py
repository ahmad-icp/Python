from datetime import date, time

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.modules.academic.schemas import AcademicClassCreate, AcademicSessionCreate, DepartmentCreate, InstitutionCreate, ProgramCreate, SectionCreate, SubjectAllocationCreate, SubjectCreate, TeacherAssignmentCreate
from app.modules.academic.service import AcademicService
from app.modules.timetable.schemas import ClassroomCreate, TimeSlotCreate, TimetableEntryCreate, TimetableVersionCreate, WorkingDayCreate
from app.modules.timetable.service import TimetableService


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as session:
        yield session


def seed(db_session):
    academic = AcademicService(db_session, "college-a")
    institution = academic.create_institution(InstitutionCreate(name="Demo College", code="DC"))
    department = academic.create_department(DepartmentCreate(institution_id=institution.id, name="Science", code="SCI"))
    session = academic.create_session(AcademicSessionCreate(name="2026-2027", start_date=date(2026, 4, 1), end_date=date(2027, 3, 31)))
    program = academic.create_program(ProgramCreate(department_id=department.id, name="Middle Science", code="MS", duration_years=3))
    klass = academic.create_class(AcademicClassCreate(program_id=program.id, session_id=session.id, name="Class 6"))
    section = academic.create_section(SectionCreate(class_id=klass.id, name="A", capacity=40, enrolled_count=30))
    subject = academic.create_subject(SubjectCreate(department_id=department.id, code="MATH", name="Mathematics", weekly_periods=5))
    academic.create_subject_allocation(SubjectAllocationCreate(class_id=klass.id, subject_id=subject.id, weekly_periods=5))
    academic.create_teacher_assignment(TeacherAssignmentCreate(teacher_id="t-1", teacher_name="Ada Teacher", section_id=section.id, subject_id=subject.id, weekly_periods=5, max_weekly_periods=30))
    timetable = TimetableService(db_session, "college-a")
    room = timetable.create_classroom(ClassroomCreate(name="Room 101", code="R101", capacity=40))
    slot = timetable.create_time_slot(TimeSlotCreate(name="P1", start_time=time(8, 0), end_time=time(8, 45), sort_order=1))
    timetable.set_working_day(WorkingDayCreate(session_id=session.id, weekday=1, is_working=True))
    version = timetable.create_version(TimetableVersionCreate(session_id=session.id, section_id=section.id, effective_from=date(2026, 4, 1), effective_to=date(2026, 4, 30)), "principal-1")
    return timetable, version, subject, room, slot


def test_add_entry_blocks_duplicate_section_slot(db_session):
    timetable, version, subject, room, slot = seed(db_session)
    payload = TimetableEntryCreate(version_id=version.id, subject_id=subject.id, teacher_id="t-1", teacher_name="Ada Teacher", classroom_id=room.id, time_slot_id=slot.id, weekday=1)
    entry = timetable.add_entry(payload)
    assert entry.id
    with pytest.raises(HTTPException) as exc:
        timetable.add_entry(payload)
    assert exc.value.status_code == 409


def test_room_capacity_validation(db_session):
    timetable, version, subject, _, slot = seed(db_session)
    small_room = timetable.create_classroom(ClassroomCreate(name="Small Room", code="SR", capacity=10))
    with pytest.raises(HTTPException) as exc:
        timetable.add_entry(TimetableEntryCreate(version_id=version.id, subject_id=subject.id, teacher_id="t-1", teacher_name="Ada Teacher", classroom_id=small_room.id, time_slot_id=slot.id, weekday=1))
    assert exc.value.status_code == 409


def test_publish_requires_entries_and_sets_status(db_session):
    timetable, version, subject, room, slot = seed(db_session)
    with pytest.raises(HTTPException):
        timetable.publish_version(version.id)
    timetable.add_entry(TimetableEntryCreate(version_id=version.id, subject_id=subject.id, teacher_id="t-1", teacher_name="Ada Teacher", classroom_id=room.id, time_slot_id=slot.id, weekday=1))
    published = timetable.publish_version(version.id)
    assert published.status == "published"
