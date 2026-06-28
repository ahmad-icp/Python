from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.security import CurrentUser, Permission, require_permission
from app.db.session import get_db
from app.modules.results import transcript_schemas as s
from app.modules.results.transcript_service import TranscriptService
router=APIRouter()
def service(db:Session,user:CurrentUser): return TranscriptService(db,user.college_id)
def page(x,limit,offset): items,total=x; return {"items":items,"total":total,"limit":limit,"offset":offset}
@router.post('/generate',response_model=s.TranscriptRead,status_code=status.HTTP_201_CREATED)
def generate(payload:s.TranscriptGenerateRequest,db:Session=Depends(get_db),user:CurrentUser=Depends(require_permission(Permission.TRANSCRIPT_WRITE))): return service(db,user).generate(payload,user.user_id)
@router.get('/')
def list_transcripts(student_id:str|None=None,limit:int=Query(50,ge=1,le=500),offset:int=Query(0,ge=0),db:Session=Depends(get_db),user:CurrentUser=Depends(require_permission(Permission.TRANSCRIPT_READ))): return page(service(db,user).list(student_id,limit,offset),limit,offset)
@router.post('/{transcript_id}/issue',response_model=s.TranscriptRead)
def issue(transcript_id:str,db:Session=Depends(get_db),user:CurrentUser=Depends(require_permission(Permission.TRANSCRIPT_ISSUE))): return service(db,user).issue(transcript_id,user.user_id)
@router.get('/verify/{code}',response_model=s.TranscriptRead)
def verify(code:str,db:Session=Depends(get_db),user:CurrentUser=Depends(require_permission(Permission.TRANSCRIPT_READ))): return service(db,user).verify(code)
