from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.security import CurrentUser, Permission, require_permission
from app.db.session import get_db
from app.modules.results import schemas as s
from app.modules.results.models import ResultStatus
from app.modules.results.service import ResultService

router = APIRouter()

def service(db: Session, user: CurrentUser) -> ResultService:
    return ResultService(db, user.college_id)

def page(items_total, limit: int, offset: int):
    items, total = items_total
    return {"items": items, "total": total, "limit": limit, "offset": offset}

@router.post("/policies", response_model=s.GradingPolicyRead, status_code=status.HTTP_201_CREATED)
def create_policy(payload: s.GradingPolicyCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.RESULT_CONFIGURE))):
    return service(db, user).create_policy(payload)

@router.get("/policies")
def list_policies(active_only: bool = True, limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.RESULT_READ))):
    return page(service(db, user).list_policies(active_only, limit, offset), limit, offset)

@router.post("/calculate", response_model=list[s.StudentResultRead])
def calculate(payload: s.CalculateRequest, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.RESULT_CALCULATE))):
    return service(db, user).calculate(payload, user.user_id)

@router.get("/results")
def list_results(exam_id: str | None = None, student_id: str | None = None, status_filter: ResultStatus | None = None, limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.RESULT_READ))):
    return page(service(db, user).list_results(exam_id, student_id, status_filter, limit, offset), limit, offset)

@router.post("/results/{result_id}/publish", response_model=s.StudentResultRead)
def publish(result_id: str, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.RESULT_PUBLISH))):
    return service(db, user).transition(result_id, "publish", user.user_id)

@router.post("/results/{result_id}/lock", response_model=s.StudentResultRead)
def lock(result_id: str, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.RESULT_LOCK))):
    return service(db, user).transition(result_id, "lock", user.user_id)
