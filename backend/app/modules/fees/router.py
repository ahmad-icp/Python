from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.security import CurrentUser, Permission, require_permission
from app.db.session import get_db
from app.modules.fees.models import ChallanStatus
from app.modules.fees.schemas import *
from app.modules.fees.service import FeeService

router=APIRouter()
def svc(db:Session,u:CurrentUser): return FeeService(db,u.college_id)

@router.get('/heads', response_model=list[FeeHeadRead])
def list_heads(db:Session=Depends(get_db), u:CurrentUser=Depends(require_permission(Permission.FEE_READ))): return svc(db,u).list_heads()
@router.post('/heads', response_model=FeeHeadRead, status_code=status.HTTP_201_CREATED)
def create_head(payload:FeeHeadCreate, db:Session=Depends(get_db), u:CurrentUser=Depends(require_permission(Permission.FEE_MANAGE))): return svc(db,u).create_head(payload)
@router.post('/templates', response_model=FeeTemplateRead, status_code=status.HTTP_201_CREATED)
def create_template(payload:FeeTemplateCreate, db:Session=Depends(get_db), u:CurrentUser=Depends(require_permission(Permission.FEE_MANAGE))): return svc(db,u).create_template(payload)
@router.post('/challans/manual', response_model=ChallanRead, status_code=status.HTTP_201_CREATED)
def manual_challan(payload:ManualChallanCreate, db:Session=Depends(get_db), u:CurrentUser=Depends(require_permission(Permission.FEE_WRITE))): return svc(db,u).create_manual_challan(payload)
@router.post('/challans/generate', response_model=list[ChallanRead], status_code=status.HTTP_201_CREATED)
def generate_challans(payload:GenerateChallanRequest, db:Session=Depends(get_db), u:CurrentUser=Depends(require_permission(Permission.FEE_WRITE))): return svc(db,u).generate_challans(payload)
@router.get('/challans', response_model=ChallanList)
def list_challans(student_id:str|None=None, status_filter:ChallanStatus|None=Query(default=None, alias='status'), limit:int=Query(25,ge=1,le=100), offset:int=Query(0,ge=0), db:Session=Depends(get_db), u:CurrentUser=Depends(require_permission(Permission.FEE_READ))):
    items,total=svc(db,u).list_challans(student_id,status_filter,limit,offset); return ChallanList(items=items,total=total,limit=limit,offset=offset)
@router.post('/payments', response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def record_payment(payload:PaymentCreate, db:Session=Depends(get_db), u:CurrentUser=Depends(require_permission(Permission.FEE_COLLECT))): return svc(db,u).record_payment(payload,u.user_id)
@router.post('/scholarships', response_model=ScholarshipRead, status_code=status.HTTP_201_CREATED)
def create_scholarship(payload:ScholarshipCreate, db:Session=Depends(get_db), u:CurrentUser=Depends(require_permission(Permission.FEE_WRITE))): return svc(db,u).create_scholarship(payload)
@router.post('/scholarships/{scholarship_id}/approval', response_model=ScholarshipRead)
def approve_scholarship(scholarship_id:str, payload:ApprovalUpdate, db:Session=Depends(get_db), u:CurrentUser=Depends(require_permission(Permission.FEE_MANAGE))): return svc(db,u).approve_scholarship(scholarship_id,payload,u.user_id)
@router.post('/installments', response_model=InstallmentPlanRead, status_code=status.HTTP_201_CREATED)
def create_installment(payload:InstallmentPlanCreate, db:Session=Depends(get_db), u:CurrentUser=Depends(require_permission(Permission.FEE_MANAGE))): return svc(db,u).create_installment_plan(payload)
@router.post('/refunds', response_model=RefundRead, status_code=status.HTTP_201_CREATED)
def request_refund(payload:RefundCreate, db:Session=Depends(get_db), u:CurrentUser=Depends(require_permission(Permission.FEE_REFUND))): return svc(db,u).request_refund(payload,u.user_id)
@router.get('/reports/summary', response_model=FinanceSummary)
def reports_summary(db:Session=Depends(get_db), u:CurrentUser=Depends(require_permission(Permission.FEE_READ))): return svc(db,u).summary()
