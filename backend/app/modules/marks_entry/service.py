import csv
from datetime import UTC, datetime
from io import StringIO

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.academic.models import Section, Subject
from app.modules.examination.models import AssessmentComponent, Exam, ExamStatus
from app.modules.marks_entry import schemas as s
from app.modules.marks_entry.models import MarksAuditAction, MarksAuditTrail, MarksBatchStatus, MarksEntry, MarksEntryBatch
from app.modules.students.models import Student, StudentStatus


class MarksEntryService:
    def __init__(self, db: Session, college_id: str) -> None:
        self.db = db
        self.college_id = college_id

    def _get(self, model, entity_id: str):
        entity = self.db.get(model, entity_id)
        if not entity or entity.college_id != self.college_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found")
        return entity

    def _audit(self, batch_id: str, entry_id: str | None, action: MarksAuditAction, actor_id: str, old_value: str | None = None, new_value: str | None = None, reason: str | None = None) -> None:
        self.db.add(MarksAuditTrail(college_id=self.college_id, batch_id=batch_id, entry_id=entry_id, action=action, actor_id=actor_id, old_value=old_value, new_value=new_value, reason=reason))

    def create_batch(self, payload: s.MarksBatchCreate, created_by: str):
        exam = self._get(Exam, payload.exam_id)
        if exam.status not in {ExamStatus.PUBLISHED, ExamStatus.LOCKED}:
            raise HTTPException(status_code=409, detail="Marks entry requires a published or locked exam")
        section = self._get(Section, payload.section_id)
        subject = self._get(Subject, payload.subject_id)
        component = self._get(AssessmentComponent, payload.component_id)
        if section.id != exam.section_id:
            raise HTTPException(status_code=409, detail="Marks batch section does not match exam section")
        if component.exam_id != exam.id or component.subject_id != subject.id:
            raise HTTPException(status_code=409, detail="Assessment component does not match exam and subject")
        batch = MarksEntryBatch(college_id=self.college_id, created_by=created_by, **payload.model_dump())
        self.db.add(batch)
        self.db.flush()
        self._audit(batch.id, None, MarksAuditAction.CREATED, created_by, new_value="batch created")
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def list_batches(self, exam_id: str | None, section_id: str | None, status_filter: MarksBatchStatus | None, limit: int, offset: int):
        query = select(MarksEntryBatch).where(MarksEntryBatch.college_id == self.college_id)
        if exam_id:
            query = query.where(MarksEntryBatch.exam_id == exam_id)
        if section_id:
            query = query.where(MarksEntryBatch.section_id == section_id)
        if status_filter:
            query = query.where(MarksEntryBatch.status == status_filter)
        total = self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
        items = self.db.scalars(query.order_by(MarksEntryBatch.created_at.desc()).limit(limit).offset(offset)).unique().all()
        return list(items), total

    def upsert_entry(self, batch_id: str, payload: s.MarksEntryUpsert, actor_id: str):
        return self.bulk_upsert(batch_id, s.BulkMarksUpsert(entries=[payload]), actor_id)[0]

    def bulk_upsert(self, batch_id: str, payload: s.BulkMarksUpsert, actor_id: str, audit_action: MarksAuditAction = MarksAuditAction.UPDATED):
        batch = self._get(MarksEntryBatch, batch_id)
        if batch.status != MarksBatchStatus.DRAFT:
            raise HTTPException(status_code=409, detail="Only draft marks batches can be edited")
        component = self._get(AssessmentComponent, batch.component_id)
        section = self._get(Section, batch.section_id)
        results = []
        for entry_payload in payload.entries:
            student = self._get(Student, entry_payload.student_id)
            if student.status != StudentStatus.ACTIVE:
                raise HTTPException(status_code=409, detail="Only active students can receive marks")
            if student.current_section and student.current_section != section.name:
                raise HTTPException(status_code=409, detail="Student does not belong to this marks section")
            self._validate_marks(component, entry_payload)
            existing = self.db.scalar(select(MarksEntry).where(MarksEntry.college_id == self.college_id, MarksEntry.batch_id == batch.id, MarksEntry.student_id == student.id))
            new_value = self._entry_value(entry_payload)
            if existing:
                old_value = self._entry_value(existing)
                existing.marks_obtained = entry_payload.marks_obtained
                existing.moderation_marks = entry_payload.moderation_marks
                existing.recheck_notes = entry_payload.recheck_notes
                existing.remarks = entry_payload.remarks
                existing.updated_by = actor_id
                existing.updated_at = datetime.now(UTC)
                self._audit(batch.id, existing.id, audit_action, actor_id, old_value=old_value, new_value=new_value)
                results.append(existing)
            else:
                entry = MarksEntry(college_id=self.college_id, batch_id=batch.id, exam_id=batch.exam_id, section_id=batch.section_id, subject_id=batch.subject_id, component_id=batch.component_id, entered_by=actor_id, **entry_payload.model_dump())
                self.db.add(entry)
                self.db.flush()
                self._audit(batch.id, entry.id, MarksAuditAction.CREATED if audit_action != MarksAuditAction.IMPORTED else MarksAuditAction.IMPORTED, actor_id, new_value=new_value)
                results.append(entry)
        self.db.commit()
        for entry in results:
            self.db.refresh(entry)
        return results

    def import_marks(self, batch_id: str, payload: s.MarksImportRequest, actor_id: str):
        rows = self._parse_delimited(payload.content)
        entries = [s.MarksEntryUpsert(student_id=row["student_id"], marks_obtained=float(row["marks_obtained"]), moderation_marks=float(row.get("moderation_marks") or 0), remarks=row.get("remarks") or None, recheck_notes=row.get("recheck_notes") or None) for row in rows]
        return self.bulk_upsert(batch_id, s.BulkMarksUpsert(entries=entries), actor_id, MarksAuditAction.IMPORTED)

    def list_entries(self, batch_id: str | None, student_id: str | None, limit: int, offset: int):
        query = select(MarksEntry).where(MarksEntry.college_id == self.college_id)
        if batch_id:
            query = query.where(MarksEntry.batch_id == batch_id)
        if student_id:
            query = query.where(MarksEntry.student_id == student_id)
        total = self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
        items = self.db.scalars(query.order_by(MarksEntry.updated_at.desc()).limit(limit).offset(offset)).unique().all()
        return list(items), total

    def submit_batch(self, batch_id: str, actor_id: str):
        batch = self._get(MarksEntryBatch, batch_id)
        if batch.status != MarksBatchStatus.DRAFT:
            raise HTTPException(status_code=409, detail="Only draft batches can be submitted")
        if not batch.entries:
            raise HTTPException(status_code=409, detail="Cannot submit an empty marks batch")
        batch.status = MarksBatchStatus.SUBMITTED
        batch.submitted_by = actor_id
        batch.submitted_at = datetime.now(UTC)
        self._audit(batch.id, None, MarksAuditAction.SUBMITTED, actor_id)
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def lock_batch(self, batch_id: str, actor_id: str):
        batch = self._get(MarksEntryBatch, batch_id)
        if batch.status != MarksBatchStatus.SUBMITTED:
            raise HTTPException(status_code=409, detail="Only submitted batches can be locked")
        batch.status = MarksBatchStatus.LOCKED
        batch.locked_by = actor_id
        batch.locked_at = datetime.now(UTC)
        self._audit(batch.id, None, MarksAuditAction.LOCKED, actor_id)
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def unlock_batch(self, batch_id: str, payload: s.UnlockRequest, actor_id: str):
        batch = self._get(MarksEntryBatch, batch_id)
        if batch.status != MarksBatchStatus.LOCKED:
            raise HTTPException(status_code=409, detail="Only locked batches can be unlocked")
        batch.status = MarksBatchStatus.DRAFT
        batch.unlocked_by = actor_id
        batch.unlocked_at = datetime.now(UTC)
        batch.unlock_reason = payload.reason
        self._audit(batch.id, None, MarksAuditAction.UNLOCKED, actor_id, reason=payload.reason)
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def list_audit(self, batch_id: str, limit: int, offset: int):
        batch = self._get(MarksEntryBatch, batch_id)
        query = select(MarksAuditTrail).where(MarksAuditTrail.college_id == self.college_id, MarksAuditTrail.batch_id == batch.id)
        total = self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
        items = self.db.scalars(query.order_by(MarksAuditTrail.created_at.desc()).limit(limit).offset(offset)).unique().all()
        return list(items), total

    def _validate_marks(self, component: AssessmentComponent, payload: s.MarksEntryUpsert) -> None:
        maximum = float(component.maximum_marks)
        final_marks = payload.marks_obtained + payload.moderation_marks
        if payload.marks_obtained > maximum:
            raise HTTPException(status_code=409, detail="Marks obtained cannot exceed component maximum marks")
        if final_marks < 0 or final_marks > maximum:
            raise HTTPException(status_code=409, detail="Moderated marks must remain within component marks range")

    def _parse_delimited(self, content: str) -> list[dict[str, str]]:
        reader = csv.DictReader(StringIO(content.strip()))
        required = {"student_id", "marks_obtained"}
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise HTTPException(status_code=422, detail="Import requires student_id and marks_obtained columns")
        return list(reader)

    def _entry_value(self, entry) -> str:
        return f"marks={entry.marks_obtained};moderation={entry.moderation_marks};remarks={entry.remarks or ''};recheck={entry.recheck_notes or ''}"
