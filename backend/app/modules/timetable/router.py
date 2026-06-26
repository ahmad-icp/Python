from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import CurrentUser, Permission, require_permission
from app.db.session import get_db
from app.modules.timetable import schemas as s
from app.modules.timetable.service import TimetableService

router = APIRouter()


def service(db: Session, user: CurrentUser) -> TimetableService:
    return TimetableService(db=db, college_id=user.college_id)


def page(items_total, limit: int, offset: int):
    items, total = items_total
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/classrooms")
def list_classrooms(search: str | None = None, limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.TIMETABLE_READ))):
    return page(service(db, user).list_classrooms(search, limit, offset), limit, offset)


@router.post("/classrooms", response_model=s.ClassroomRead, status_code=status.HTTP_201_CREATED)
def create_classroom(payload: s.ClassroomCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.TIMETABLE_WRITE))):
    return service(db, user).create_classroom(payload)


@router.get("/time-slots")
def list_time_slots(search: str | None = None, limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.TIMETABLE_READ))):
    return page(service(db, user).list_time_slots(search, limit, offset), limit, offset)


@router.post("/time-slots", response_model=s.TimeSlotRead, status_code=status.HTTP_201_CREATED)
def create_time_slot(payload: s.TimeSlotCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.TIMETABLE_WRITE))):
    return service(db, user).create_time_slot(payload)


@router.post("/working-days", response_model=s.WorkingDayRead, status_code=status.HTTP_201_CREATED)
def set_working_day(payload: s.WorkingDayCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.TIMETABLE_WRITE))):
    return service(db, user).set_working_day(payload)


@router.get("/calendar-events")
def list_calendar_events(search: str | None = None, limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.TIMETABLE_READ))):
    return page(service(db, user).list_calendar_events(search, limit, offset), limit, offset)


@router.post("/calendar-events", response_model=s.CalendarEventRead, status_code=status.HTTP_201_CREATED)
def create_calendar_event(payload: s.CalendarEventCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.TIMETABLE_WRITE))):
    return service(db, user).create_calendar_event(payload)


@router.get("/versions")
def list_versions(limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.TIMETABLE_READ))):
    return page(service(db, user).list_versions(None, limit, offset), limit, offset)


@router.post("/versions", response_model=s.TimetableVersionRead, status_code=status.HTTP_201_CREATED)
def create_version(payload: s.TimetableVersionCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.TIMETABLE_WRITE))):
    return service(db, user).create_version(payload, user.user_id)


@router.post("/versions/{version_id}/publish", response_model=s.TimetableVersionRead)
def publish_version(version_id: str, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.TIMETABLE_PUBLISH))):
    return service(db, user).publish_version(version_id)


@router.get("/entries")
def list_entries(section_id: str | None = None, teacher_id: str | None = None, classroom_id: str | None = None, limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.TIMETABLE_READ))):
    return page(service(db, user).list_entries(section_id, teacher_id, classroom_id, limit, offset), limit, offset)


@router.post("/entries", response_model=s.TimetableEntryRead, status_code=status.HTTP_201_CREATED)
def add_entry(payload: s.TimetableEntryCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.TIMETABLE_WRITE))):
    return service(db, user).add_entry(payload)


@router.post("/auto-generate", response_model=list[s.TimetableEntryRead])
def auto_generate(payload: s.AutoGenerateRequest, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.TIMETABLE_WRITE))):
    return service(db, user).auto_generate(payload)
