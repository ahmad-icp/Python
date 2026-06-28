from datetime import UTC, datetime
from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.examination.models import AssessmentComponent, Exam
from app.modules.marks_entry.models import MarksBatchStatus, MarksEntry, MarksEntryBatch
from app.modules.results import schemas as s
from app.modules.results.models import GradingPolicy, ResultAuditAction, ResultAuditTrail, ResultOutcome, ResultStatus, StudentResult, SubjectResult
from app.modules.students.models import Student, StudentStatus
from app.modules.academic.models import Subject


class ResultService:
    def __init__(self, db: Session, college_id: str) -> None:
        self.db = db
        self.college_id = college_id

    def _get(self, model, entity_id: str):
        entity = self.db.get(model, entity_id)
        if not entity or entity.college_id != self.college_id:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        return entity

    def create_policy(self, payload: s.GradingPolicyCreate):
        policy = GradingPolicy(college_id=self.college_id, **payload.model_dump())
        self.db.add(policy); self.db.commit(); self.db.refresh(policy)
        return policy

    def list_policies(self, active_only: bool, limit: int, offset: int):
        q = select(GradingPolicy).where(GradingPolicy.college_id == self.college_id)
        if active_only: q = q.where(GradingPolicy.is_active.is_(True))
        total = self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
        return self.db.scalars(q.order_by(GradingPolicy.name, GradingPolicy.version.desc()).limit(limit).offset(offset)).all(), total

    def _policy(self, policy_id: str | None):
        if policy_id: return self._get(GradingPolicy, policy_id)
        policy = self.db.scalar(select(GradingPolicy).where(GradingPolicy.college_id == self.college_id, GradingPolicy.is_active.is_(True)).order_by(GradingPolicy.version.desc()))
        if not policy:
            policy = GradingPolicy(college_id=self.college_id, name="Default Pass Policy", version=1, minimum_percentage=40, grace_marks=0, promotion_minimum_percentage=40)
            self.db.add(policy); self.db.flush()
        return policy

    def calculate(self, payload: s.CalculateRequest, actor_id: str):
        exam = self._get(Exam, payload.exam_id)
        policy = self._policy(payload.policy_id)
        students_q = select(Student).where(Student.college_id == self.college_id, Student.status == StudentStatus.ACTIVE)
        if payload.student_ids: students_q = students_q.where(Student.id.in_(payload.student_ids))
        students = self.db.scalars(students_q).all()
        if not students: raise HTTPException(status_code=404, detail="No active students found for result calculation")
        components = self.db.scalars(select(AssessmentComponent).where(AssessmentComponent.college_id == self.college_id, AssessmentComponent.exam_id == exam.id)).all()
        if not components: raise HTTPException(status_code=409, detail="Exam has no assessment components")
        unlocked = self.db.scalar(select(MarksEntryBatch).where(MarksEntryBatch.college_id == self.college_id, MarksEntryBatch.exam_id == exam.id, MarksEntryBatch.status != MarksBatchStatus.LOCKED).limit(1))
        if unlocked: raise HTTPException(status_code=409, detail="All marks batches must be locked before result calculation")
        by_subject: dict[str, list[AssessmentComponent]] = {}
        for c in components: by_subject.setdefault(c.subject_id, []).append(c)
        results = []
        for student in students:
            existing = self.db.scalar(select(StudentResult).where(StudentResult.college_id == self.college_id, StudentResult.exam_id == exam.id, StudentResult.student_id == student.id))
            if existing and existing.status == ResultStatus.LOCKED and not payload.force_recalculate:
                raise HTTPException(status_code=409, detail="Locked result cannot be recalculated without force_recalculate")
            result = existing or StudentResult(college_id=self.college_id, exam_id=exam.id, student_id=student.id, calculated_by=actor_id)
            if not existing: self.db.add(result); self.db.flush()
            if existing: self.db.execute(delete(SubjectResult).where(SubjectResult.result_id == result.id))
            result.policy_id = policy.id; result.status = ResultStatus.DRAFT; result.calculated_by = actor_id; result.calculated_at = datetime.now(UTC)
            total = obtained = grace_total = 0.0; outcomes = []
            for subject_id, comps in by_subject.items():
                subject = self._get(Subject, subject_id)
                max_marks = sum(float(c.maximum_marks) for c in comps)
                entries = self.db.scalars(select(MarksEntry).where(MarksEntry.college_id == self.college_id, MarksEntry.exam_id == exam.id, MarksEntry.subject_id == subject_id, MarksEntry.student_id == student.id)).all()
                if len(entries) < len(comps):
                    score = 0.0; outcome = ResultOutcome.INCOMPLETE; grace = 0.0
                else:
                    score = sum(float(e.marks_obtained) + float(e.moderation_marks) for e in entries)
                    required = max_marks * float(policy.minimum_percentage) / 100
                    grace = min(float(policy.grace_marks), max(0.0, required - score))
                    outcome = ResultOutcome.PASS if score + grace >= required else ResultOutcome.FAIL
                pct = round(((score + grace) / max_marks) * 100, 2) if max_marks else 0
                self.db.add(SubjectResult(college_id=self.college_id, result_id=result.id, exam_id=exam.id, student_id=student.id, subject_id=subject_id, credit_hours=subject.credit_hours, maximum_marks=max_marks, obtained_marks=score + grace, grace_awarded=grace, percentage=pct, outcome=outcome))
                total += max_marks; obtained += score + grace; grace_total += grace; outcomes.append(outcome)
            result.total_marks = total; result.obtained_marks = obtained; result.grace_awarded = grace_total; result.percentage = round((obtained / total) * 100, 2) if total else 0
            result.outcome = ResultOutcome.PASS if outcomes and all(o == ResultOutcome.PASS for o in outcomes) else (ResultOutcome.INCOMPLETE if ResultOutcome.INCOMPLETE in outcomes else ResultOutcome.FAIL)
            result.is_promotion_eligible = result.outcome == ResultOutcome.PASS and float(result.percentage) >= float(policy.promotion_minimum_percentage)
            self.db.add(ResultAuditTrail(college_id=self.college_id, result_id=result.id, action=ResultAuditAction.RECALCULATED if existing else ResultAuditAction.CALCULATED, actor_id=actor_id, details=f"exam={exam.id};policy={policy.id}"))
            results.append(result)
        self.db.commit()
        for r in results: self.db.refresh(r)
        return results

    def list_results(self, exam_id: str | None, student_id: str | None, status_filter: ResultStatus | None, limit: int, offset: int):
        q = select(StudentResult).where(StudentResult.college_id == self.college_id)
        if exam_id: q = q.where(StudentResult.exam_id == exam_id)
        if student_id: q = q.where(StudentResult.student_id == student_id)
        if status_filter: q = q.where(StudentResult.status == status_filter)
        total = self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
        return self.db.scalars(q.order_by(StudentResult.calculated_at.desc()).limit(limit).offset(offset)).unique().all(), total

    def transition(self, result_id: str, action: str, actor_id: str):
        result = self._get(StudentResult, result_id)
        now = datetime.now(UTC)
        if action == "publish":
            if result.status != ResultStatus.DRAFT: raise HTTPException(status_code=409, detail="Only draft results can be published")
            result.status = ResultStatus.PUBLISHED; result.published_by = actor_id; result.published_at = now; audit = ResultAuditAction.PUBLISHED
        elif action == "lock":
            if result.status != ResultStatus.PUBLISHED: raise HTTPException(status_code=409, detail="Only published results can be locked")
            result.status = ResultStatus.LOCKED; result.locked_by = actor_id; result.locked_at = now; audit = ResultAuditAction.LOCKED
        else: raise HTTPException(status_code=400, detail="Unsupported result transition")
        self.db.add(ResultAuditTrail(college_id=self.college_id, result_id=result.id, action=audit, actor_id=actor_id))
        self.db.commit(); self.db.refresh(result); return result
