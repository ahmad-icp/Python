from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import CurrentUser, Permission, require_permission
from app.db.session import get_db
from app.modules.attendance import schemas as s
from app.modules.attendance.service import AttendanceService

router = APIRouter()


def service(db: Session, user: CurrentUser) -> AttendanceService:
    return AttendanceService(db=db, college_id=user.college_id)


def page(items_total, limit: int, offset: int):
    items, total = items_total
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/sessions")
def list_sessions(section_id: str | None = None, start_date: date | None = None, end_date: date | None = None, limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ATTENDANCE_READ))):
    return page(service(db, user).list_sessions(section_id, start_date, end_date, limit, offset), limit, offset)


@router.post("/sessions", response_model=s.AttendanceSessionRead, status_code=status.HTTP_201_CREATED)
def create_session(payload: s.AttendanceSessionCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ATTENDANCE_WRITE))):
    return service(db, user).create_session(payload)


@router.post("/sessions/{attendance_session_id}/records", response_model=list[s.AttendanceRecordRead])
def mark_records(attendance_session_id: str, payload: s.BulkAttendanceMark, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ATTENDANCE_MARK))):
    return service(db, user).mark_records(attendance_session_id, payload, user.user_id)


@router.post("/sessions/{attendance_session_id}/finalize", response_model=s.AttendanceSessionRead)
def finalize_session(attendance_session_id: str, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ATTENDANCE_FINALIZE))):
    return service(db, user).finalize_session(attendance_session_id, user.user_id)


@router.get("/records")
def list_records(attendance_session_id: str | None = None, student_id: str | None = None, limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ATTENDANCE_READ))):
    return page(service(db, user).list_records(attendance_session_id, student_id, limit, offset), limit, offset)


@router.get("/summary", response_model=s.AttendanceSummary)
def summary(section_id: str | None = None, student_id: str | None = None, start_date: date | None = None, end_date: date | None = None, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ATTENDANCE_READ))):
    return service(db, user).summary(section_id, student_id, start_date, end_date)
