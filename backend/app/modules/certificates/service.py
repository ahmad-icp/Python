from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.certificates.models import (
    CertificateRequest,
    CertificateStatus,
    CertificateTemplate,
    DocumentApprovalStatus,
    DocumentRepositoryItem,
    verification_code_for,
)
from app.modules.certificates.schemas import (
    CertificateApprovalUpdate,
    CertificateRequestCreate,
    CertificateTemplateCreate,
    DocumentApprovalUpdate,
    DocumentCreate,
)


class CertificateService:
    def __init__(self, db: Session, college_id: str) -> None:
        self.db = db
        self.college_id = college_id

    def create_template(self, payload: CertificateTemplateCreate) -> CertificateTemplate:
        template = CertificateTemplate(college_id=self.college_id, **payload.model_dump())
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def list_templates(self) -> list[CertificateTemplate]:
        return list(
            self.db.scalars(
                select(CertificateTemplate)
                .where(CertificateTemplate.college_id == self.college_id)
                .order_by(CertificateTemplate.certificate_type, CertificateTemplate.name)
            ).all()
        )

    def request_certificate(self, payload: CertificateRequestCreate, requested_by: str) -> CertificateRequest:
        template = None
        rendered_html = None
        if payload.template_id:
            template = self.db.get(CertificateTemplate, payload.template_id)
            if not template or template.college_id != self.college_id or not template.is_active:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Certificate template not found")
            if template.certificate_type != payload.certificate_type:
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Template type does not match certificate type")
            rendered_html = self._render(template.body_template, payload.context)
        request = CertificateRequest(
            college_id=self.college_id,
            template_id=template.id if template else None,
            certificate_type=payload.certificate_type,
            student_id=payload.student_id,
            employee_id=payload.employee_id,
            purpose=payload.purpose,
            requested_by=requested_by,
            verification_code="pending",
            rendered_html=rendered_html,
        )
        self.db.add(request)
        self.db.flush()
        request.verification_code = verification_code_for(self.college_id, request.id)
        request.qr_payload = f"/api/v1/certificates/verify/{request.verification_code}"
        self.db.commit()
        self.db.refresh(request)
        return request

    def list_requests(self, status_filter: CertificateStatus | None, limit: int, offset: int) -> tuple[list[CertificateRequest], int]:
        query = select(CertificateRequest).where(CertificateRequest.college_id == self.college_id)
        if status_filter:
            query = query.where(CertificateRequest.status == status_filter)
        total = self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
        items = self.db.scalars(query.order_by(CertificateRequest.created_at.desc()).limit(limit).offset(offset)).all()
        return list(items), total

    def approve(self, request_id: str, payload: CertificateApprovalUpdate, actor_id: str) -> CertificateRequest:
        request = self._get_request(request_id)
        if request.status not in {CertificateStatus.PENDING_APPROVAL, CertificateStatus.DRAFT}:
            raise HTTPException(status.HTTP_409_CONFLICT, "Only pending certificates can be approved or rejected")
        request.status = payload.status
        request.approved_by = actor_id if payload.status == CertificateStatus.APPROVED else None
        request.approved_at = datetime.now(UTC) if payload.status == CertificateStatus.APPROVED else None
        request.rejection_reason = payload.rejection_reason if payload.status == CertificateStatus.REJECTED else None
        self.db.commit()
        self.db.refresh(request)
        return request

    def issue(self, request_id: str, actor_id: str) -> CertificateRequest:
        request = self._get_request(request_id)
        if request.status != CertificateStatus.APPROVED:
            raise HTTPException(status.HTTP_409_CONFLICT, "Only approved certificates can be issued")
        request.status = CertificateStatus.ISSUED
        request.issued_by = actor_id
        request.issued_at = datetime.now(UTC)
        if not request.rendered_html:
            request.rendered_html = self._default_certificate_html(request)
        self.db.commit()
        self.db.refresh(request)
        return request

    def verify(self, verification_code: str):
        certificate = self.db.scalar(
            select(CertificateRequest).where(
                CertificateRequest.college_id == self.college_id,
                CertificateRequest.verification_code == verification_code,
                CertificateRequest.status == CertificateStatus.ISSUED,
            )
        )
        return certificate

    def upload_document(self, payload: DocumentCreate, uploaded_by: str) -> DocumentRepositoryItem:
        document = DocumentRepositoryItem(college_id=self.college_id, uploaded_by=uploaded_by, **payload.model_dump())
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def list_documents(self, owner_type: str | None, owner_id: str | None) -> list[DocumentRepositoryItem]:
        query = select(DocumentRepositoryItem).where(DocumentRepositoryItem.college_id == self.college_id)
        if owner_type:
            query = query.where(DocumentRepositoryItem.owner_type == owner_type)
        if owner_id:
            query = query.where(DocumentRepositoryItem.owner_id == owner_id)
        return list(self.db.scalars(query.order_by(DocumentRepositoryItem.created_at.desc()).limit(100)).all())

    def approve_document(self, document_id: str, payload: DocumentApprovalUpdate, actor_id: str) -> DocumentRepositoryItem:
        document = self.db.get(DocumentRepositoryItem, document_id)
        if not document or document.college_id != self.college_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
        document.approval_status = payload.status
        document.approved_by = actor_id if payload.status == DocumentApprovalStatus.APPROVED else None
        document.approved_at = datetime.now(UTC) if payload.status == DocumentApprovalStatus.APPROVED else None
        document.rejection_reason = payload.rejection_reason if payload.status == DocumentApprovalStatus.REJECTED else None
        self.db.commit()
        self.db.refresh(document)
        return document

    def _get_request(self, request_id: str) -> CertificateRequest:
        request = self.db.get(CertificateRequest, request_id)
        if not request or request.college_id != self.college_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Certificate request not found")
        return request

    def _render(self, template: str, context: dict[str, str]) -> str:
        rendered = template
        for key, value in context.items():
            rendered = rendered.replace("{{" + key + "}}", value)
        return rendered

    def _default_certificate_html(self, request: CertificateRequest) -> str:
        owner = request.student_id or request.employee_id or "record"
        return f"<h1>{request.certificate_type.value.title()} Certificate</h1><p>Issued for {owner}.</p><p>Verification: {request.verification_code}</p>"
