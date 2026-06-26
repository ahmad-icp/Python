from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import CurrentUser, Permission, require_permission
from app.db.session import get_db
from app.modules.academic import schemas as s
from app.modules.academic.service import AcademicService

router = APIRouter()

def svc(db: Session, user: CurrentUser) -> AcademicService:
    return AcademicService(db, user.college_id)

def list_response(items_total, limit, offset):
    items, total = items_total
    return {"items": items, "total": total, "limit": limit, "offset": offset}

@router.get("/institutions")
def list_institutions(search: str | None = None, limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_READ))):
    return list_response(svc(db, user).list_institutions(search, limit, offset), limit, offset)
@router.post("/institutions", response_model=s.InstitutionRead, status_code=status.HTTP_201_CREATED)
def create_institution(payload: s.InstitutionCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_WRITE))): return svc(db, user).create_institution(payload)

@router.get("/campuses")
def list_campuses(search: str | None = None, limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_READ))): return list_response(svc(db, user).list_campuses(search, limit, offset), limit, offset)
@router.post("/campuses", response_model=s.CampusRead, status_code=status.HTTP_201_CREATED)
def create_campus(payload: s.CampusCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_WRITE))): return svc(db, user).create_campus(payload)

@router.get("/departments")
def list_departments(search: str | None = None, limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_READ))): return list_response(svc(db, user).list_departments(search, limit, offset), limit, offset)
@router.post("/departments", response_model=s.DepartmentRead, status_code=status.HTTP_201_CREATED)
def create_department(payload: s.DepartmentCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_WRITE))): return svc(db, user).create_department(payload)

@router.get("/sessions")
def list_sessions(search: str | None = None, limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_READ))): return list_response(svc(db, user).list_sessions(search, limit, offset), limit, offset)
@router.post("/sessions", response_model=s.AcademicSessionRead, status_code=status.HTTP_201_CREATED)
def create_session(payload: s.AcademicSessionCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_WRITE))): return svc(db, user).create_session(payload)

@router.get("/programs")
def list_programs(search: str | None = None, limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_READ))): return list_response(svc(db, user).list_programs(search, limit, offset), limit, offset)
@router.post("/programs", response_model=s.ProgramRead, status_code=status.HTTP_201_CREATED)
def create_program(payload: s.ProgramCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_WRITE))): return svc(db, user).create_program(payload)

@router.get("/classes")
def list_classes(search: str | None = None, limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_READ))): return list_response(svc(db, user).list_classes(search, limit, offset), limit, offset)
@router.post("/classes", response_model=s.AcademicClassRead, status_code=status.HTTP_201_CREATED)
def create_class(payload: s.AcademicClassCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_WRITE))): return svc(db, user).create_class(payload)

@router.get("/sections")
def list_sections(search: str | None = None, limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_READ))): return list_response(svc(db, user).list_sections(search, limit, offset), limit, offset)
@router.post("/sections", response_model=s.SectionRead, status_code=status.HTTP_201_CREATED)
def create_section(payload: s.SectionCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_WRITE))): return svc(db, user).create_section(payload)

@router.get("/subjects")
def list_subjects(search: str | None = None, limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_READ))): return list_response(svc(db, user).list_subjects(search, limit, offset), limit, offset)
@router.post("/subjects", response_model=s.SubjectRead, status_code=status.HTTP_201_CREATED)
def create_subject(payload: s.SubjectCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_WRITE))): return svc(db, user).create_subject(payload)

@router.post("/subject-groups", response_model=s.SubjectGroupRead, status_code=status.HTTP_201_CREATED)
def create_subject_group(payload: s.SubjectGroupCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_WRITE))): return svc(db, user).create_subject_group(payload)
@router.post("/elective-groups", response_model=s.ElectiveGroupRead, status_code=status.HTTP_201_CREATED)
def create_elective_group(payload: s.ElectiveGroupCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_WRITE))): return svc(db, user).create_elective_group(payload)
@router.post("/subject-allocations", response_model=s.SubjectAllocationRead, status_code=status.HTTP_201_CREATED)
def create_subject_allocation(payload: s.SubjectAllocationCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_ASSIGN))): return svc(db, user).create_subject_allocation(payload)

@router.get("/teacher-assignments")
def list_teacher_assignments(search: str | None = None, limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_READ))): return list_response(svc(db, user).list_teacher_assignments(search, limit, offset), limit, offset)
@router.post("/teacher-assignments", response_model=s.TeacherAssignmentRead, status_code=status.HTTP_201_CREATED)
def create_teacher_assignment(payload: s.TeacherAssignmentCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_ASSIGN))): return svc(db, user).create_teacher_assignment(payload)
@router.get("/teacher-assignments/{teacher_id}/workload", response_model=s.TeacherWorkloadRead)
def teacher_workload(teacher_id: str, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_READ))): return svc(db, user).teacher_workload(teacher_id)

@router.post("/promotion-rules", response_model=s.PromotionRuleRead, status_code=status.HTTP_201_CREATED)
def create_promotion_rule(payload: s.PromotionRuleCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_WRITE))): return svc(db, user).create_promotion_rule(payload)
@router.post("/archives", response_model=s.AcademicArchiveRead, status_code=status.HTTP_201_CREATED)
def archive(payload: s.ArchiveRequest, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_DELETE))): return svc(db, user).archive(payload, user.user_id)
