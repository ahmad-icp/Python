from datetime import date
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.modules.fees.models import *
from app.modules.fees.schemas import *

class FeeService:
    def __init__(self, db: Session, college_id: str): self.db=db; self.college_id=college_id
    def _challan_no(self): return f"CH-{date.today():%Y%m%d}-{(self.db.scalar(select(func.count()).select_from(FeeChallan).where(FeeChallan.college_id==self.college_id)) or 0)+1:05d}"
    def create_head(self,p):
        obj=FeeHead(college_id=self.college_id, **p.model_dump()); self.db.add(obj); self.db.commit(); self.db.refresh(obj); return obj
    def list_heads(self): return list(self.db.scalars(select(FeeHead).where(FeeHead.college_id==self.college_id).order_by(FeeHead.name)).all())
    def create_template(self,p):
        ids=[l.fee_head_id for l in p.lines]; count=self.db.scalar(select(func.count()).select_from(FeeHead).where(FeeHead.college_id==self.college_id, FeeHead.id.in_(ids))) or 0
        if count != len(set(ids)): raise HTTPException(400,'One or more fee heads are invalid for this college')
        obj=FeeTemplate(college_id=self.college_id, **p.model_dump(exclude={'lines'})); obj.lines=[FeeTemplateLine(**l.model_dump()) for l in p.lines]
        self.db.add(obj); self.db.commit(); self.db.refresh(obj); return obj
    def create_manual_challan(self,p):
        subtotal=sum((l.amount for l in p.lines), Decimal('0')); total=subtotal + p.carry_forward + p.late_fine - p.discount_total
        if total < 0: raise HTTPException(400,'Challan total cannot be negative')
        ch=FeeChallan(college_id=self.college_id, challan_number=self._challan_no(), subtotal=subtotal,total_amount=total,balance_amount=total, **p.model_dump(exclude={'lines'})); ch.lines=[FeeChallanLine(**l.model_dump()) for l in p.lines]
        self.db.add(ch); self.db.commit(); self.db.refresh(ch); return ch
    def generate_challans(self,p):
        tmpl=self.db.get(FeeTemplate,p.template_id)
        if not tmpl or tmpl.college_id != self.college_id or not tmpl.is_active: raise HTTPException(404,'Fee template not found')
        out=[]
        for sid in p.student_ids:
            lines=[ChallanLineCreate(fee_head_id=l.fee_head_id, description=l.fee_head.name, amount=l.amount) for l in tmpl.lines]
            out.append(self.create_manual_challan(ManualChallanCreate(student_id=sid,billing_period=p.billing_period,issue_date=p.issue_date,due_date=p.due_date,carry_forward=p.carry_forward_balances.get(sid,Decimal('0')),lines=lines)))
        return out
    def list_challans(self, student_id, status_filter, limit, offset):
        q=select(FeeChallan).where(FeeChallan.college_id==self.college_id)
        if student_id: q=q.where(FeeChallan.student_id==student_id)
        if status_filter: q=q.where(FeeChallan.status==status_filter)
        total=self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
        return list(self.db.scalars(q.order_by(FeeChallan.due_date.desc()).limit(limit).offset(offset)).unique().all()), total
    def record_payment(self,p, user_id):
        ch=self.db.get(FeeChallan,p.challan_id)
        if not ch or ch.college_id != self.college_id: raise HTTPException(404,'Challan not found')
        dup=self.db.scalar(select(FeePayment).where(FeePayment.college_id==self.college_id, FeePayment.reference_number==p.reference_number))
        pay=FeePayment(college_id=self.college_id, received_by=user_id, status=PaymentStatus.DUPLICATE if dup else PaymentStatus.RECONCILED, **p.model_dump())
        if not dup:
            ch.paid_amount += p.amount; ch.balance_amount=max(Decimal('0'), ch.total_amount-ch.paid_amount); ch.status=ChallanStatus.PAID if ch.balance_amount==0 else ChallanStatus.PARTIALLY_PAID
        self.db.add(pay); self.db.commit(); self.db.refresh(pay); return pay
    def create_scholarship(self,p): obj=Scholarship(college_id=self.college_id, **p.model_dump()); self.db.add(obj); self.db.commit(); self.db.refresh(obj); return obj
    def approve_scholarship(self,id,p,user):
        obj=self.db.get(Scholarship,id)
        if not obj or obj.college_id!=self.college_id: raise HTTPException(404,'Scholarship not found')
        obj.status=p.status; obj.approved_by=user if p.status==ApprovalStatus.APPROVED else None; self.db.commit(); self.db.refresh(obj); return obj
    def create_installment_plan(self,p): obj=InstallmentPlan(college_id=self.college_id, **p.model_dump()); self.db.add(obj); self.db.commit(); self.db.refresh(obj); return obj
    def request_refund(self,p,user): obj=FeeRefund(college_id=self.college_id, requested_by=user, **p.model_dump()); self.db.add(obj); self.db.commit(); self.db.refresh(obj); return obj
    def summary(self):
        col=self.db.scalar(select(func.coalesce(func.sum(FeePayment.amount),0)).where(FeePayment.college_id==self.college_id, FeePayment.status==PaymentStatus.RECONCILED)) or 0
        out=self.db.scalar(select(func.coalesce(func.sum(FeeChallan.balance_amount),0)).where(FeeChallan.college_id==self.college_id, FeeChallan.status!=ChallanStatus.CANCELLED)) or 0
        overdue=self.db.scalar(select(func.count()).select_from(FeeChallan).where(FeeChallan.college_id==self.college_id, FeeChallan.due_date<date.today(), FeeChallan.balance_amount>0)) or 0
        sch=self.db.scalar(select(func.count()).select_from(Scholarship).where(Scholarship.college_id==self.college_id, Scholarship.status==ApprovalStatus.APPROVED)) or 0
        return FinanceSummary(total_collections=col,outstanding_dues=out,overdue_challans=overdue,scholarships_approved=sch)
