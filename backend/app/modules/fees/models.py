import uuid
from datetime import date, datetime
from enum import StrEnum
from decimal import Decimal
from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def new_uuid() -> str: return str(uuid.uuid4())

class FeeHeadType(StrEnum):
    TUITION='tuition'; ADMISSION='admission'; EXAM='exam'; LAB='lab'; LIBRARY='library'; TRANSPORT='transport'; HOSTEL='hostel'; MISCELLANEOUS='miscellaneous'
class BillingFrequency(StrEnum): MONTHLY='monthly'; QUARTERLY='quarterly'; SEMESTER='semester'; YEARLY='yearly'
class ChallanStatus(StrEnum): DRAFT='draft'; ISSUED='issued'; PARTIALLY_PAID='partially_paid'; PAID='paid'; OVERDUE='overdue'; CANCELLED='cancelled'
class PaymentMethod(StrEnum): CASH='cash'; CHEQUE='cheque'; BANK_TRANSFER='bank_transfer'; JAZZCASH='jazzcash'; EASYPAISA='easypaisa'; RAAST='raast'
class PaymentStatus(StrEnum): PENDING='pending'; RECONCILED='reconciled'; FAILED='failed'; DUPLICATE='duplicate'
class ApprovalStatus(StrEnum): PENDING='pending'; APPROVED='approved'; REJECTED='rejected'
class ScholarshipType(StrEnum): MERIT='merit'; NEED_BASED='need_based'; STAFF='staff'; SIBLING='sibling'; DISCOUNT='discount'
class RefundStatus(StrEnum): REQUESTED='requested'; APPROVED='approved'; REJECTED='rejected'; PAID='paid'

class FeeHead(Base):
    __tablename__='fee_heads'; __table_args__=(UniqueConstraint('college_id','code',name='uq_fee_head_code_college'), Index('ix_fee_heads_college_type','college_id','head_type'))
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str]=mapped_column(String(64), nullable=False, index=True)
    code: Mapped[str]=mapped_column(String(40), nullable=False)
    name: Mapped[str]=mapped_column(String(120), nullable=False)
    head_type: Mapped[FeeHeadType]=mapped_column(Enum(FeeHeadType), nullable=False)
    is_refundable: Mapped[bool]=mapped_column(default=False, nullable=False)
    is_active: Mapped[bool]=mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class FeeTemplate(Base):
    __tablename__='fee_templates'; __table_args__=(UniqueConstraint('college_id','code','version',name='uq_fee_template_version'), Index('ix_fee_templates_scope','college_id','program','class_name','section'))
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str]=mapped_column(String(64), nullable=False, index=True)
    code: Mapped[str]=mapped_column(String(50), nullable=False)
    name: Mapped[str]=mapped_column(String(160), nullable=False)
    version: Mapped[int]=mapped_column(default=1, nullable=False)
    program: Mapped[str|None]=mapped_column(String(120))
    class_name: Mapped[str|None]=mapped_column(String(80))
    section: Mapped[str|None]=mapped_column(String(80))
    frequency: Mapped[BillingFrequency]=mapped_column(Enum(BillingFrequency), nullable=False)
    effective_from: Mapped[date]=mapped_column(Date, nullable=False)
    effective_to: Mapped[date|None]=mapped_column(Date)
    is_active: Mapped[bool]=mapped_column(default=True, nullable=False)
    lines: Mapped[list['FeeTemplateLine']]=relationship(back_populates='template', cascade='all, delete-orphan', lazy='selectin')

class FeeTemplateLine(Base):
    __tablename__='fee_template_lines'; __table_args__=(UniqueConstraint('template_id','fee_head_id',name='uq_template_fee_head'),)
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=new_uuid)
    template_id: Mapped[str]=mapped_column(ForeignKey('fee_templates.id', ondelete='CASCADE'), nullable=False, index=True)
    fee_head_id: Mapped[str]=mapped_column(ForeignKey('fee_heads.id'), nullable=False, index=True)
    amount: Mapped[Decimal]=mapped_column(Numeric(12,2), nullable=False)
    template: Mapped[FeeTemplate]=relationship(back_populates='lines')
    fee_head: Mapped[FeeHead]=relationship(lazy='selectin')

class FeeChallan(Base):
    __tablename__='fee_challans'; __table_args__=(UniqueConstraint('college_id','challan_number',name='uq_challan_number_college'), Index('ix_challans_student_status_due','college_id','student_id','status','due_date'))
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str]=mapped_column(String(64), nullable=False, index=True)
    challan_number: Mapped[str]=mapped_column(String(60), nullable=False)
    student_id: Mapped[str]=mapped_column(String(36), nullable=False, index=True)
    billing_period: Mapped[str]=mapped_column(String(30), nullable=False)
    issue_date: Mapped[date]=mapped_column(Date, nullable=False)
    due_date: Mapped[date]=mapped_column(Date, nullable=False)
    status: Mapped[ChallanStatus]=mapped_column(Enum(ChallanStatus), default=ChallanStatus.ISSUED, nullable=False)
    subtotal: Mapped[Decimal]=mapped_column(Numeric(12,2), default=0, nullable=False)
    discount_total: Mapped[Decimal]=mapped_column(Numeric(12,2), default=0, nullable=False)
    late_fine: Mapped[Decimal]=mapped_column(Numeric(12,2), default=0, nullable=False)
    carry_forward: Mapped[Decimal]=mapped_column(Numeric(12,2), default=0, nullable=False)
    paid_amount: Mapped[Decimal]=mapped_column(Numeric(12,2), default=0, nullable=False)
    total_amount: Mapped[Decimal]=mapped_column(Numeric(12,2), default=0, nullable=False)
    balance_amount: Mapped[Decimal]=mapped_column(Numeric(12,2), default=0, nullable=False)
    notes: Mapped[str|None]=mapped_column(Text)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    lines: Mapped[list['FeeChallanLine']]=relationship(back_populates='challan', cascade='all, delete-orphan', lazy='selectin')
    payments: Mapped[list['FeePayment']]=relationship(back_populates='challan', cascade='all, delete-orphan', lazy='selectin')

class FeeChallanLine(Base):
    __tablename__='fee_challan_lines'
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=new_uuid)
    challan_id: Mapped[str]=mapped_column(ForeignKey('fee_challans.id', ondelete='CASCADE'), nullable=False, index=True)
    fee_head_id: Mapped[str]=mapped_column(ForeignKey('fee_heads.id'), nullable=False)
    description: Mapped[str]=mapped_column(String(200), nullable=False)
    amount: Mapped[Decimal]=mapped_column(Numeric(12,2), nullable=False)
    challan: Mapped[FeeChallan]=relationship(back_populates='lines')
    fee_head: Mapped[FeeHead]=relationship(lazy='selectin')

class Scholarship(Base):
    __tablename__='scholarships'; __table_args__=(Index('ix_scholarships_college_student_status','college_id','student_id','status'),)
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str]=mapped_column(String(64), nullable=False, index=True)
    student_id: Mapped[str]=mapped_column(String(36), nullable=False, index=True)
    scholarship_type: Mapped[ScholarshipType]=mapped_column(Enum(ScholarshipType), nullable=False)
    title: Mapped[str]=mapped_column(String(160), nullable=False)
    percentage: Mapped[Decimal|None]=mapped_column(Numeric(5,2))
    amount: Mapped[Decimal|None]=mapped_column(Numeric(12,2))
    effective_from: Mapped[date]=mapped_column(Date, nullable=False)
    effective_to: Mapped[date|None]=mapped_column(Date)
    renewal_rule: Mapped[str|None]=mapped_column(String(200))
    status: Mapped[ApprovalStatus]=mapped_column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False)
    approved_by: Mapped[str|None]=mapped_column(String(64))

class InstallmentPlan(Base):
    __tablename__='installment_plans'
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str]=mapped_column(String(64), nullable=False, index=True)
    challan_id: Mapped[str]=mapped_column(ForeignKey('fee_challans.id', ondelete='CASCADE'), nullable=False, index=True)
    student_id: Mapped[str]=mapped_column(String(36), nullable=False, index=True)
    number_of_installments: Mapped[int]=mapped_column(nullable=False)
    penalty_amount: Mapped[Decimal]=mapped_column(Numeric(12,2), default=0, nullable=False)
    status: Mapped[ApprovalStatus]=mapped_column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False)
    approved_by: Mapped[str|None]=mapped_column(String(64))

class FeePayment(Base):
    __tablename__='fee_payments'; __table_args__=(Index('ix_payments_college_reference','college_id','reference_number'), Index('ix_payments_college_method_status','college_id','method','status'))
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str]=mapped_column(String(64), nullable=False, index=True)
    challan_id: Mapped[str]=mapped_column(ForeignKey('fee_challans.id', ondelete='CASCADE'), nullable=False, index=True)
    amount: Mapped[Decimal]=mapped_column(Numeric(12,2), nullable=False)
    method: Mapped[PaymentMethod]=mapped_column(Enum(PaymentMethod), nullable=False)
    reference_number: Mapped[str]=mapped_column(String(120), nullable=False)
    paid_on: Mapped[date]=mapped_column(Date, nullable=False)
    status: Mapped[PaymentStatus]=mapped_column(Enum(PaymentStatus), default=PaymentStatus.RECONCILED, nullable=False)
    received_by: Mapped[str]=mapped_column(String(64), nullable=False)
    challan: Mapped[FeeChallan]=relationship(back_populates='payments')

class FeeRefund(Base):
    __tablename__='fee_refunds'
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str]=mapped_column(String(64), nullable=False, index=True)
    payment_id: Mapped[str]=mapped_column(ForeignKey('fee_payments.id'), nullable=False, index=True)
    amount: Mapped[Decimal]=mapped_column(Numeric(12,2), nullable=False)
    reason: Mapped[str]=mapped_column(Text, nullable=False)
    status: Mapped[RefundStatus]=mapped_column(Enum(RefundStatus), default=RefundStatus.REQUESTED, nullable=False)
    requested_by: Mapped[str]=mapped_column(String(64), nullable=False)
    approved_by: Mapped[str|None]=mapped_column(String(64))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
