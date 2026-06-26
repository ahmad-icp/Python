from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import CurrentUser, Permission, require_permission
from app.db.session import get_db
from app.modules.examination import schemas as s
from app.modules.examination.models import ExamStatus
from app.modules.examination.service import ExaminationService

router = APIRouter()


def service(db: Session, user: CurrentUser) -> ExaminationService:
    return ExaminationService(db=db, college_id=user.college_id)


def page(items_total, limit: int, offset: int):
    items, total = items_total
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/types")
def list_exam_types(search: str | None = None, limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.EXAM_READ))):
    return page(service(db, user).list_exam_types(search, limit, offset), limit, offset)


@router.post("/types", response_model=s.ExamTypeRead, status_code=status.HTTP_201_CREATED)
def create_exam_type(payload: s.ExamTypeCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.EXAM_CONFIGURE))):
    return service(db, user).create_exam_type(payload)


@router.get("/exams")
def list_exams(session_id: str | None = None, section_id: str | None = None, status_filter: ExamStatus | None = None, limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.EXAM_READ))):
    return page(service(db, user).list_exams(session_id, section_id, status_filter, limit, offset), limit, offset)


@router.post("/exams", response_model=s.ExamRead, status_code=status.HTTP_201_CREATED)
def create_exam(payload: s.ExamCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.EXAM_WRITE))):
    return service(db, user).create_exam(payload, user.user_id)


@router.post("/exams/{exam_id}/publish", response_model=s.ExamRead)
def publish_exam(exam_id: str, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.EXAM_PUBLISH))):
    return service(db, user).publish_exam(exam_id)


@router.post("/exams/{exam_id}/lock", response_model=s.ExamRead)
def lock_exam(exam_id: str, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.EXAM_LOCK))):
    return service(db, user).lock_exam(exam_id)


@router.get("/components")
def list_components(exam_id: str | None = None, subject_id: str | None = None, limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.EXAM_READ))):
    return page(service(db, user).list_components(exam_id, subject_id, limit, offset), limit, offset)


@router.post("/components", response_model=s.AssessmentComponentRead, status_code=status.HTTP_201_CREATED)
def add_component(payload: s.AssessmentComponentCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.EXAM_CONFIGURE))):
    return service(db, user).add_component(payload)


@router.get("/halls")
def list_halls(search: str | None = None, limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.EXAM_READ))):
    return page(service(db, user).list_halls(search, limit, offset), limit, offset)


@router.post("/halls", response_model=s.ExamHallRead, status_code=status.HTTP_201_CREATED)
def create_hall(payload: s.ExamHallCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.EXAM_CONFIGURE))):
    return service(db, user).create_hall(payload)


@router.get("/schedules")
def list_schedules(exam_id: str | None = None, exam_date: date | None = None, limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.EXAM_READ))):
    return page(service(db, user).list_schedules(exam_id, exam_date, limit, offset), limit, offset)


@router.post("/schedules", response_model=s.ExamScheduleRead, status_code=status.HTTP_201_CREATED)
def schedule_exam(payload: s.ExamScheduleCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.EXAM_SCHEDULE))):
    return service(db, user).schedule_exam(payload)


@router.get("/invigilators")
def list_invigilators(schedule_id: str | None = None, teacher_id: str | None = None, limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.EXAM_READ))):
    return page(service(db, user).list_invigilators(schedule_id, teacher_id, limit, offset), limit, offset)


@router.post("/invigilators", response_model=s.InvigilatorAssignmentRead, status_code=status.HTTP_201_CREATED)
def assign_invigilator(payload: s.InvigilatorAssignmentCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.EXAM_SCHEDULE))):
    return service(db, user).assign_invigilator(payload, user.user_id)
