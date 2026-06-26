from datetime import date

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.modules.academic.schemas import AcademicClassCreate, AcademicSessionCreate, DepartmentCreate, InstitutionCreate, ProgramCreate, SectionCreate, SubjectAllocationCreate, SubjectCreate, TeacherAssignmentCreate
from app.modules.academic.service import AcademicService

@pytest.fixture()
def db_session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as session:
        yield session

def seed(service: AcademicService):
    institution = service.create_institution(InstitutionCreate(name="Demo College", code="DC"))
    department = service.create_department(DepartmentCreate(institution_id=institution.id, name="Science", code="SCI"))
    session = service.create_session(AcademicSessionCreate(name="2026-2027", start_date=date(2026, 4, 1), end_date=date(2027, 3, 31)))
    program = service.create_program(ProgramCreate(department_id=department.id, name="Middle Science", code="MS", duration_years=3))
    klass = service.create_class(AcademicClassCreate(program_id=program.id, session_id=session.id, name="Class 6"))
    return institution, department, session, program, klass

def test_duplicate_class_blocked_within_program_session(db_session):
    service = AcademicService(db_session, "college-a")
    _, _, _, program, klass = seed(service)
    assert klass.name == "Class 6"
    with pytest.raises(HTTPException) as exc:
        service.create_class(AcademicClassCreate(program_id=program.id, session_id=klass.session_id, name="class 6"))
    assert exc.value.status_code == 409

def test_section_capacity_validation(db_session):
    service = AcademicService(db_session, "college-a")
    *_, klass = seed(service)
    with pytest.raises(ValueError):
        SectionCreate(class_id=klass.id, name="A", capacity=10, enrolled_count=11)

def test_subject_prerequisite_and_teacher_workload(db_session):
    service = AcademicService(db_session, "college-a")
    _, department, _, _, klass = seed(service)
    section = service.create_section(SectionCreate(class_id=klass.id, name="A", capacity=40, enrolled_count=20))
    math = service.create_subject(SubjectCreate(department_id=department.id, code="MATH", name="Mathematics", weekly_periods=5))
    physics = service.create_subject(SubjectCreate(department_id=department.id, code="PHY", name="Physics", weekly_periods=4, prerequisite_subject_ids=[math.id]))
    with pytest.raises(HTTPException) as exc:
        service.create_subject_allocation(SubjectAllocationCreate(class_id=klass.id, subject_id=physics.id, weekly_periods=4))
    assert exc.value.status_code == 409
    service.create_subject_allocation(SubjectAllocationCreate(class_id=klass.id, subject_id=math.id, weekly_periods=5))
    service.create_subject_allocation(SubjectAllocationCreate(class_id=klass.id, subject_id=physics.id, weekly_periods=4))
    service.create_teacher_assignment(TeacherAssignmentCreate(teacher_id="t-1", teacher_name="Ada Teacher", section_id=section.id, subject_id=math.id, weekly_periods=5, max_weekly_periods=8))
    with pytest.raises(HTTPException):
        service.create_teacher_assignment(TeacherAssignmentCreate(teacher_id="t-1", teacher_name="Ada Teacher", section_id=section.id, subject_id=physics.id, weekly_periods=4, max_weekly_periods=8))
    workload = service.teacher_workload("t-1")
    assert workload.assigned_periods == 5
