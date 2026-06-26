from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.modules.attendance.schemas import AttendanceSessionCreate
from app.modules.attendance.service import AttendanceService
from app.modules.students.schemas import GuardianCreate, StudentCreate
from app.modules.students.service import StudentService
from tests.unit.test_timetable_service import seed

engine = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def override_get_db():
    with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def test_attendance_api_marks_records():
    with TestingSessionLocal() as db_session:
        _, version, _, _, slot = seed(db_session)
        student = StudentService(db_session, "college-a").create_student(StudentCreate(admission_number="ADM-API-1", first_name="Sara", last_name="Ahmed", date_of_birth=date(2014, 2, 1), gender="female", address="Main campus road", program="Middle Science", current_class="Class 6", current_section="A", academic_session="2026-2027", enrollment_date=date(2026, 4, 1), guardians=[GuardianCreate(full_name="Parent Ahmed", relationship="mother", mobile="03111111111", is_primary=True)]))
        attendance = AttendanceService(db_session, "college-a").create_session(AttendanceSessionCreate(session_id=version.session_id, section_id=version.section_id, attendance_date=date(2026, 4, 6), teacher_id="t-1", teacher_name="Ada Teacher", time_slot_id=slot.id))
        attendance_id = attendance.id
        student_id = student.id
    response = client.post(f"/api/v1/attendance/sessions/{attendance_id}/records", json={"records": [{"student_id": student_id, "status": "present"}]})
    assert response.status_code == 200
    assert response.json()[0]["student_id"] == student_id
