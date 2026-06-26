from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import CurrentUser, Permission, require_permission
from app.db.session import get_db
from app.modules.marks_entry import schemas as s
from app.modules.marks_entry.models import MarksBatchStatus
from app.modules.marks_entry.service import MarksEntryService

router = APIRouter()


def service(db: Session, user: CurrentUser) -> MarksEntryService:
    return MarksEntryService(db=db, college_id=user.college_id)


def page(items_total, limit: int, offset: int):
    items, total = items_total
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/batches")
def list_batches(exam_id: str | None = None, section_id: str | None = None, status_filter: MarksBatchStatus | None = None, limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.MARKS_READ))):
    return page(service(db, user).list_batches(exam_id, section_id, status_filter, limit, offset), limit, offset)


@router.post("/batches", response_model=s.MarksBatchRead, status_code=status.HTTP_201_CREATED)
def create_batch(payload: s.MarksBatchCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.MARKS_WRITE))):
    return service(db, user).create_batch(payload, user.user_id)


@router.post("/batches/{batch_id}/entries", response_model=list[s.MarksEntryRead])
def bulk_upsert(batch_id: str, payload: s.BulkMarksUpsert, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.MARKS_WRITE))):
    return service(db, user).bulk_upsert(batch_id, payload, user.user_id)


@router.post("/batches/{batch_id}/entries/single", response_model=s.MarksEntryRead)
def upsert_single(batch_id: str, payload: s.MarksEntryUpsert, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.MARKS_WRITE))):
    return service(db, user).upsert_entry(batch_id, payload, user.user_id)


@router.post("/batches/{batch_id}/import", response_model=list[s.MarksEntryRead])
def import_marks(batch_id: str, payload: s.MarksImportRequest, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.MARKS_WRITE))):
    return service(db, user).import_marks(batch_id, payload, user.user_id)


@router.post("/batches/{batch_id}/submit", response_model=s.MarksBatchRead)
def submit_batch(batch_id: str, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.MARKS_SUBMIT))):
    return service(db, user).submit_batch(batch_id, user.user_id)


@router.post("/batches/{batch_id}/lock", response_model=s.MarksBatchRead)
def lock_batch(batch_id: str, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.MARKS_LOCK))):
    return service(db, user).lock_batch(batch_id, user.user_id)


@router.post("/batches/{batch_id}/unlock", response_model=s.MarksBatchRead)
def unlock_batch(batch_id: str, payload: s.UnlockRequest, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.MARKS_LOCK))):
    return service(db, user).unlock_batch(batch_id, payload, user.user_id)


@router.get("/entries")
def list_entries(batch_id: str | None = None, student_id: str | None = None, limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.MARKS_READ))):
    return page(service(db, user).list_entries(batch_id, student_id, limit, offset), limit, offset)


@router.get("/batches/{batch_id}/audit")
def list_audit(batch_id: str, limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.MARKS_READ))):
    return page(service(db, user).list_audit(batch_id, limit, offset), limit, offset)
