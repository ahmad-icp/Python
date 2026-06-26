from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.modules.academic.models import AcademicSession, Section, Subject, SubjectAllocation, TeacherAssignment, AssignmentStatus
from app.modules.timetable.models import CalendarEvent, Classroom, TimeSlot, TimetableEntry, TimetableStatus, TimetableVersion, WorkingDay
from app.modules.timetable import schemas as s


class TimetableService:
    def __init__(self, db: Session, college_id: str) -> None:
        self.db = db
        self.college_id = college_id

    def _get(self, model, entity_id: str):
        entity = self.db.get(model, entity_id)
        if not entity or entity.college_id != self.college_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found")
        return entity

    def _list(self, model, search: str | None, limit: int, offset: int, *columns):
        query = select(model).where(model.college_id == self.college_id)
        if search and columns:
            term = f"%{search.strip()}%"
            query = query.where(or_(*[column.ilike(term) for column in columns]))
        total = self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
        return list(self.db.scalars(query.limit(limit).offset(offset)).unique().all()), total

    def create_classroom(self, payload: s.ClassroomCreate):
        item = Classroom(college_id=self.college_id, **payload.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_classrooms(self, search: str | None, limit: int, offset: int):
        return self._list(Classroom, search, limit, offset, Classroom.name, Classroom.code)

    def create_time_slot(self, payload: s.TimeSlotCreate):
        item = TimeSlot(college_id=self.college_id, **payload.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_time_slots(self, search: str | None, limit: int, offset: int):
        return self._list(TimeSlot, search, limit, offset, TimeSlot.name)

    def set_working_day(self, payload: s.WorkingDayCreate):
        self._get(AcademicSession, payload.session_id)
        existing = self.db.scalar(select(WorkingDay).where(WorkingDay.college_id == self.college_id, WorkingDay.session_id == payload.session_id, WorkingDay.weekday == int(payload.weekday)))
        if existing:
            existing.is_working = payload.is_working
            self.db.commit()
            self.db.refresh(existing)
            return existing
        item = WorkingDay(college_id=self.college_id, session_id=payload.session_id, weekday=int(payload.weekday), is_working=payload.is_working)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def create_calendar_event(self, payload: s.CalendarEventCreate):
        self._get(AcademicSession, payload.session_id)
        item = CalendarEvent(college_id=self.college_id, **payload.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_calendar_events(self, search: str | None, limit: int, offset: int):
        return self._list(CalendarEvent, search, limit, offset, CalendarEvent.title)

    def create_version(self, payload: s.TimetableVersionCreate, created_by: str):
        self._get(AcademicSession, payload.session_id)
        section = self._get(Section, payload.section_id)
        academic_class = section.academic_class
        if academic_class.session_id != payload.session_id:
            raise HTTPException(status_code=409, detail="Section does not belong to this academic session")
        version_number = (self.db.scalar(select(func.max(TimetableVersion.version_number)).where(TimetableVersion.college_id == self.college_id, TimetableVersion.section_id == payload.section_id)) or 0) + 1
        item = TimetableVersion(college_id=self.college_id, version_number=version_number, created_by=created_by, **payload.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_versions(self, search: str | None, limit: int, offset: int):
        return self._list(TimetableVersion, None, limit, offset)

    def add_entry(self, payload: s.TimetableEntryCreate):
        version = self._get(TimetableVersion, payload.version_id)
        if version.status != TimetableStatus.DRAFT:
            raise HTTPException(status_code=409, detail="Only draft timetables can be edited")
        subject = self._get(Subject, payload.subject_id)
        classroom = self._get(Classroom, payload.classroom_id)
        time_slot = self._get(TimeSlot, payload.time_slot_id)
        if time_slot.is_break:
            raise HTTPException(status_code=409, detail="Cannot schedule a lecture in a break slot")
        section = self._get(Section, version.section_id)
        if section.enrolled_count > classroom.capacity:
            raise HTTPException(status_code=409, detail="Room capacity is lower than section enrollment")
        self._validate_working_day(version.session_id, int(payload.weekday))
        self._validate_subject_allocated(version.section_id, subject.id)
        self._validate_teacher_assigned(version.section_id, subject.id, payload.teacher_id, int(payload.weekday), payload.time_slot_id)
        self._validate_no_holiday(version, int(payload.weekday))
        self._validate_no_clashes(version, payload)
        item = TimetableEntry(college_id=self.college_id, session_id=version.session_id, section_id=version.section_id, weekday=int(payload.weekday), **payload.model_dump(exclude={"weekday"}))
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def publish_version(self, version_id: str):
        version = self._get(TimetableVersion, version_id)
        if not version.entries:
            raise HTTPException(status_code=409, detail="Cannot publish an empty timetable")
        active = list(self.db.scalars(select(TimetableVersion).where(TimetableVersion.college_id == self.college_id, TimetableVersion.section_id == version.section_id, TimetableVersion.status == TimetableStatus.PUBLISHED)).all())
        for current in active:
            current.status = TimetableStatus.ARCHIVED
        version.status = TimetableStatus.PUBLISHED
        version.published_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(version)
        return version

    def list_entries(self, section_id: str | None, teacher_id: str | None, classroom_id: str | None, limit: int, offset: int):
        query = select(TimetableEntry).where(TimetableEntry.college_id == self.college_id)
        if section_id:
            query = query.where(TimetableEntry.section_id == section_id)
        if teacher_id:
            query = query.where(TimetableEntry.teacher_id == teacher_id)
        if classroom_id:
            query = query.where(TimetableEntry.classroom_id == classroom_id)
        total = self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
        items = self.db.scalars(query.order_by(TimetableEntry.weekday, TimetableEntry.time_slot_id).limit(limit).offset(offset)).unique().all()
        return list(items), total

    def auto_generate(self, payload: s.AutoGenerateRequest):
        version = self._get(TimetableVersion, payload.version_id)
        section = self._get(Section, version.section_id)
        allocations = list(self.db.scalars(select(SubjectAllocation).where(SubjectAllocation.class_id == section.class_id, SubjectAllocation.college_id == self.college_id)).all())
        slots = [slot for slot in self.db.scalars(select(TimeSlot).where(TimeSlot.college_id == self.college_id, TimeSlot.is_break.is_(False)).order_by(TimeSlot.sort_order)).all()]
        days = [day.weekday for day in self.db.scalars(select(WorkingDay).where(WorkingDay.college_id == self.college_id, WorkingDay.session_id == version.session_id, WorkingDay.is_working.is_(True)).order_by(WorkingDay.weekday)).all()]
        if not allocations or not slots or not days:
            raise HTTPException(status_code=409, detail="Subject allocations, working days, and time slots are required for auto generation")
        created = []
        slot_index = 0
        for allocation in allocations:
            for _ in range(allocation.weekly_periods):
                for _attempt in range(len(days) * len(slots)):
                    day = days[(slot_index // len(slots)) % len(days)]
                    slot = slots[slot_index % len(slots)]
                    slot_index += 1
                    try:
                        created.append(self.add_entry(s.TimetableEntryCreate(version_id=version.id, subject_id=allocation.subject_id, teacher_id=payload.teacher_id, teacher_name=payload.teacher_name, classroom_id=payload.classroom_id, time_slot_id=slot.id, weekday=day)))
                        break
                    except HTTPException as exc:
                        if exc.status_code not in {409, 404}:
                            raise
        return created

    def _validate_working_day(self, session_id: str, weekday: int) -> None:
        working_day = self.db.scalar(select(WorkingDay).where(WorkingDay.college_id == self.college_id, WorkingDay.session_id == session_id, WorkingDay.weekday == weekday))
        if working_day and not working_day.is_working:
            raise HTTPException(status_code=409, detail="Selected day is not a working day")

    def _validate_no_holiday(self, version: TimetableVersion, weekday: int) -> None:
        current = version.effective_from
        while current <= version.effective_to:
            if current.isoweekday() == weekday:
                holiday = self.db.scalar(select(CalendarEvent).where(CalendarEvent.college_id == self.college_id, CalendarEvent.session_id == version.session_id, CalendarEvent.is_holiday.is_(True), CalendarEvent.start_date <= current, CalendarEvent.end_date >= current))
                if holiday:
                    raise HTTPException(status_code=409, detail="Timetable entry conflicts with an academic holiday")
            current += timedelta(days=1)

    def _validate_subject_allocated(self, section_id: str, subject_id: str) -> None:
        section = self._get(Section, section_id)
        allocation = self.db.scalar(select(SubjectAllocation).where(SubjectAllocation.college_id == self.college_id, SubjectAllocation.class_id == section.class_id, SubjectAllocation.subject_id == subject_id))
        if not allocation:
            raise HTTPException(status_code=409, detail="Subject is not allocated to this section's class")

    def _validate_teacher_assigned(self, section_id: str, subject_id: str, teacher_id: str, weekday: int, time_slot_id: str) -> None:
        assignment = self.db.scalar(select(TeacherAssignment).where(TeacherAssignment.college_id == self.college_id, TeacherAssignment.section_id == section_id, TeacherAssignment.subject_id == subject_id, TeacherAssignment.teacher_id == teacher_id, TeacherAssignment.status == AssignmentStatus.ACTIVE))
        if not assignment:
            raise HTTPException(status_code=409, detail="Teacher is not assigned to this section and subject")
        scheduled = self.db.scalar(select(func.count()).select_from(TimetableEntry).where(TimetableEntry.college_id == self.college_id, TimetableEntry.teacher_id == teacher_id)) or 0
        if scheduled + 1 > assignment.max_weekly_periods:
            raise HTTPException(status_code=409, detail="Teacher timetable exceeds weekly workload")

    def _validate_no_clashes(self, version: TimetableVersion, payload: s.TimetableEntryCreate) -> None:
        conditions = [
            (TimetableEntry.version_id == version.id, "Duplicate section slot in this timetable"),
            (TimetableEntry.teacher_id == payload.teacher_id, "Teacher clash detected"),
            (TimetableEntry.classroom_id == payload.classroom_id, "Classroom clash detected"),
            (TimetableEntry.section_id == version.section_id, "Section clash detected"),
        ]
        for condition, message in conditions:
            clash = self.db.scalar(select(TimetableEntry).where(TimetableEntry.college_id == self.college_id, TimetableEntry.weekday == int(payload.weekday), TimetableEntry.time_slot_id == payload.time_slot_id, condition))
            if clash:
                raise HTTPException(status_code=409, detail=message)
