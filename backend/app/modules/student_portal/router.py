from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import CurrentUser, Permission, require_permission
from app.db.session import get_db
from app.modules.student_portal.schemas import StudentPortalDashboard
from app.modules.student_portal.service import StudentPortalService

router = APIRouter()

@router.get('/students/{student_id}/dashboard', response_model=StudentPortalDashboard)
def student_dashboard(student_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(require_permission(Permission.STUDENT_PORTAL_READ))):
    return StudentPortalService(db, current_user.college_id).dashboard(student_id)
