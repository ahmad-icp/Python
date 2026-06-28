import uuid
from datetime import datetime
from enum import StrEnum
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

def new_uuid() -> str: return str(uuid.uuid4())
class MeritScope(StrEnum):
    INSTITUTION="institution"; PROGRAM="program"; CLASS="class"; SECTION="section"; SESSION="session"
class MeritBasis(StrEnum):
    PERCENTAGE="percentage"; GPA="gpa"
class MeritStatus(StrEnum):
    DRAFT="draft"; PUBLISHED="published"; LOCKED="locked"
class TieBreaker(StrEnum):
    DOB_OLDER="dob_older"; DOB_YOUNGER="dob_younger"; ADMISSION_NUMBER="admission_number"; NAME="name"
class MeritList(Base):
    __tablename__="merit_lists"
    __table_args__=(UniqueConstraint("college_id","exam_id","scope_type","scope_id","basis",name="uq_merit_list_scope_basis"), Index("ix_merit_lists_college_exam_status","college_id","exam_id","status"), Index("ix_merit_lists_college_scope","college_id","scope_type","scope_id"))
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=new_uuid)
    college_id: Mapped[str]=mapped_column(String(64),nullable=False,index=True)
    exam_id: Mapped[str]=mapped_column(ForeignKey("exams.id",ondelete="CASCADE"),nullable=False,index=True)
    scope_type: Mapped[MeritScope]=mapped_column(Enum(MeritScope),nullable=False)
    scope_id: Mapped[str]=mapped_column(String(64),default="",nullable=False)
    basis: Mapped[MeritBasis]=mapped_column(Enum(MeritBasis),nullable=False)
    status: Mapped[MeritStatus]=mapped_column(Enum(MeritStatus),default=MeritStatus.DRAFT,nullable=False)
    title: Mapped[str]=mapped_column(String(180),nullable=False)
    tie_breakers: Mapped[str]=mapped_column(Text,nullable=False)
    analytics_json: Mapped[str]=mapped_column(Text,nullable=False,default="{}")
    generated_by: Mapped[str]=mapped_column(String(64),nullable=False)
    published_by: Mapped[str|None]=mapped_column(String(64))
    generated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    published_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
    items: Mapped[list["MeritListItem"]]=relationship(back_populates="merit_list",cascade="all, delete-orphan",lazy="selectin")
class MeritListItem(Base):
    __tablename__="merit_list_items"
    __table_args__=(UniqueConstraint("merit_list_id","student_id",name="uq_merit_item_student"), Index("ix_merit_items_list_rank","merit_list_id","rank"),)
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=new_uuid)
    college_id: Mapped[str]=mapped_column(String(64),nullable=False,index=True)
    merit_list_id: Mapped[str]=mapped_column(ForeignKey("merit_lists.id",ondelete="CASCADE"),nullable=False,index=True)
    result_id: Mapped[str]=mapped_column(ForeignKey("student_results.id",ondelete="CASCADE"),nullable=False,index=True)
    grade_calculation_id: Mapped[str|None]=mapped_column(ForeignKey("student_grade_calculations.id",ondelete="SET NULL"),index=True)
    student_id: Mapped[str]=mapped_column(ForeignKey("students.id",ondelete="CASCADE"),nullable=False,index=True)
    rank: Mapped[int]=mapped_column(Integer,nullable=False)
    score: Mapped[float]=mapped_column(Numeric(7,3),nullable=False)
    percentage: Mapped[float]=mapped_column(Numeric(5,2),nullable=False)
    gpa: Mapped[float|None]=mapped_column(Numeric(4,2))
    tie_breaker_value: Mapped[str|None]=mapped_column(String(180))
    is_certificate_issued: Mapped[bool]=mapped_column(Boolean,default=False,nullable=False)
    merit_list: Mapped[MeritList]=relationship(back_populates="items")
class MeritCertificate(Base):
    __tablename__="merit_certificates"
    __table_args__=(UniqueConstraint("college_id","merit_item_id",name="uq_merit_certificate_item"), UniqueConstraint("college_id","verification_code",name="uq_merit_certificate_code"),)
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=new_uuid)
    college_id: Mapped[str]=mapped_column(String(64),nullable=False,index=True)
    merit_item_id: Mapped[str]=mapped_column(ForeignKey("merit_list_items.id",ondelete="CASCADE"),nullable=False,index=True)
    verification_code: Mapped[str]=mapped_column(String(80),nullable=False)
    printable_html: Mapped[str]=mapped_column(Text,nullable=False)
    issued_by: Mapped[str]=mapped_column(String(64),nullable=False)
    issued_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
