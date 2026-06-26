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
        "admission_number": "ADM-API-001",
        "first_name": "Bilal",
        "last_name": "Ahmed",
        "date_of_birth": str(date(2011, 1, 15)),
        "gender": "male",
        "address": "Main Campus Road",
        "program": "Computer Science",
        "current_class": "7",
        "current_section": "C",
        "academic_session": "2026-2027",
        "enrollment_date": str(date(2026, 4, 2)),
        "guardians": [{"full_name": "Sara Ahmed", "relationship": "mother", "mobile": "03001234567", "is_primary": True}],
        "documents": [],
    }


def test_student_crud_promotion_and_alumni_flow():
    create_response = client.post("/api/v1/students", json=payload(), headers={"X-Role": "administrator"})
    assert create_response.status_code == 201
    student = create_response.json()

    list_response = client.get("/api/v1/students", headers={"X-Role": "teacher"})
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1

    patch_response = client.patch(
        f"/api/v1/students/{student['id']}",
        json={"current_section": "D"},
        headers={"X-Role": "administrator"},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["current_section"] == "D"

    promotion_response = client.post(
        f"/api/v1/students/{student['id']}/promotions",
        json={"to_class": "8", "to_section": "A", "to_session": "2027-2028", "promoted_on": "2027-04-01"},
        headers={"X-Role": "principal", "X-User-Id": "principal-1"},
    )
    assert promotion_response.status_code == 201
    assert promotion_response.json()["to_class"] == "8"

    alumni_response = client.post(
        f"/api/v1/students/{student['id']}/alumni",
        json={"graduation_date": "2030-04-01", "remarks": "Completed"},
        headers={"X-Role": "principal"},
    )
    assert alumni_response.status_code == 200
    assert alumni_response.json()["status"] == "alumni"


def test_rbac_blocks_teacher_write_access():
    response = client.post("/api/v1/students", json=payload(), headers={"X-Role": "teacher"})
    assert response.status_code == 403
