import uuid
from datetime import datetime
from enum import StrEnum
from sqlalchemy import DateTime, Enum, Index, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

def new_uuid() -> str: return str(uuid.uuid4())
class GazetteScope(StrEnum):
    CLASS = "class"; SECTION = "section"; PROGRAM = "program"; OVERALL = "overall"
class GazetteStatus(StrEnum):
    GENERATED = "generated"; PUBLISHED = "published"
class Gazette(Base):
    __tablename__ = "gazettes"
    __table_args__ = (UniqueConstraint("college_id", "exam_id", "scope_type", "scope_id", name="uq_gazette_scope"), Index("ix_gazettes_college_exam", "college_id", "exam_id", "scope_type"))
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    college_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    exam_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    scope_type: Mapped[GazetteScope] = mapped_column(Enum(GazetteScope), nullable=False)
    scope_id: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    status: Mapped[GazetteStatus] = mapped_column(Enum(GazetteStatus), default=GazetteStatus.GENERATED, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    summary_json: Mapped[str] = mapped_column(Text, nullable=False)
    rows_json: Mapped[str] = mapped_column(Text, nullable=False)
    generated_by: Mapped[str] = mapped_column(String(64), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
