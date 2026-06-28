import uuid
from datetime import datetime
from enum import StrEnum
from sqlalchemy import DateTime, Enum, Index, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

def new_uuid() -> str: return str(uuid.uuid4())
class TranscriptStatus(StrEnum): DRAFT="draft"; ISSUED="issued"; REVOKED="revoked"
class Transcript(Base):
    __tablename__="transcripts"
    __table_args__=(UniqueConstraint("college_id","student_id","verification_code",name="uq_transcript_verification"), Index("ix_transcripts_college_student_status","college_id","student_id","status"),)
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=new_uuid)
    college_id: Mapped[str]=mapped_column(String(64),nullable=False,index=True)
    student_id: Mapped[str]=mapped_column(String(36),nullable=False,index=True)
    status: Mapped[TranscriptStatus]=mapped_column(Enum(TranscriptStatus),default=TranscriptStatus.DRAFT,nullable=False)
    verification_code: Mapped[str]=mapped_column(String(80),nullable=False)
    institution_name: Mapped[str]=mapped_column(String(180),nullable=False)
    academic_history_json: Mapped[str]=mapped_column(Text,nullable=False)
    summary_json: Mapped[str]=mapped_column(Text,nullable=False)
    printable_html: Mapped[str]=mapped_column(Text,nullable=False)
    generated_by: Mapped[str]=mapped_column(String(64),nullable=False)
    issued_by: Mapped[str|None]=mapped_column(String(64))
    generated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    issued_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
