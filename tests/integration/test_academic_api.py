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

def test_academic_configuration_flow_and_permissions():
    blocked = client.post("/api/v1/academic/institutions", json={"name":"Demo College","code":"DC"}, headers={"X-Role":"teacher"})
    assert blocked.status_code == 403
    institution = client.post("/api/v1/academic/institutions", json={"name":"Demo College","code":"DC"}, headers={"X-Role":"administrator"}).json()
    department = client.post("/api/v1/academic/departments", json={"institution_id": institution["id"], "name":"Science", "code":"SCI"}, headers={"X-Role":"administrator"}).json()
    session = client.post("/api/v1/academic/sessions", json={"name":"2026-2027", "start_date":"2026-04-01", "end_date":"2027-03-31"}, headers={"X-Role":"administrator"}).json()
    program = client.post("/api/v1/academic/programs", json={"department_id": department["id"], "name":"Science", "code":"SCI-P", "duration_years":3}, headers={"X-Role":"administrator"}).json()
    klass = client.post("/api/v1/academic/classes", json={"program_id": program["id"], "session_id": session["id"], "name":"Class 6"}, headers={"X-Role":"administrator"}).json()
    duplicate = client.post("/api/v1/academic/classes", json={"program_id": program["id"], "session_id": session["id"], "name":"class 6"}, headers={"X-Role":"administrator"})
    assert duplicate.status_code == 409
    section = client.post("/api/v1/academic/sections", json={"class_id": klass["id"], "name":"A", "capacity":40}, headers={"X-Role":"administrator"}).json()
    subject = client.post("/api/v1/academic/subjects", json={"department_id": department["id"], "code":"MATH", "name":"Mathematics", "weekly_periods":5}, headers={"X-Role":"administrator"}).json()
    assignment = client.post("/api/v1/academic/teacher-assignments", json={"teacher_id":"t-1", "teacher_name":"Ada Teacher", "section_id":section["id"], "subject_id":subject["id"], "weekly_periods":5}, headers={"X-Role":"administrator"})
    assert assignment.status_code == 201
    workload = client.get("/api/v1/academic/teacher-assignments/t-1/workload", headers={"X-Role":"teacher"})
    assert workload.status_code == 200
    assert workload.json()["assigned_periods"] == 5
