from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import CurrentUser, Permission, require_permission
from app.db.session import get_db
from app.modules.admissions.models import AdmissionStatus
from app.modules.admissions.schemas import (
    AdmissionApplicationCreate,
    AdmissionApplicationList,
    AdmissionApplicationRead,
    AdmissionApplicationUpdate,
    AdmissionDecision,
    AdmissionDocumentCreate,
    AdmissionDocumentRead,
    AdmissionDocumentVerification,
    EnrollApplicant,
    MeritListCreate,
    MeritListRead,
)
from app.modules.admissions.service import AdmissionService
from app.modules.students.schemas import StudentRead

router = APIRouter()


def get_service(db: Session, current_user: CurrentUser) -> AdmissionService:
    return AdmissionService(db=db, college_id=current_user.college_id)


@router.get("/applications", response_model=AdmissionApplicationList)
def list_applications(
    search: str | None = None,
    status_filter: AdmissionStatus | None = Query(default=None, alias="status"),
    program: str | None = None,
    academic_session: str | None = None,
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.ADMISSION_READ)),
) -> AdmissionApplicationList:
    service = get_service(db, current_user)
    items, total = service.list_applications(search, status_filter, program, academic_session, limit, offset)
    return AdmissionApplicationList(items=items, total=total, limit=limit, offset=offset)


@router.post("/applications", response_model=AdmissionApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(
    payload: AdmissionApplicationCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.ADMISSION_WRITE)),
):
    return get_service(db, current_user).create_application(payload)


@router.get("/applications/{application_id}", response_model=AdmissionApplicationRead)
def get_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.ADMISSION_READ)),
):
    return get_service(db, current_user).get_application(application_id)


@router.patch("/applications/{application_id}", response_model=AdmissionApplicationRead)
def update_application(
    application_id: str,
    payload: AdmissionApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.ADMISSION_WRITE)),
):
    return get_service(db, current_user).update_application(application_id, payload)


@router.post("/applications/{application_id}/documents", response_model=AdmissionDocumentRead, status_code=status.HTTP_201_CREATED)
def add_document(
    application_id: str,
    payload: AdmissionDocumentCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.ADMISSION_WRITE)),
):
    return get_service(db, current_user).add_document(application_id, payload)


@router.post("/applications/{application_id}/documents/{document_id}/verification", response_model=AdmissionDocumentRead)
def verify_document(
    application_id: str,
    document_id: str,
    payload: AdmissionDocumentVerification,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.DOCUMENT_VERIFY)),
):
    return get_service(db, current_user).verify_document(application_id, document_id, payload, current_user.user_id)


@router.post("/applications/{application_id}/decision", response_model=AdmissionApplicationRead)
def decide_application(
    application_id: str,
    payload: AdmissionDecision,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.ADMISSION_DECIDE)),
):
    return get_service(db, current_user).decide_application(application_id, payload, current_user.user_id)


@router.post("/merit-lists", response_model=MeritListRead, status_code=status.HTTP_201_CREATED)
def create_merit_list(
    payload: MeritListCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.MERIT_LIST_MANAGE)),
):
    return get_service(db, current_user).create_merit_list(payload, current_user.user_id)


@router.post("/merit-lists/{merit_list_id}/publish", response_model=MeritListRead)
def publish_merit_list(
    merit_list_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.MERIT_LIST_MANAGE)),
):
    return get_service(db, current_user).publish_merit_list(merit_list_id)


@router.post("/applications/{application_id}/enroll", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def enroll_applicant(
    application_id: str,
    payload: EnrollApplicant,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.ADMISSION_ENROLL)),
):
    return get_service(db, current_user).enroll_applicant(application_id, payload, current_user.user_id)
