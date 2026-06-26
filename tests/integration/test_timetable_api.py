from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app

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

def seed_academic():
    institution = client.post("/api/v1/academic/institutions", json={"name":"Demo College","code":"DC"}, headers={"X-Role":"administrator"}).json()
    department = client.post("/api/v1/academic/departments", json={"institution_id": institution["id"], "name":"Science", "code":"SCI"}, headers={"X-Role":"administrator"}).json()
    session = client.post("/api/v1/academic/sessions", json={"name":"2026-2027", "start_date":"2026-04-01", "end_date":"2027-03-31"}, headers={"X-Role":"administrator"}).json()
    program = client.post("/api/v1/academic/programs", json={"department_id": department["id"], "name":"Science", "code":"SCI-P", "duration_years":3}, headers={"X-Role":"administrator"}).json()
    klass = client.post("/api/v1/academic/classes", json={"program_id": program["id"], "session_id": session["id"], "name":"Class 6"}, headers={"X-Role":"administrator"}).json()
    section = client.post("/api/v1/academic/sections", json={"class_id": klass["id"], "name":"A", "capacity":40, "enrolled_count":30}, headers={"X-Role":"administrator"}).json()
    subject = client.post("/api/v1/academic/subjects", json={"department_id": department["id"], "code":"MATH", "name":"Mathematics", "weekly_periods":5}, headers={"X-Role":"administrator"}).json()
    client.post("/api/v1/academic/subject-allocations", json={"class_id": klass["id"], "subject_id": subject["id"], "weekly_periods":5}, headers={"X-Role":"administrator"})
    client.post("/api/v1/academic/teacher-assignments", json={"teacher_id":"t-1", "teacher_name":"Ada Teacher", "section_id":section["id"], "subject_id":subject["id"], "weekly_periods":5}, headers={"X-Role":"administrator"})
    return session, section, subject

def test_timetable_flow_clash_and_permissions():
    session, section, subject = seed_academic()
    blocked = client.post("/api/v1/timetable/classrooms", json={"name":"Room 101", "code":"R101", "capacity":40}, headers={"X-Role":"teacher"})
    assert blocked.status_code == 403
    room = client.post("/api/v1/timetable/classrooms", json={"name":"Room 101", "code":"R101", "capacity":40}, headers={"X-Role":"administrator"}).json()
    slot = client.post("/api/v1/timetable/time-slots", json={"name":"P1", "start_time":"08:00:00", "end_time":"08:45:00", "sort_order":1}, headers={"X-Role":"administrator"}).json()
    client.post("/api/v1/timetable/working-days", json={"session_id": session["id"], "weekday":1}, headers={"X-Role":"administrator"})
    version = client.post("/api/v1/timetable/versions", json={"session_id":session["id"], "section_id":section["id"], "effective_from":"2026-04-01", "effective_to":"2026-04-30"}, headers={"X-Role":"administrator", "X-User-Id":"principal-1"}).json()
    entry_payload = {"version_id":version["id"], "subject_id":subject["id"], "teacher_id":"t-1", "teacher_name":"Ada Teacher", "classroom_id":room["id"], "time_slot_id":slot["id"], "weekday":1}
    created = client.post("/api/v1/timetable/entries", json=entry_payload, headers={"X-Role":"administrator"})
    assert created.status_code == 201
    duplicate = client.post("/api/v1/timetable/entries", json=entry_payload, headers={"X-Role":"administrator"})
    assert duplicate.status_code == 409
    published = client.post(f"/api/v1/timetable/versions/{version['id']}/publish", headers={"X-Role":"administrator"})
    assert published.status_code == 200
    assert published.json()["status"] == "published"
    teacher_view = client.get("/api/v1/timetable/entries?teacher_id=t-1", headers={"X-Role":"teacher"})
    assert teacher_view.status_code == 200
    assert teacher_view.json()["total"] == 1
