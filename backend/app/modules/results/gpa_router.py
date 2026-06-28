from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.security import CurrentUser, Permission, require_permission
from app.db.session import get_db
from app.modules.results import gpa_schemas as s
from app.modules.results.gpa_service import GradeCalculationService

router = APIRouter()

def service(db: Session, user: CurrentUser) -> GradeCalculationService:
    return GradeCalculationService(db, user.college_id)

def page(items_total, limit: int, offset: int):
    items, total = items_total
    return {"items": items, "total": total, "limit": limit, "offset": offset}

@router.post("/systems", response_model=s.GradeSystemRead, status_code=status.HTTP_201_CREATED)
def create_system(payload: s.GradeSystemCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.GRADE_CONFIGURE))):
    return service(db, user).create_system(payload)

@router.get("/systems")
def list_systems(scope_type: str | None = None, active_only: bool = True, limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.GRADE_READ))):
    return page(service(db, user).list_systems(scope_type, active_only, limit, offset), limit, offset)

@router.post("/calculations", response_model=list[s.StudentGradeCalculationRead])
def calculate(payload: s.GradeCalculationRequest, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.GRADE_CALCULATE))):
    return service(db, user).calculate(payload, user.user_id)

@router.get("/calculations")
def list_calculations(student_id: str | None = None, exam_id: str | None = None, limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.GRADE_READ))):
    return page(service(db, user).list_calculations(student_id, exam_id, limit, offset), limit, offset)
