from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import CurrentUser, Permission, get_current_user, require_permission
from app.db.session import get_db
from app.modules.certificates.models import CertificateStatus
from app.modules.certificates.schemas import (
    CertificateApprovalUpdate,
    CertificateList,
    CertificateRead,
    CertificateRequestCreate,
    CertificateTemplateCreate,
    CertificateTemplateRead,
    DocumentApprovalUpdate,
    DocumentCreate,
    DocumentRead,
    VerificationResponse,
)
from app.modules.certificates.service import CertificateService

router = APIRouter()


def service(db: Session, current_user: CurrentUser) -> CertificateService:
    return CertificateService(db=db, college_id=current_user.college_id)


@router.post("/templates", response_model=CertificateTemplateRead, status_code=status.HTTP_201_CREATED)
def create_template(
    payload: CertificateTemplateCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.CERTIFICATE_MANAGE)),
):
    return service(db, current_user).create_template(payload)


@router.get("/templates", response_model=list[CertificateTemplateRead])
def list_templates(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.CERTIFICATE_READ)),
):
    return service(db, current_user).list_templates()


@router.post("/requests", response_model=CertificateRead, status_code=status.HTTP_201_CREATED)
def request_certificate(
    payload: CertificateRequestCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.CERTIFICATE_WRITE)),
):
    return service(db, current_user).request_certificate(payload, current_user.user_id)


@router.get("/requests", response_model=CertificateList)
def list_requests(
    status_filter: CertificateStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.CERTIFICATE_READ)),
):
    items, total = service(db, current_user).list_requests(status_filter, limit, offset)
    return CertificateList(items=items, total=total, limit=limit, offset=offset)


@router.post("/requests/{request_id}/approval", response_model=CertificateRead)
def approve_certificate(
    request_id: str,
    payload: CertificateApprovalUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.CERTIFICATE_APPROVE)),
):
    return service(db, current_user).approve(request_id, payload, current_user.user_id)


@router.post("/requests/{request_id}/issue", response_model=CertificateRead)
def issue_certificate(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.CERTIFICATE_ISSUE)),
):
    return service(db, current_user).issue(request_id, current_user.user_id)


@router.get("/verify/{verification_code}", response_model=VerificationResponse)
def verify_certificate(
    verification_code: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    certificate = service(db, current_user).verify(verification_code)
    return VerificationResponse(valid=certificate is not None, certificate=certificate)


@router.post("/documents", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
def upload_document(
    payload: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.DOCUMENT_WRITE)),
):
    return service(db, current_user).upload_document(payload, current_user.user_id)


@router.get("/documents", response_model=list[DocumentRead])
def list_documents(
    owner_type: str | None = None,
    owner_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.DOCUMENT_READ)),
):
    return service(db, current_user).list_documents(owner_type, owner_id)


@router.post("/documents/{document_id}/approval", response_model=DocumentRead)
def approve_document(
    document_id: str,
    payload: DocumentApprovalUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.DOCUMENT_APPROVE)),
):
    return service(db, current_user).approve_document(document_id, payload, current_user.user_id)
