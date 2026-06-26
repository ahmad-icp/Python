from datetime import date, time

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.modules.examination.schemas import ExamScheduleCreate
from tests.unit.test_attendance_service import create_student
from tests.unit.test_examination_service import setup_exam

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


def test_marks_entry_api_permission_and_flow():
    with TestingSessionLocal() as db_session:
        exam_service, exam, subject, component, hall = setup_exam(db_session)
        exam_service.schedule_exam(ExamScheduleCreate(exam_id=exam.id, subject_id=subject.id, hall_id=hall.id, component_type="theory", exam_date=date(2026, 4, 6), start_time=time(9, 0), end_time=time(11, 0)))
        exam_service.publish_exam(exam.id)
        student = create_student(db_session)
        payload = {"exam_id": exam.id, "section_id": exam.section_id, "subject_id": subject.id, "component_id": component.id}
        student_id = student.id
    blocked = client.post("/api/v1/marks-entry/batches", json=payload, headers={"X-Role": "student"})
    assert blocked.status_code == 403
    batch = client.post("/api/v1/marks-entry/batches", json=payload, headers={"X-Role": "teacher", "X-User-Id": "teacher-1"})
    assert batch.status_code == 201
    response = client.post(f"/api/v1/marks-entry/batches/{batch.json()['id']}/entries", json={"entries": [{"student_id": student_id, "marks_obtained": 91}]}, headers={"X-Role": "teacher", "X-User-Id": "teacher-1"})
    assert response.status_code == 200
    assert response.json()[0]["student_id"] == student_id
