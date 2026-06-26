from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.security import CurrentUser, Permission, require_permission
from app.db.session import get_db
from app.modules.students.models import StudentStatus
from app.modules.students.schemas import (
    AlumniCreate,
    DocumentCreate,
    DocumentRead,
    DocumentVerification,
    PromotionCreate,
    PromotionRead,
    StudentCreate,
    StudentList,
    StudentRead,
    StudentUpdate,
)
from app.modules.students.service import StudentService

router = APIRouter()


def get_service(db: Session, current_user: CurrentUser) -> StudentService:
    return StudentService(db=db, college_id=current_user.college_id)


@router.get("", response_model=StudentList)
def list_students(
    search: str | None = None,
    status_filter: StudentStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.STUDENT_READ)),
) -> StudentList:
    service = get_service(db, current_user)
    items, total = service.list_students(search, status_filter, limit, offset)
    return StudentList(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(
    payload: StudentCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.STUDENT_WRITE)),
):
    return get_service(db, current_user).create_student(payload)


@router.get("/{student_id}", response_model=StudentRead)
def get_student(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.STUDENT_READ)),
):
    return get_service(db, current_user).get_student(student_id)


@router.patch("/{student_id}", response_model=StudentRead)
def update_student(
    student_id: str,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.STUDENT_WRITE)),
):
    return get_service(db, current_user).update_student(student_id, payload)


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.STUDENT_DELETE)),
) -> Response:
    get_service(db, current_user).delete_student(student_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{student_id}/documents", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
def add_document(
    student_id: str,
    payload: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.STUDENT_WRITE)),
):
    return get_service(db, current_user).add_document(student_id, payload)


@router.post("/{student_id}/documents/{document_id}/verification", response_model=DocumentRead)
def verify_document(
    student_id: str,
    document_id: str,
    payload: DocumentVerification,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.DOCUMENT_VERIFY)),
):
    return get_service(db, current_user).verify_document(student_id, document_id, payload, current_user.user_id)


@router.post("/{student_id}/promotions", response_model=PromotionRead, status_code=status.HTTP_201_CREATED)
def promote_student(
    student_id: str,
    payload: PromotionCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.STUDENT_PROMOTE)),
):
    return get_service(db, current_user).promote_student(student_id, payload, current_user.user_id)


@router.post("/{student_id}/alumni", response_model=StudentRead)
def mark_alumni(
    student_id: str,
    payload: AlumniCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.STUDENT_ALUMNI)),
):
    return get_service(db, current_user).mark_alumni(student_id, payload, current_user.user_id)
