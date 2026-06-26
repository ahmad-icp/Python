from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.modules.students.models import (
    Student,
    StudentDocument,
    StudentGuardian,
    StudentPromotion,
    StudentStatus,
    VerificationStatus,
)
from app.modules.students.schemas import (
    AlumniCreate,
    DocumentCreate,
    DocumentVerification,
    PromotionCreate,
    StudentCreate,
    StudentUpdate,
)


def normalize_identity(first_name: str, last_name: str, date_of_birth: object, primary_mobile: str) -> str:
    return "|".join(
        [
            first_name.strip().casefold(),
            last_name.strip().casefold(),
            str(date_of_birth),
            "".join(ch for ch in primary_mobile if ch.isdigit()),
        ]
    )


class StudentService:
    def __init__(self, db: Session, college_id: str) -> None:
        self.db = db
        self.college_id = college_id

    def list_students(self, search: str | None, status_filter: StudentStatus | None, limit: int, offset: int) -> tuple[list[Student], int]:
        query = select(Student).where(Student.college_id == self.college_id)
        if status_filter:
            query = query.where(Student.status == status_filter)
        if search:
            term = f"%{search.strip()}%"
            query = query.where(
                or_(Student.first_name.ilike(term), Student.last_name.ilike(term), Student.admission_number.ilike(term))
            )
        total = self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
        items = self.db.scalars(query.order_by(Student.created_at.desc()).limit(limit).offset(offset)).unique().all()
        return list(items), total

    def get_student(self, student_id: str) -> Student:
        student = self.db.get(Student, student_id)
        if not student or student.college_id != self.college_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        return student

    def create_student(self, payload: StudentCreate) -> Student:
        primary_guardian = next(guardian for guardian in payload.guardians if guardian.is_primary)
        normalized_identity = normalize_identity(
            payload.first_name, payload.last_name, payload.date_of_birth, primary_guardian.mobile
        )
        duplicate = self.db.scalar(
            select(Student).where(
                Student.college_id == self.college_id,
                or_(
                    Student.admission_number == payload.admission_number,
                    Student.normalized_identity == normalized_identity,
                ),
            )
        )
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A student with the same admission number or identity already exists",
            )
        student = Student(
            college_id=self.college_id,
            normalized_identity=normalized_identity,
            **payload.model_dump(exclude={"guardians", "documents"}),
        )
        student.guardians = [StudentGuardian(**guardian.model_dump()) for guardian in payload.guardians]
        student.documents = [StudentDocument(**document.model_dump()) for document in payload.documents]
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

    def update_student(self, student_id: str, payload: StudentUpdate) -> Student:
        student = self.get_student(student_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(student, field, value)
        self.db.commit()
        self.db.refresh(student)
        return student

    def delete_student(self, student_id: str) -> None:
        student = self.get_student(student_id)
        if student.status == StudentStatus.ACTIVE:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Active students must be withdrawn before deletion")
        self.db.delete(student)
        self.db.commit()

    def add_document(self, student_id: str, payload: DocumentCreate) -> StudentDocument:
        student = self.get_student(student_id)
        document = StudentDocument(student_id=student.id, **payload.model_dump())
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def verify_document(self, student_id: str, document_id: str, payload: DocumentVerification, verified_by: str) -> StudentDocument:
        self.get_student(student_id)
        document = self.db.get(StudentDocument, document_id)
        if not document or document.student_id != student_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        document.verification_status = payload.status
        document.verified_by = verified_by
        document.verified_at = datetime.now(UTC)
        document.rejection_reason = payload.rejection_reason if payload.status == VerificationStatus.REJECTED else None
        self.db.commit()
        self.db.refresh(document)
        return document

    def promote_student(self, student_id: str, payload: PromotionCreate, promoted_by: str) -> StudentPromotion:
        student = self.get_student(student_id)
        if student.status not in {StudentStatus.ACTIVE, StudentStatus.APPLICANT}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only active/applicant students can be promoted")
        promotion = StudentPromotion(
            student_id=student.id,
            from_class=student.current_class,
            from_section=student.current_section,
            from_session=student.academic_session,
            to_class=payload.to_class,
            to_section=payload.to_section,
            to_session=payload.to_session,
            promoted_on=payload.promoted_on,
            remarks=payload.remarks,
            promoted_by=promoted_by,
        )
        student.current_class = payload.to_class
        student.current_section = payload.to_section
        student.academic_session = payload.to_session
        student.status = StudentStatus.ACTIVE
        self.db.add(promotion)
        self.db.commit()
        self.db.refresh(promotion)
        return promotion

    def mark_alumni(self, student_id: str, payload: AlumniCreate, updated_by: str) -> Student:
        student = self.get_student(student_id)
        if student.status == StudentStatus.ALUMNI:
            return student
        promotion = StudentPromotion(
            student_id=student.id,
            from_class=student.current_class,
            from_section=student.current_section,
            from_session=student.academic_session,
            to_class="Alumni",
            to_section=None,
            to_session=student.academic_session,
            promoted_on=payload.graduation_date,
            promoted_by=updated_by,
            remarks=payload.remarks,
        )
        student.status = StudentStatus.ALUMNI
        self.db.add(promotion)
        self.db.commit()
        self.db.refresh(student)
        return student
