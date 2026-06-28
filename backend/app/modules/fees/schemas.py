from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.modules.fees.models import ApprovalStatus, BillingFrequency, ChallanStatus, FeeHeadType, PaymentMethod, PaymentStatus, RefundStatus, ScholarshipType

class FeeHeadCreate(BaseModel):
    code: str = Field(min_length=2, max_length=40); name: str = Field(min_length=2, max_length=120); head_type: FeeHeadType; is_refundable: bool=False; is_active: bool=True
class FeeHeadRead(FeeHeadCreate):
    model_config=ConfigDict(from_attributes=True); id: str; college_id: str; created_at: datetime

class FeeTemplateLineCreate(BaseModel):
    fee_head_id: str; amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
class FeeTemplateCreate(BaseModel):
    code: str; name: str; version: int=Field(default=1, ge=1); program: str|None=None; class_name: str|None=None; section: str|None=None; frequency: BillingFrequency; effective_from: date; effective_to: date|None=None; lines: list[FeeTemplateLineCreate]=Field(min_length=1)
    @model_validator(mode='after')
    def dates_valid(self):
        if self.effective_to and self.effective_to < self.effective_from: raise ValueError('effective_to must be after effective_from')
        return self
class FeeTemplateLineRead(FeeTemplateLineCreate):
    model_config=ConfigDict(from_attributes=True); id: str
class FeeTemplateRead(FeeTemplateCreate):
    model_config=ConfigDict(from_attributes=True); id: str; college_id: str; is_active: bool; lines: list[FeeTemplateLineRead]

class ChallanLineCreate(BaseModel):
    fee_head_id: str; description: str; amount: Decimal=Field(gt=0)
class ManualChallanCreate(BaseModel):
    student_id: str; billing_period: str; issue_date: date; due_date: date; carry_forward: Decimal=Decimal('0'); late_fine: Decimal=Decimal('0'); discount_total: Decimal=Decimal('0'); notes: str|None=None; lines: list[ChallanLineCreate]=Field(min_length=1)
class GenerateChallanRequest(BaseModel):
    template_id: str; student_ids: list[str]=Field(min_length=1); billing_period: str; issue_date: date; due_date: date; carry_forward_balances: dict[str, Decimal] = {}
class ChallanLineRead(ChallanLineCreate):
    model_config=ConfigDict(from_attributes=True); id: str
class ChallanRead(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id: str; college_id: str; challan_number: str; student_id: str; billing_period: str; issue_date: date; due_date: date; status: ChallanStatus; subtotal: Decimal; discount_total: Decimal; late_fine: Decimal; carry_forward: Decimal; paid_amount: Decimal; total_amount: Decimal; balance_amount: Decimal; notes: str|None; created_at: datetime; lines: list[ChallanLineRead]
class ChallanList(BaseModel): items: list[ChallanRead]; total: int; limit: int; offset: int

class ScholarshipCreate(BaseModel):
    student_id: str; scholarship_type: ScholarshipType; title: str; percentage: Decimal|None=Field(default=None, ge=0, le=100); amount: Decimal|None=Field(default=None, ge=0); effective_from: date; effective_to: date|None=None; renewal_rule: str|None=None
    @model_validator(mode='after')
    def has_discount(self):
        if self.percentage is None and self.amount is None: raise ValueError('percentage or amount is required')
        return self
class ScholarshipRead(ScholarshipCreate):
    model_config=ConfigDict(from_attributes=True); id: str; college_id: str; status: ApprovalStatus; approved_by: str|None
class ApprovalUpdate(BaseModel): status: ApprovalStatus; remarks: str|None=None

class InstallmentPlanCreate(BaseModel): challan_id: str; student_id: str; number_of_installments: int=Field(ge=2, le=24); penalty_amount: Decimal=Field(default=Decimal('0'), ge=0)
class InstallmentPlanRead(InstallmentPlanCreate):
    model_config=ConfigDict(from_attributes=True); id: str; college_id: str; status: ApprovalStatus; approved_by: str|None

class PaymentCreate(BaseModel): challan_id: str; amount: Decimal=Field(gt=0); method: PaymentMethod; reference_number: str; paid_on: date
class PaymentRead(PaymentCreate):
    model_config=ConfigDict(from_attributes=True); id: str; college_id: str; status: PaymentStatus; received_by: str
class RefundCreate(BaseModel): payment_id: str; amount: Decimal=Field(gt=0); reason: str=Field(min_length=5)
class RefundRead(RefundCreate):
    model_config=ConfigDict(from_attributes=True); id: str; college_id: str; status: RefundStatus; requested_by: str; approved_by: str|None; created_at: datetime
class FinanceSummary(BaseModel): total_collections: Decimal; outstanding_dues: Decimal; overdue_challans: int; scholarships_approved: int
