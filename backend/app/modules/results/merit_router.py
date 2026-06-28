from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.security import CurrentUser, Permission, require_permission
from app.db.session import get_db
from app.modules.results import merit_schemas as s
from app.modules.results.merit_models import MeritScope
from app.modules.results.merit_service import MeritService
router=APIRouter()
def service(db:Session,user:CurrentUser): return MeritService(db,user.college_id)
def page(x,limit,offset): items,total=x; return {"items":items,"total":total,"limit":limit,"offset":offset}
@router.post('/generate',response_model=s.MeritListRead,status_code=status.HTTP_201_CREATED)
def generate(payload:s.MeritListGenerateRequest,db:Session=Depends(get_db),user:CurrentUser=Depends(require_permission(Permission.MERIT_WRITE))): return service(db,user).generate(payload,user.user_id)
@router.get('/')
def list_merit(exam_id:str|None=None,scope_type:MeritScope|None=None,limit:int=Query(50,ge=1,le=500),offset:int=Query(0,ge=0),db:Session=Depends(get_db),user:CurrentUser=Depends(require_permission(Permission.MERIT_READ))): return page(service(db,user).list(exam_id,scope_type,limit,offset),limit,offset)
@router.post('/{merit_id}/publish',response_model=s.MeritListRead)
def publish(merit_id:str,db:Session=Depends(get_db),user:CurrentUser=Depends(require_permission(Permission.MERIT_PUBLISH))): return service(db,user).publish(merit_id,user.user_id)
@router.post('/{merit_id}/lock',response_model=s.MeritListRead)
def lock(merit_id:str,db:Session=Depends(get_db),user:CurrentUser=Depends(require_permission(Permission.MERIT_PUBLISH))): return service(db,user).lock(merit_id,user.user_id)
@router.post('/items/{item_id}/certificate',response_model=s.MeritCertificateRead)
def certificate(item_id:str,db:Session=Depends(get_db),user:CurrentUser=Depends(require_permission(Permission.MERIT_PUBLISH))): return service(db,user).issue_certificate(item_id,user.user_id)
