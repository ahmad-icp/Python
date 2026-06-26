from datetime import UTC, date, datetime

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.modules.academic.models import AcademicClass, AcademicSession, Program, Section, Subject, SubjectAllocation
from app.modules.examination import schemas as s
from app.modules.examination.models import AssessmentComponent, Exam, ExamHall, ExamSchedule, ExamStatus, ExamType, InvigilatorAssignment
from app.modules.timetable.models import CalendarEvent, WorkingDay


class ExaminationService:
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
        items = self.db.scalars(query.limit(limit).offset(offset)).unique().all()
        return list(items), total

    def create_exam_type(self, payload: s.ExamTypeCreate):
        item = ExamType(college_id=self.college_id, **payload.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_exam_types(self, search: str | None, limit: int, offset: int):
        return self._list(ExamType, search, limit, offset, ExamType.name)

    def create_exam(self, payload: s.ExamCreate, created_by: str):
        exam_type = self._get(ExamType, payload.exam_type_id)
        if not exam_type.is_active:
            raise HTTPException(status_code=409, detail="Exam type is inactive")
        academic_session = self._get(AcademicSession, payload.session_id)
        academic_class = self._get(AcademicClass, payload.class_id)
        section = self._get(Section, payload.section_id)
        if academic_class.session_id != academic_session.id:
            raise HTTPException(status_code=409, detail="Class does not belong to this academic session")
        if section.class_id != academic_class.id:
            raise HTTPException(status_code=409, detail="Section does not belong to this class")
        if payload.program_id:
            program = self._get(Program, payload.program_id)
            if academic_class.program_id != program.id:
                raise HTTPException(status_code=409, detail="Program does not match the selected class")
        if not (academic_session.start_date <= payload.start_date <= academic_session.end_date and academic_session.start_date <= payload.end_date <= academic_session.end_date):
            raise HTTPException(status_code=409, detail="Exam dates must be inside the academic session")
        item = Exam(college_id=self.college_id, created_by=created_by, **payload.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_exams(self, session_id: str | None, section_id: str | None, status_filter: ExamStatus | None, limit: int, offset: int):
        query = select(Exam).where(Exam.college_id == self.college_id)
        if session_id:
            query = query.where(Exam.session_id == session_id)
        if section_id:
            query = query.where(Exam.section_id == section_id)
        if status_filter:
            query = query.where(Exam.status == status_filter)
        total = self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
        items = self.db.scalars(query.order_by(Exam.start_date.desc()).limit(limit).offset(offset)).unique().all()
        return list(items), total

    def add_component(self, payload: s.AssessmentComponentCreate):
        exam = self._get(Exam, payload.exam_id)
        self._ensure_editable(exam)
        subject = self._get(Subject, payload.subject_id)
        self._validate_subject_allocated(exam.class_id, subject.id)
        total_weightage = self.db.scalar(select(func.coalesce(func.sum(AssessmentComponent.weightage), 0)).where(AssessmentComponent.college_id == self.college_id, AssessmentComponent.exam_id == exam.id, AssessmentComponent.subject_id == subject.id)) or 0
        if float(total_weightage) + payload.weightage > 100:
            raise HTTPException(status_code=409, detail="Subject component weightage cannot exceed 100")
        item = AssessmentComponent(college_id=self.college_id, **payload.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_components(self, exam_id: str | None, subject_id: str | None, limit: int, offset: int):
        query = select(AssessmentComponent).where(AssessmentComponent.college_id == self.college_id)
        if exam_id:
            query = query.where(AssessmentComponent.exam_id == exam_id)
        if subject_id:
            query = query.where(AssessmentComponent.subject_id == subject_id)
        total = self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
        items = self.db.scalars(query.limit(limit).offset(offset)).unique().all()
        return list(items), total

    def create_hall(self, payload: s.ExamHallCreate):
        item = ExamHall(college_id=self.college_id, **payload.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_halls(self, search: str | None, limit: int, offset: int):
        return self._list(ExamHall, search, limit, offset, ExamHall.name, ExamHall.code)

    def schedule_exam(self, payload: s.ExamScheduleCreate):
        exam = self._get(Exam, payload.exam_id)
        self._ensure_editable(exam)
        hall = self._get(ExamHall, payload.hall_id)
        if not hall.is_active:
            raise HTTPException(status_code=409, detail="Exam hall is inactive")
        section = self._get(Section, exam.section_id)
        if section.enrolled_count > hall.capacity:
            raise HTTPException(status_code=409, detail="Exam hall capacity is lower than section enrollment")
        subject = self._get(Subject, payload.subject_id)
        self._validate_subject_allocated(exam.class_id, subject.id)
        component = self.db.scalar(select(AssessmentComponent).where(AssessmentComponent.college_id == self.college_id, AssessmentComponent.exam_id == exam.id, AssessmentComponent.subject_id == subject.id, AssessmentComponent.component_type == payload.component_type))
        if not component:
            raise HTTPException(status_code=409, detail="Assessment component must be configured before scheduling")
        if not (exam.start_date <= payload.exam_date <= exam.end_date):
            raise HTTPException(status_code=409, detail="Schedule date must be inside exam date range")
        self._validate_working_date(exam.session_id, payload.exam_date)
        self._validate_schedule_conflicts(exam, payload)
        item = ExamSchedule(college_id=self.college_id, section_id=exam.section_id, **payload.model_dump())
        self.db.add(item)
        exam.status = ExamStatus.SCHEDULED
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_schedules(self, exam_id: str | None, exam_date: date | None, limit: int, offset: int):
        query = select(ExamSchedule).where(ExamSchedule.college_id == self.college_id)
        if exam_id:
            query = query.where(ExamSchedule.exam_id == exam_id)
        if exam_date:
            query = query.where(ExamSchedule.exam_date == exam_date)
        total = self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
        items = self.db.scalars(query.order_by(ExamSchedule.exam_date, ExamSchedule.start_time).limit(limit).offset(offset)).unique().all()
        return list(items), total

    def assign_invigilator(self, payload: s.InvigilatorAssignmentCreate, assigned_by: str):
        schedule = self._get(ExamSchedule, payload.schedule_id)
        conflict = self.db.scalar(select(InvigilatorAssignment).where(InvigilatorAssignment.college_id == self.college_id, InvigilatorAssignment.teacher_id == payload.teacher_id, InvigilatorAssignment.exam_date == schedule.exam_date, InvigilatorAssignment.start_time < schedule.end_time, InvigilatorAssignment.end_time > schedule.start_time))
        if conflict:
            raise HTTPException(status_code=409, detail="Invigilator has a conflicting exam assignment")
        item = InvigilatorAssignment(college_id=self.college_id, exam_date=schedule.exam_date, start_time=schedule.start_time, end_time=schedule.end_time, assigned_by=assigned_by, **payload.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_invigilators(self, schedule_id: str | None, teacher_id: str | None, limit: int, offset: int):
        query = select(InvigilatorAssignment).where(InvigilatorAssignment.college_id == self.college_id)
        if schedule_id:
            query = query.where(InvigilatorAssignment.schedule_id == schedule_id)
        if teacher_id:
            query = query.where(InvigilatorAssignment.teacher_id == teacher_id)
        total = self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
        items = self.db.scalars(query.limit(limit).offset(offset)).unique().all()
        return list(items), total

    def publish_exam(self, exam_id: str):
        exam = self._get(Exam, exam_id)
        if exam.status not in {ExamStatus.SCHEDULED, ExamStatus.PUBLISHED}:
            raise HTTPException(status_code=409, detail="Only scheduled exams can be published")
        if not exam.components or not exam.schedules:
            raise HTTPException(status_code=409, detail="Components and schedules are required before publishing")
        exam.status = ExamStatus.PUBLISHED
        exam.published_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(exam)
        return exam

    def lock_exam(self, exam_id: str):
        exam = self._get(Exam, exam_id)
        if exam.status != ExamStatus.PUBLISHED:
            raise HTTPException(status_code=409, detail="Only published exams can be locked")
        exam.status = ExamStatus.LOCKED
        exam.locked_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(exam)
        return exam

    def _ensure_editable(self, exam: Exam) -> None:
        if exam.status in {ExamStatus.PUBLISHED, ExamStatus.LOCKED, ExamStatus.CANCELLED}:
            raise HTTPException(status_code=409, detail="Published, locked, or cancelled exams cannot be edited")

    def _validate_subject_allocated(self, class_id: str, subject_id: str) -> None:
        allocation = self.db.scalar(select(SubjectAllocation).where(SubjectAllocation.college_id == self.college_id, SubjectAllocation.class_id == class_id, SubjectAllocation.subject_id == subject_id))
        if not allocation:
            raise HTTPException(status_code=409, detail="Subject is not allocated to this class")

    def _validate_schedule_conflicts(self, exam: Exam, payload: s.ExamScheduleCreate) -> None:
        overlap = (ExamSchedule.start_time < payload.end_time, ExamSchedule.end_time > payload.start_time)
        hall_conflict = self.db.scalar(select(ExamSchedule).where(ExamSchedule.college_id == self.college_id, ExamSchedule.hall_id == payload.hall_id, ExamSchedule.exam_date == payload.exam_date, *overlap))
        if hall_conflict:
            raise HTTPException(status_code=409, detail="Exam hall is already booked for this time")
        section_conflict = self.db.scalar(select(ExamSchedule).where(ExamSchedule.college_id == self.college_id, ExamSchedule.section_id == exam.section_id, ExamSchedule.exam_date == payload.exam_date, *overlap))
        if section_conflict:
            raise HTTPException(status_code=409, detail="Section already has an exam at this time")

    def _validate_working_date(self, session_id: str, exam_date: date) -> None:
        holiday = self.db.scalar(select(CalendarEvent).where(CalendarEvent.college_id == self.college_id, CalendarEvent.session_id == session_id, CalendarEvent.is_holiday.is_(True), CalendarEvent.start_date <= exam_date, CalendarEvent.end_date >= exam_date))
        if holiday:
            raise HTTPException(status_code=409, detail="Cannot schedule an exam on an academic holiday")
        working_day = self.db.scalar(select(WorkingDay).where(WorkingDay.college_id == self.college_id, WorkingDay.session_id == session_id, WorkingDay.weekday == exam_date.isoweekday()))
        if working_day and not working_day.is_working:
            raise HTTPException(status_code=409, detail="Cannot schedule an exam on a non-working day")
