from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.modules.academic.models import Section
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


def test_examination_api_permissions_and_creation():
    with TestingSessionLocal() as db_session:
        _, version, _, _, _ = seed(db_session)
        section = db_session.get(Section, version.section_id)
        session_id = version.session_id
        class_id = section.class_id
        section_id = section.id
    blocked = client.post("/api/v1/examinations/types", json={"code": "final", "name": "Final"}, headers={"X-Role": "teacher"})
    assert blocked.status_code == 403
    exam_type = client.post("/api/v1/examinations/types", json={"code": "final", "name": "Final"}, headers={"X-Role": "administrator"})
    assert exam_type.status_code == 201
    exam = client.post("/api/v1/examinations/exams", json={"exam_type_id": exam_type.json()["id"], "session_id": session_id, "class_id": class_id, "section_id": section_id, "name": "Final Class 6A", "start_date": "2026-04-06", "end_date": "2026-04-10"}, headers={"X-Role": "administrator", "X-User-Id": "principal-1"})
    assert exam.status_code == 201
    assert exam.json()["status"] == "draft"
