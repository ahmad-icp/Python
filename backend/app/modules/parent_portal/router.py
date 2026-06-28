from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.security import CurrentUser, Permission, require_permission
from app.db.session import get_db
from app.modules.parent_portal.schemas import ParentPortalDashboard
from app.modules.student_portal.service import StudentPortalService
from app.modules.students.models import Student, StudentGuardian

router = APIRouter()

@router.get('/dashboard', response_model=ParentPortalDashboard)
def parent_dashboard(child_id: str | None = Query(default=None), db: Session = Depends(get_db), current_user: CurrentUser = Depends(require_permission(Permission.PARENT_PORTAL_READ))):
    service = StudentPortalService(db, current_user.college_id)
    if child_id:
        if current_user.role == 'parent':
            linked = db.scalar(select(Student.id).join(StudentGuardian).where(Student.college_id == current_user.college_id, Student.id == child_id, StudentGuardian.email == current_user.user_id))
            if not linked:
                raise HTTPException(status.HTTP_403_FORBIDDEN, 'Child is not linked to this parent account')
        children = [service.dashboard(child_id)]
    else:
        student_ids = db.scalars(select(Student.id).join(StudentGuardian).where(Student.college_id == current_user.college_id, StudentGuardian.email == current_user.user_id).limit(10)).all()
        children = [service.dashboard(student_id) for student_id in student_ids]
    return ParentPortalDashboard(children=children, teacher_communication=[])
