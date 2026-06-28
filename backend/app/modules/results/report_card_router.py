from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.security import CurrentUser, Permission, require_permission
from app.db.session import get_db
from app.modules.results import report_card_schemas as s
from app.modules.results.report_card_service import ReportCardService
router = APIRouter()
def service(db: Session, user: CurrentUser) -> ReportCardService: return ReportCardService(db, user.college_id)
def page(items_total, limit: int, offset: int):
    items, total = items_total; return {"items": items, "total": total, "limit": limit, "offset": offset}
@router.post("/generate", response_model=s.ReportCardRead, status_code=status.HTTP_201_CREATED)
def generate(payload: s.ReportCardGenerateRequest, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.REPORT_CARD_WRITE))): return service(db, user).generate(payload, user.user_id)
@router.get("/")
def list_cards(student_id: str | None = None, exam_id: str | None = None, limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.REPORT_CARD_READ))): return page(service(db, user).list_cards(student_id, exam_id, limit, offset), limit, offset)
@router.post("/{card_id}/issue", response_model=s.ReportCardRead)
def issue(card_id: str, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.REPORT_CARD_ISSUE))): return service(db, user).issue(card_id, user.user_id)
@router.get("/verify/{code}", response_model=s.ReportCardRead)
def verify(code: str, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.REPORT_CARD_READ))): return service(db, user).verify(code)
