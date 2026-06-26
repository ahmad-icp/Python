from datetime import date

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.modules.admissions.models import AdmissionStatus, MeritListStatus
from app.modules.admissions.schemas import (
    AdmissionApplicationCreate,
    AdmissionDecision,
    AdmissionDocumentVerification,
    EnrollApplicant,
    MeritListCreate,
)
from app.modules.admissions.service import AdmissionService, calculate_merit_score
from app.modules.students.models import VerificationStatus


def application_payload(application_number="APP-001", obtained_marks=450, total_marks=500):
    return AdmissionApplicationCreate(
        application_number=application_number,
        mode="online",
        applicant_first_name="Hina",
        applicant_last_name="Malik",
        date_of_birth=date(2012, 3, 12),
        gender="female",
        address="Admissions Road Lahore",
        guardian_name="Nadia Malik",
        guardian_mobile="03001234567",
        program="Science",
        applying_for_class="6",
        preferred_section="A",
        academic_session="2026-2027",
        obtained_marks=obtained_marks,
        total_marks=total_marks,
        documents=[{"document_type": "b_form", "title": "B Form", "file_path": "storage/documents/app-bform.pdf"}],
    )


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as session:
        yield session


def test_create_application_calculates_merit_and_blocks_duplicates(db_session):
    service = AdmissionService(db_session, "college-a")
    application = service.create_application(application_payload())

    assert application.id
    assert float(application.merit_score) == 90.0
    assert application.status == AdmissionStatus.SUBMITTED

    with pytest.raises(HTTPException) as exc:
        service.create_application(application_payload("APP-002"))
    assert exc.value.status_code == 409


def test_document_verification_and_decision_flow(db_session):
    service = AdmissionService(db_session, "college-a")
    application = service.create_application(application_payload())
    document = application.documents[0]

    verified = service.verify_document(
        application.id,
        document.id,
        AdmissionDocumentVerification(status=VerificationStatus.VERIFIED),
        verified_by="admission-officer-1",
    )
    assert verified.verification_status == VerificationStatus.VERIFIED
    assert application.status == AdmissionStatus.ELIGIBLE

    decided = service.decide_application(
        application.id,
        AdmissionDecision(status=AdmissionStatus.OFFERED),
        reviewed_by="principal-1",
    )
    assert decided.status == AdmissionStatus.OFFERED
    assert decided.reviewed_by == "principal-1"


def test_merit_list_generation_publish_and_enrollment(db_session):
    service = AdmissionService(db_session, "college-a")
    application = service.create_application(application_payload())
    service.verify_document(
        application.id,
        application.documents[0].id,
        AdmissionDocumentVerification(status=VerificationStatus.VERIFIED),
        verified_by="admission-officer-1",
    )

    merit_list = service.create_merit_list(
        MeritListCreate(
            title="First Merit List",
            program="Science",
            academic_session="2026-2027",
            list_number=1,
            capacity=10,
            minimum_score=80,
            offer_expires_on=date(2026, 5, 1),
        ),
        created_by="principal-1",
    )
    assert merit_list.status == MeritListStatus.DRAFT
    assert len(merit_list.entries) == 1
    assert merit_list.entries[0].position == 1

    published = service.publish_merit_list(merit_list.id)
    assert published.status == MeritListStatus.PUBLISHED
    assert application.status == AdmissionStatus.OFFERED

    student = service.enroll_applicant(
        application.id,
        EnrollApplicant(admission_number="STU-001", roll_number="R-1", section="A", enrollment_date=date(2026, 4, 10)),
        admitted_by="principal-1",
    )
    assert student.admission_number == "STU-001"
    assert application.status == AdmissionStatus.ADMITTED
    assert application.admitted_student_id == student.id


def test_calculate_merit_score_handles_missing_marks():
    assert calculate_merit_score(None, None) is None
    assert calculate_merit_score(45, 50) == 90.0
