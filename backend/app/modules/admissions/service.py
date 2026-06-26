from datetime import UTC, datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.modules.admissions.models import (
    AdmissionApplication,
    AdmissionDocument,
    AdmissionStatus,
    MeritList,
    MeritListEntry,
    MeritListStatus,
)
from app.modules.admissions.schemas import (
    AdmissionApplicationCreate,
    AdmissionApplicationUpdate,
    AdmissionDecision,
    AdmissionDocumentCreate,
    AdmissionDocumentVerification,
    EnrollApplicant,
    MeritListCreate,
)
from app.modules.students.models import StudentStatus, VerificationStatus
from app.modules.students.schemas import GuardianCreate, StudentCreate
from app.modules.students.service import StudentService, normalize_identity


def calculate_merit_score(obtained_marks: float | Decimal | None, total_marks: float | Decimal | None) -> float | None:
    if obtained_marks is None or total_marks is None:
        return None
    return round(float(obtained_marks) / float(total_marks) * 100, 4)


class AdmissionService:
    def __init__(self, db: Session, college_id: str) -> None:
        self.db = db
        self.college_id = college_id

    def list_applications(
        self,
        search: str | None,
        status_filter: AdmissionStatus | None,
        program: str | None,
        academic_session: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[AdmissionApplication], int]:
        query = select(AdmissionApplication).where(AdmissionApplication.college_id == self.college_id)
        if status_filter:
            query = query.where(AdmissionApplication.status == status_filter)
        if program:
            query = query.where(AdmissionApplication.program == program)
        if academic_session:
            query = query.where(AdmissionApplication.academic_session == academic_session)
        if search:
            term = f"%{search.strip()}%"
            query = query.where(
                or_(
                    AdmissionApplication.application_number.ilike(term),
                    AdmissionApplication.applicant_first_name.ilike(term),
                    AdmissionApplication.applicant_last_name.ilike(term),
                    AdmissionApplication.guardian_mobile.ilike(term),
                )
            )
        total = self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
        items = self.db.scalars(query.order_by(AdmissionApplication.submitted_at.desc()).limit(limit).offset(offset)).unique().all()
        return list(items), total

    def get_application(self, application_id: str) -> AdmissionApplication:
        application = self.db.get(AdmissionApplication, application_id)
        if not application or application.college_id != self.college_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admission application not found")
        return application

    def create_application(self, payload: AdmissionApplicationCreate) -> AdmissionApplication:
        normalized_identity = normalize_identity(
            payload.applicant_first_name, payload.applicant_last_name, payload.date_of_birth, payload.guardian_mobile
        )
        duplicate = self.db.scalar(
            select(AdmissionApplication).where(
                AdmissionApplication.college_id == self.college_id,
                or_(
                    AdmissionApplication.application_number == payload.application_number,
                    AdmissionApplication.normalized_identity == normalized_identity,
                ),
            )
        )
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An admission application with the same number or applicant identity already exists",
            )
        application = AdmissionApplication(
            college_id=self.college_id,
            normalized_identity=normalized_identity,
            merit_score=calculate_merit_score(payload.obtained_marks, payload.total_marks),
            **payload.model_dump(exclude={"documents"}),
        )
        application.documents = [AdmissionDocument(**document.model_dump()) for document in payload.documents]
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def update_application(self, application_id: str, payload: AdmissionApplicationUpdate) -> AdmissionApplication:
        application = self.get_application(application_id)
        if application.status in {AdmissionStatus.ADMITTED, AdmissionStatus.CANCELLED}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Finalized applications cannot be edited")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(application, field, value)
        application.merit_score = calculate_merit_score(application.obtained_marks, application.total_marks)
        self.db.commit()
        self.db.refresh(application)
        return application

    def add_document(self, application_id: str, payload: AdmissionDocumentCreate) -> AdmissionDocument:
        application = self.get_application(application_id)
        if application.status in {AdmissionStatus.ADMITTED, AdmissionStatus.CANCELLED}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot add documents to finalized applications")
        document = AdmissionDocument(application_id=application.id, **payload.model_dump())
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def verify_document(
        self, application_id: str, document_id: str, payload: AdmissionDocumentVerification, verified_by: str
    ) -> AdmissionDocument:
        application = self.get_application(application_id)
        document = self.db.get(AdmissionDocument, document_id)
        if not document or document.application_id != application.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admission document not found")
        document.verification_status = payload.status
        document.verified_by = verified_by
        document.verified_at = datetime.now(UTC)
        document.rejection_reason = payload.rejection_reason if payload.status == VerificationStatus.REJECTED else None
        if payload.status == VerificationStatus.REJECTED:
            application.status = AdmissionStatus.DOCUMENTS_PENDING
        elif application.documents and all(doc.verification_status == VerificationStatus.VERIFIED for doc in application.documents):
            application.status = AdmissionStatus.ELIGIBLE
        self.db.commit()
        self.db.refresh(document)
        return document

    def decide_application(self, application_id: str, payload: AdmissionDecision, reviewed_by: str) -> AdmissionApplication:
        application = self.get_application(application_id)
        if application.status == AdmissionStatus.ADMITTED:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Admitted applications cannot be changed")
        application.status = payload.status
        application.decision_reason = payload.reason
        application.reviewed_by = reviewed_by
        application.reviewed_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(application)
        return application

    def create_merit_list(self, payload: MeritListCreate, created_by: str) -> MeritList:
        minimum_score = payload.minimum_score if payload.minimum_score is not None else 0
        eligible_query = (
            select(AdmissionApplication)
            .where(
                AdmissionApplication.college_id == self.college_id,
                AdmissionApplication.program == payload.program,
                AdmissionApplication.academic_session == payload.academic_session,
                AdmissionApplication.status.in_([AdmissionStatus.ELIGIBLE, AdmissionStatus.OFFERED, AdmissionStatus.MERIT_LISTED]),
                AdmissionApplication.merit_score.is_not(None),
                AdmissionApplication.merit_score >= minimum_score,
            )
            .order_by(AdmissionApplication.merit_score.desc(), AdmissionApplication.submitted_at.asc())
            .limit(payload.capacity)
        )
        applications = list(self.db.scalars(eligible_query).unique().all())
        if not applications:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No eligible applications found for merit list")
        merit_list = MeritList(
            college_id=self.college_id,
            title=payload.title,
            program=payload.program,
            academic_session=payload.academic_session,
            list_number=payload.list_number,
            minimum_score=payload.minimum_score,
            created_by=created_by,
        )
        merit_list.entries = [
            MeritListEntry(
                application_id=application.id,
                position=index,
                score=float(application.merit_score or 0),
                offer_expires_on=payload.offer_expires_on,
            )
            for index, application in enumerate(applications, start=1)
        ]
        for application in applications:
            application.status = AdmissionStatus.MERIT_LISTED
        self.db.add(merit_list)
        self.db.commit()
        self.db.refresh(merit_list)
        return merit_list

    def publish_merit_list(self, merit_list_id: str) -> MeritList:
        merit_list = self._get_merit_list(merit_list_id)
        if merit_list.status == MeritListStatus.LOCKED:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Locked merit lists cannot be republished")
        merit_list.status = MeritListStatus.PUBLISHED
        merit_list.published_at = datetime.now(UTC)
        for entry in merit_list.entries:
            entry.application.status = AdmissionStatus.OFFERED
        self.db.commit()
        self.db.refresh(merit_list)
        return merit_list

    def enroll_applicant(self, application_id: str, payload: EnrollApplicant, admitted_by: str):
        application = self.get_application(application_id)
        if application.status not in {AdmissionStatus.OFFERED, AdmissionStatus.ELIGIBLE, AdmissionStatus.MERIT_LISTED}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only eligible or offered applicants can be enrolled")
        if application.documents and any(doc.verification_status != VerificationStatus.VERIFIED for doc in application.documents):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="All submitted documents must be verified before enrollment")
        student_payload = StudentCreate(
            admission_number=payload.admission_number,
            roll_number=payload.roll_number,
            first_name=application.applicant_first_name,
            last_name=application.applicant_last_name,
            date_of_birth=application.date_of_birth,
            gender=application.gender,
            email=application.email,
            mobile=application.mobile,
            address=application.address,
            program=application.program,
            current_class=application.applying_for_class,
            current_section=payload.section or application.preferred_section,
            academic_session=application.academic_session,
            enrollment_date=payload.enrollment_date,
            guardians=[
                GuardianCreate(
                    full_name=application.guardian_name,
                    relationship="guardian",
                    mobile=application.guardian_mobile,
                    email=application.guardian_email,
                    is_primary=True,
                )
            ],
            documents=[],
        )
        student = StudentService(self.db, self.college_id).create_student(student_payload)
        student.status = StudentStatus.ACTIVE
        application.status = AdmissionStatus.ADMITTED
        application.admitted_student_id = student.id
        application.reviewed_by = admitted_by
        application.reviewed_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(application)
        self.db.refresh(student)
        return student

    def _get_merit_list(self, merit_list_id: str) -> MeritList:
        merit_list = self.db.get(MeritList, merit_list_id)
        if not merit_list or merit_list.college_id != self.college_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merit list not found")
        return merit_list
