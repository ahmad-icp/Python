from datetime import date

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.modules.students.models import StudentStatus, VerificationStatus
from app.modules.students.schemas import AlumniCreate, DocumentVerification, PromotionCreate, StudentCreate
from app.modules.students.service import StudentService, normalize_identity


def make_payload(admission_number="ADM-001"):
    return StudentCreate(
        admission_number=admission_number,
        first_name="Ayesha",
        last_name="Khan",
        date_of_birth=date(2010, 5, 1),
        gender="female",
        address="College Road Lahore",
        program="Science",
        current_class="8",
        current_section="A",
        academic_session="2026-2027",
        enrollment_date=date(2026, 4, 1),
        guardians=[{
            "full_name": "Imran Khan",
            "relationship": "father",
            "mobile": "+92 300 1234567",
            "is_primary": True,
        }],
        documents=[{"document_type": "b_form", "title": "B Form", "file_path": "storage/documents/bform.pdf"}],
    )


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as session:
        yield session


def test_create_student_prevents_duplicate_identity(db_session):
    service = StudentService(db_session, "college-a")
    created = service.create_student(make_payload())

    assert created.id
    assert created.status == StudentStatus.ACTIVE
    assert created.guardians[0].is_primary is True

    with pytest.raises(HTTPException) as exc:
        service.create_student(make_payload("ADM-002"))
    assert exc.value.status_code == 409


def test_promote_and_mark_alumni(db_session):
    service = StudentService(db_session, "college-a")
    student = service.create_student(make_payload())

    promotion = service.promote_student(
        student.id,
        PromotionCreate(to_class="9", to_section="B", to_session="2027-2028", promoted_on=date(2027, 4, 1)),
        promoted_by="principal-1",
    )
    assert promotion.from_class == "8"
    assert promotion.to_class == "9"
    assert student.current_class == "9"

    alumni = service.mark_alumni(student.id, AlumniCreate(graduation_date=date(2030, 4, 1), remarks="Graduated"), "principal-1")
    assert alumni.status == StudentStatus.ALUMNI


def test_document_verification_records_auditor(db_session):
    service = StudentService(db_session, "college-a")
    student = service.create_student(make_payload())
    document = student.documents[0]

    verified = service.verify_document(
        student.id,
        document.id,
        DocumentVerification(status=VerificationStatus.VERIFIED),
        verified_by="admission-officer-1",
    )
    assert verified.verification_status == VerificationStatus.VERIFIED
    assert verified.verified_by == "admission-officer-1"
    assert verified.verified_at is not None


def test_normalize_identity_removes_mobile_formatting():
    assert normalize_identity(" Ayesha ", "KHAN", date(2010, 5, 1), "+92 300-123") == "ayesha|khan|2010-05-01|92300123"
