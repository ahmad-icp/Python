from datetime import UTC, date, datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.academic.models import AcademicSession, Section
from app.modules.attendance import schemas as s
from app.modules.attendance.models import AttendanceRecord, AttendanceSession, AttendanceSessionStatus, AttendanceStatus
from app.modules.students.models import Student, StudentStatus
from app.modules.timetable.models import CalendarEvent, TimeSlot, TimetableEntry, WorkingDay


class AttendanceService:
    def __init__(self, db: Session, college_id: str) -> None:
        self.db = db
        self.college_id = college_id

    def _get(self, model, entity_id: str):
        entity = self.db.get(model, entity_id)
        if not entity or entity.college_id != self.college_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found")
        return entity

    def create_session(self, payload: s.AttendanceSessionCreate):
        academic_session = self._get(AcademicSession, payload.session_id)
        section = self._get(Section, payload.section_id)
        if section.academic_class.session_id != academic_session.id:
            raise HTTPException(status_code=409, detail="Section does not belong to this academic session")
        if not (academic_session.start_date <= payload.attendance_date <= academic_session.end_date):
            raise HTTPException(status_code=409, detail="Attendance date is outside the academic session")
        self._validate_working_date(payload.session_id, payload.attendance_date)
        if payload.time_slot_id:
            self._get(TimeSlot, payload.time_slot_id)
        if payload.timetable_entry_id:
            entry = self._get(TimetableEntry, payload.timetable_entry_id)
            if entry.section_id != payload.section_id or entry.session_id != payload.session_id:
                raise HTTPException(status_code=409, detail="Timetable entry does not match attendance section and session")
            if payload.time_slot_id and entry.time_slot_id != payload.time_slot_id:
                raise HTTPException(status_code=409, detail="Timetable entry does not match the selected time slot")
        item = AttendanceSession(college_id=self.college_id, **payload.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_sessions(self, section_id: str | None, start_date: date | None, end_date: date | None, limit: int, offset: int):
        query = select(AttendanceSession).where(AttendanceSession.college_id == self.college_id)
        if section_id:
            query = query.where(AttendanceSession.section_id == section_id)
        if start_date:
            query = query.where(AttendanceSession.attendance_date >= start_date)
        if end_date:
            query = query.where(AttendanceSession.attendance_date <= end_date)
        total = self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
        items = self.db.scalars(query.order_by(AttendanceSession.attendance_date.desc()).limit(limit).offset(offset)).unique().all()
        return list(items), total

    def mark_records(self, attendance_session_id: str, payload: s.BulkAttendanceMark, marked_by: str):
        attendance_session = self._get(AttendanceSession, attendance_session_id)
        if attendance_session.status == AttendanceSessionStatus.FINALIZED:
            raise HTTPException(status_code=409, detail="Finalized attendance cannot be changed")
        seen: set[str] = set()
        results = []
        for record_payload in payload.records:
            if record_payload.student_id in seen:
                raise HTTPException(status_code=409, detail="Duplicate student in attendance payload")
            seen.add(record_payload.student_id)
            student = self._get(Student, record_payload.student_id)
            if student.status != StudentStatus.ACTIVE:
                raise HTTPException(status_code=409, detail="Only active students can be marked for attendance")
            if student.current_section and student.current_section != self._get(Section, attendance_session.section_id).name:
                raise HTTPException(status_code=409, detail="Student does not belong to this attendance section")
            existing = self.db.scalar(select(AttendanceRecord).where(AttendanceRecord.attendance_session_id == attendance_session.id, AttendanceRecord.student_id == student.id))
            values = record_payload.model_dump()
            if existing:
                for key, value in values.items():
                    setattr(existing, key, value)
                existing.marked_by = marked_by
                existing.marked_at = datetime.now(UTC)
                results.append(existing)
            else:
                results.append(AttendanceRecord(college_id=self.college_id, attendance_session_id=attendance_session.id, section_id=attendance_session.section_id, attendance_date=attendance_session.attendance_date, marked_by=marked_by, **values))
                self.db.add(results[-1])
        self.db.commit()
        for record in results:
            self.db.refresh(record)
        return results

    def finalize_session(self, attendance_session_id: str, finalized_by: str):
        attendance_session = self._get(AttendanceSession, attendance_session_id)
        if not attendance_session.records:
            raise HTTPException(status_code=409, detail="Cannot finalize attendance without records")
        attendance_session.status = AttendanceSessionStatus.FINALIZED
        attendance_session.finalized_by = finalized_by
        attendance_session.finalized_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(attendance_session)
        return attendance_session

    def list_records(self, attendance_session_id: str | None, student_id: str | None, limit: int, offset: int):
        query = select(AttendanceRecord).where(AttendanceRecord.college_id == self.college_id)
        if attendance_session_id:
            query = query.where(AttendanceRecord.attendance_session_id == attendance_session_id)
        if student_id:
            query = query.where(AttendanceRecord.student_id == student_id)
        total = self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
        items = self.db.scalars(query.order_by(AttendanceRecord.attendance_date.desc()).limit(limit).offset(offset)).unique().all()
        return list(items), total

    def summary(self, section_id: str | None, student_id: str | None, start_date: date | None, end_date: date | None) -> s.AttendanceSummary:
        query = select(AttendanceRecord.status, func.count()).where(AttendanceRecord.college_id == self.college_id)
        if section_id:
            query = query.where(AttendanceRecord.section_id == section_id)
        if student_id:
            query = query.where(AttendanceRecord.student_id == student_id)
        if start_date:
            query = query.where(AttendanceRecord.attendance_date >= start_date)
        if end_date:
            query = query.where(AttendanceRecord.attendance_date <= end_date)
        counts = {status: count for status, count in self.db.execute(query.group_by(AttendanceRecord.status)).all()}
        present = counts.get(AttendanceStatus.PRESENT, 0) + counts.get(AttendanceStatus.LATE, 0) + counts.get(AttendanceStatus.EXCUSED, 0)
        total = sum(counts.values())
        return s.AttendanceSummary(total=total, present=counts.get(AttendanceStatus.PRESENT, 0), absent=counts.get(AttendanceStatus.ABSENT, 0), late=counts.get(AttendanceStatus.LATE, 0), excused=counts.get(AttendanceStatus.EXCUSED, 0), attendance_percentage=round((present / total) * 100, 2) if total else 0.0)

    def _validate_working_date(self, session_id: str, attendance_date: date) -> None:
        holiday = self.db.scalar(select(CalendarEvent).where(CalendarEvent.college_id == self.college_id, CalendarEvent.session_id == session_id, CalendarEvent.is_holiday.is_(True), CalendarEvent.start_date <= attendance_date, CalendarEvent.end_date >= attendance_date))
        if holiday:
            raise HTTPException(status_code=409, detail="Cannot create attendance on an academic holiday")
        working_day = self.db.scalar(select(WorkingDay).where(WorkingDay.college_id == self.college_id, WorkingDay.session_id == session_id, WorkingDay.weekday == attendance_date.isoweekday()))
        if working_day and not working_day.is_working:
            raise HTTPException(status_code=409, detail="Cannot create attendance on a non-working day")
