from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.modules.academic.models import *
from app.modules.academic import schemas as s


class AcademicService:
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

    def create_institution(self, payload: s.InstitutionCreate):
        item = Institution(college_id=self.college_id, **payload.model_dump())
        self.db.add(item); self.db.commit(); self.db.refresh(item); return item
    def list_institutions(self, search, limit, offset): return self._list(Institution, search, limit, offset, Institution.name, Institution.code)

    def create_campus(self, payload: s.CampusCreate):
        self._get(Institution, payload.institution_id)
        item = Campus(college_id=self.college_id, **payload.model_dump())
        self.db.add(item); self.db.commit(); self.db.refresh(item); return item
    def list_campuses(self, search, limit, offset): return self._list(Campus, search, limit, offset, Campus.name, Campus.code)

    def create_department(self, payload: s.DepartmentCreate):
        self._get(Institution, payload.institution_id)
        if payload.campus_id: self._get(Campus, payload.campus_id)
        item = Department(college_id=self.college_id, **payload.model_dump())
        self.db.add(item); self.db.commit(); self.db.refresh(item); return item
    def list_departments(self, search, limit, offset): return self._list(Department, search, limit, offset, Department.name, Department.code)

    def create_session(self, payload: s.AcademicSessionCreate):
        if payload.status == SessionStatus.ACTIVE:
            active = self.db.scalar(select(AcademicSession).where(AcademicSession.college_id == self.college_id, AcademicSession.status == SessionStatus.ACTIVE))
            if active:
                raise HTTPException(status_code=409, detail="Only one active academic session is allowed")
        item = AcademicSession(college_id=self.college_id, **payload.model_dump())
        self.db.add(item); self.db.commit(); self.db.refresh(item); return item
    def list_sessions(self, search, limit, offset): return self._list(AcademicSession, search, limit, offset, AcademicSession.name)

    def create_program(self, payload: s.ProgramCreate):
        self._get(Department, payload.department_id)
        item = Program(college_id=self.college_id, **payload.model_dump())
        self.db.add(item); self.db.commit(); self.db.refresh(item); return item
    def list_programs(self, search, limit, offset): return self._list(Program, search, limit, offset, Program.name, Program.code)

    def create_class(self, payload: s.AcademicClassCreate):
        self._get(Program, payload.program_id); self._get(AcademicSession, payload.session_id)
        duplicate = self.db.scalar(select(AcademicClass).where(AcademicClass.college_id == self.college_id, AcademicClass.program_id == payload.program_id, AcademicClass.session_id == payload.session_id, func.lower(AcademicClass.name) == payload.name.strip().lower()))
        if duplicate:
            raise HTTPException(status_code=409, detail="Class name already exists for this program and session")
        item = AcademicClass(college_id=self.college_id, **payload.model_dump())
        self.db.add(item); self.db.commit(); self.db.refresh(item); return item
    def list_classes(self, search, limit, offset): return self._list(AcademicClass, search, limit, offset, AcademicClass.name)

    def create_section(self, payload: s.SectionCreate):
        self._get(AcademicClass, payload.class_id)
        item = Section(college_id=self.college_id, **payload.model_dump())
        self.db.add(item); self.db.commit(); self.db.refresh(item); return item
    def list_sections(self, search, limit, offset): return self._list(Section, search, limit, offset, Section.name, Section.room)

    def create_subject(self, payload: s.SubjectCreate):
        if payload.department_id: self._get(Department, payload.department_id)
        subject = Subject(college_id=self.college_id, **payload.model_dump(exclude={"prerequisite_subject_ids"}))
        self.db.add(subject); self.db.flush()
        for prereq_id in payload.prerequisite_subject_ids:
            prereq = self._get(Subject, prereq_id)
            if prereq.id == subject.id:
                raise HTTPException(status_code=422, detail="Subject cannot be its own prerequisite")
            self.db.add(SubjectPrerequisite(subject_id=subject.id, prerequisite_subject_id=prereq.id))
        self.db.commit(); self.db.refresh(subject); return subject
    def list_subjects(self, search, limit, offset): return self._list(Subject, search, limit, offset, Subject.name, Subject.code)

    def create_subject_group(self, payload: s.SubjectGroupCreate):
        item = SubjectGroup(college_id=self.college_id, **payload.model_dump())
        self.db.add(item); self.db.commit(); self.db.refresh(item); return item
    def list_subject_groups(self, search, limit, offset): return self._list(SubjectGroup, search, limit, offset, SubjectGroup.name)

    def create_elective_group(self, payload: s.ElectiveGroupCreate):
        self._get(AcademicClass, payload.class_id)
        item = ElectiveGroup(college_id=self.college_id, **payload.model_dump())
        self.db.add(item); self.db.commit(); self.db.refresh(item); return item

    def create_subject_allocation(self, payload: s.SubjectAllocationCreate):
        klass = self._get(AcademicClass, payload.class_id); subject = self._get(Subject, payload.subject_id)
        if payload.elective_group_id: self._get(ElectiveGroup, payload.elective_group_id)
        if payload.subject_group_id: self._get(SubjectGroup, payload.subject_group_id)
        for prereq in subject.prerequisites:
            exists = self.db.scalar(select(SubjectAllocation).where(SubjectAllocation.class_id == klass.id, SubjectAllocation.subject_id == prereq.prerequisite_subject_id))
            if not exists:
                raise HTTPException(status_code=409, detail="Subject prerequisite must be allocated to the class first")
        item = SubjectAllocation(college_id=self.college_id, **payload.model_dump())
        self.db.add(item); self.db.commit(); self.db.refresh(item); return item
    def list_subject_allocations(self, search, limit, offset): return self._list(SubjectAllocation, None, limit, offset)

    def create_teacher_assignment(self, payload: s.TeacherAssignmentCreate):
        self._get(Section, payload.section_id); self._get(Subject, payload.subject_id)
        assigned = self.db.scalar(select(func.coalesce(func.sum(TeacherAssignment.weekly_periods), 0)).where(TeacherAssignment.college_id == self.college_id, TeacherAssignment.teacher_id == payload.teacher_id, TeacherAssignment.status == AssignmentStatus.ACTIVE)) or 0
        if assigned + payload.weekly_periods > payload.max_weekly_periods:
            raise HTTPException(status_code=409, detail="Teacher workload would exceed maximum weekly periods")
        item = TeacherAssignment(college_id=self.college_id, **payload.model_dump())
        self.db.add(item); self.db.commit(); self.db.refresh(item); return item
    def list_teacher_assignments(self, search, limit, offset): return self._list(TeacherAssignment, search, limit, offset, TeacherAssignment.teacher_name, TeacherAssignment.teacher_id)

    def teacher_workload(self, teacher_id: str):
        rows = list(self.db.scalars(select(TeacherAssignment).where(TeacherAssignment.college_id == self.college_id, TeacherAssignment.teacher_id == teacher_id, TeacherAssignment.status == AssignmentStatus.ACTIVE)).all())
        if not rows: raise HTTPException(status_code=404, detail="Teacher assignment not found")
        total = sum(row.weekly_periods for row in rows); max_periods = max(row.max_weekly_periods for row in rows)
        return s.TeacherWorkloadRead(teacher_id=teacher_id, teacher_name=rows[0].teacher_name, assigned_periods=total, max_weekly_periods=max_periods, remaining_periods=max_periods-total, assignment_count=len(rows))

    def create_promotion_rule(self, payload: s.PromotionRuleCreate):
        from_class = self._get(AcademicClass, payload.from_class_id); to_class = self._get(AcademicClass, payload.to_class_id)
        if from_class.program_id != to_class.program_id:
            raise HTTPException(status_code=409, detail="Promotion rule classes must belong to the same program")
        item = PromotionRule(college_id=self.college_id, **payload.model_dump())
        self.db.add(item); self.db.commit(); self.db.refresh(item); return item
    def list_promotion_rules(self, search, limit, offset): return self._list(PromotionRule, None, limit, offset)

    def archive(self, payload: s.ArchiveRequest, archived_by: str):
        item = AcademicArchive(college_id=self.college_id, archived_by=archived_by, **payload.model_dump())
        self.db.add(item); self.db.commit(); self.db.refresh(item); return item
    def list_archives(self, search, limit, offset): return self._list(AcademicArchive, search, limit, offset, AcademicArchive.entity_type, AcademicArchive.entity_id)
