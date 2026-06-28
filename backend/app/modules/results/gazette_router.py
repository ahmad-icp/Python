from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.security import CurrentUser, Permission, require_permission
from app.db.session import get_db
from app.modules.results import gazette_schemas as s
from app.modules.results.gazette_service import GazetteService
router=APIRouter()
def service(db:Session,user:CurrentUser): return GazetteService(db,user.college_id)
def page(x,limit,offset): items,total=x; return {"items":items,"total":total,"limit":limit,"offset":offset}
@router.post('/generate',response_model=s.GazetteRead,status_code=status.HTTP_201_CREATED)
def generate(payload:s.GazetteGenerateRequest,db:Session=Depends(get_db),user:CurrentUser=Depends(require_permission(Permission.GAZETTE_WRITE))): return service(db,user).generate(payload,user.user_id)
@router.get('/')
def list_gazettes(exam_id:str|None=None,limit:int=Query(50,ge=1,le=500),offset:int=Query(0,ge=0),db:Session=Depends(get_db),user:CurrentUser=Depends(require_permission(Permission.GAZETTE_READ))): return page(service(db,user).list(exam_id,limit,offset),limit,offset)
