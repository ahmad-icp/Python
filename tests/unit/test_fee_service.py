from datetime import date
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.modules.fees.models import ChallanStatus, FeeHeadType, PaymentMethod, PaymentStatus
from app.modules.fees.schemas import FeeHeadCreate, ManualChallanCreate, ChallanLineCreate, PaymentCreate
from app.modules.fees.service import FeeService

def session():
    engine=create_engine('sqlite+pysqlite:///:memory:'); Base.metadata.create_all(engine); return sessionmaker(bind=engine, expire_on_commit=False)()

def test_manual_challan_and_partial_payment():
    db=session(); svc=FeeService(db,'college-a')
    head=svc.create_head(FeeHeadCreate(code='TUI', name='Tuition', head_type=FeeHeadType.TUITION))
    ch=svc.create_manual_challan(ManualChallanCreate(student_id='stu-1', billing_period='2026-07', issue_date=date(2026,7,1), due_date=date(2026,7,10), lines=[ChallanLineCreate(fee_head_id=head.id, description='Tuition July', amount=Decimal('1000'))]))
    assert ch.total_amount == Decimal('1000')
    pay=svc.record_payment(PaymentCreate(challan_id=ch.id, amount=Decimal('400'), method=PaymentMethod.CASH, reference_number='R-1', paid_on=date(2026,7,2)), 'cashier')
    assert pay.status == PaymentStatus.RECONCILED
    assert ch.status == ChallanStatus.PARTIALLY_PAID
    assert ch.balance_amount == Decimal('600')

def test_duplicate_payment_is_flagged_without_double_counting():
    db=session(); svc=FeeService(db,'college-a')
    head=svc.create_head(FeeHeadCreate(code='EXAM', name='Exam', head_type=FeeHeadType.EXAM))
    ch=svc.create_manual_challan(ManualChallanCreate(student_id='stu-1', billing_period='2026-FALL', issue_date=date(2026,8,1), due_date=date(2026,8,15), lines=[ChallanLineCreate(fee_head_id=head.id, description='Exam', amount=Decimal('500'))]))
    payload=PaymentCreate(challan_id=ch.id, amount=Decimal('500'), method=PaymentMethod.BANK_TRANSFER, reference_number='BANK-1', paid_on=date(2026,8,2))
    svc.record_payment(payload,'cashier'); dup=svc.record_payment(payload,'cashier')
    assert dup.status == PaymentStatus.DUPLICATE
    assert ch.paid_amount == Decimal('500')
