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


def payload():
    return {
        "application_number": "APP-API-001",
        "mode": "offline",
        "applicant_first_name": "Omar",
        "applicant_last_name": "Farooq",
        "date_of_birth": str(date(2012, 2, 2)),
        "gender": "male",
        "address": "Admission Office Campus",
        "guardian_name": "Farah Farooq",
        "guardian_mobile": "03007654321",
        "program": "Science",
        "applying_for_class": "6",
        "preferred_section": "B",
        "academic_session": "2026-2027",
        "obtained_marks": 470,
        "total_marks": 500,
        "documents": [{"document_type": "b_form", "title": "B Form", "file_path": "storage/documents/api-bform.pdf"}],
    }


def test_admission_application_merit_and_enrollment_flow():
    create_response = client.post("/api/v1/admissions/applications", json=payload(), headers={"X-Role": "admission_officer"})
    assert create_response.status_code == 201
    application = create_response.json()
    assert application["merit_score"] == 94.0

    document_id = application["documents"][0]["id"]
    verify_response = client.post(
        f"/api/v1/admissions/applications/{application['id']}/documents/{document_id}/verification",
        json={"status": "verified"},
        headers={"X-Role": "admission_officer", "X-User-Id": "officer-1"},
    )
    assert verify_response.status_code == 200

    merit_response = client.post(
        "/api/v1/admissions/merit-lists",
        json={
            "title": "First Merit List",
            "program": "Science",
            "academic_session": "2026-2027",
            "list_number": 1,
            "capacity": 10,
            "minimum_score": 80,
            "offer_expires_on": "2026-05-01",
        },
        headers={"X-Role": "principal", "X-User-Id": "principal-1"},
    )
    assert merit_response.status_code == 201
    merit_list = merit_response.json()
    assert len(merit_list["entries"]) == 1

    publish_response = client.post(
        f"/api/v1/admissions/merit-lists/{merit_list['id']}/publish",
        headers={"X-Role": "principal"},
    )
    assert publish_response.status_code == 200
    assert publish_response.json()["status"] == "published"

    enroll_response = client.post(
        f"/api/v1/admissions/applications/{application['id']}/enroll",
        json={"admission_number": "STU-API-001", "roll_number": "R-100", "section": "B", "enrollment_date": "2026-04-15"},
        headers={"X-Role": "principal", "X-User-Id": "principal-1"},
    )
    assert enroll_response.status_code == 201
    assert enroll_response.json()["admission_number"] == "STU-API-001"


def test_teacher_cannot_create_admission_application():
    response = client.post("/api/v1/admissions/applications", json=payload(), headers={"X-Role": "teacher"})
    assert response.status_code == 403
