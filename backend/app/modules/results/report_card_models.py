import uuid
from datetime import datetime
from enum import StrEnum
from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

def new_uuid() -> str: return str(uuid.uuid4())

class ReportCardStatus(StrEnum):
    DRAFT = "draft"
    ISSUED = "issued"
    REVOKED = "revoked"

class ReportCard(Base):
    __tablename__ = "report_cards"
    __table_args__ = (
        UniqueConstraint("college_id", "result_id", name="uq_report_card_result"),
        UniqueConstraint("college_id", "verification_code", name="uq_report_card_verification"),
        Index("ix_report_cards_college_student", "college_id", "student_id", "issued_at"),
        Index("ix_report_cards_college_exam", "college_id", "exam_id", "status"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    result_id: Mapped[str] = mapped_column(ForeignKey("student_results.id", ondelete="CASCADE"), nullable=False, index=True)
    grade_calculation_id: Mapped[str | None] = mapped_column(ForeignKey("student_grade_calculations.id", ondelete="SET NULL"), index=True)
    exam_id: Mapped[str] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[ReportCardStatus] = mapped_column(Enum(ReportCardStatus), default=ReportCardStatus.DRAFT, nullable=False)
    verification_code: Mapped[str] = mapped_column(String(80), nullable=False)
    institution_name: Mapped[str] = mapped_column(String(180), nullable=False)
    branding_json: Mapped[str | None] = mapped_column(Text)
    remarks: Mapped[str | None] = mapped_column(Text)
    qr_payload: Mapped[str] = mapped_column(Text, nullable=False)
    printable_html: Mapped[str] = mapped_column(Text, nullable=False)
    pdf_file_path: Mapped[str | None] = mapped_column(String(500))
    generated_by: Mapped[str] = mapped_column(String(64), nullable=False)
    issued_by: Mapped[str | None] = mapped_column(String(64))
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    issued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
