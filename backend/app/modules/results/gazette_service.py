import json
from datetime import UTC, datetime
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.modules.results import gazette_schemas as s
from app.modules.results.gazette_models import Gazette, GazetteScope
from app.modules.results.gpa_models import StudentGradeCalculation
from app.modules.results.models import ResultOutcome, StudentResult
from app.modules.students.models import Student
class GazetteService:
    def __init__(self, db: Session, college_id: str): self.db=db; self.college_id=college_id
    def generate(self, payload: s.GazetteGenerateRequest, actor_id: str):
        scope_id = payload.scope_id or ""
        q = select(StudentResult).where(StudentResult.college_id==self.college_id, StudentResult.exam_id==payload.exam_id)
        results = self.db.scalars(q).unique().all()
        if not results: raise HTTPException(status_code=404, detail="No results found for gazette")
        rows=[]
        for r in results:
            student=self.db.get(Student, r.student_id)
            if payload.scope_type != GazetteScope.OVERALL and scope_id:
                attr = {GazetteScope.CLASS:'current_class', GazetteScope.SECTION:'current_section', GazetteScope.PROGRAM:'program'}[payload.scope_type]
                if not student or getattr(student, attr) != scope_id: continue
            grade=self.db.scalar(select(StudentGradeCalculation).where(StudentGradeCalculation.college_id==self.college_id, StudentGradeCalculation.result_id==r.id))
            rows.append({'student_id':r.student_id,'student_name':f"{student.first_name} {student.last_name}" if student else r.student_id,'percentage':float(r.percentage),'gpa':float(grade.gpa) if grade and grade.gpa is not None else None,'grade':grade.grade if grade else None,'outcome':r.outcome.value})
        rows.sort(key=lambda x: (x['gpa'] if x['gpa'] is not None else x['percentage']), reverse=True)
        for idx,row in enumerate(rows,1): row['rank']=idx
        summary={'total':len(rows),'passed':sum(1 for r in rows if r['outcome']==ResultOutcome.PASS.value),'failed':sum(1 for r in rows if r['outcome']==ResultOutcome.FAIL.value)}
        gazette=self.db.scalar(select(Gazette).where(Gazette.college_id==self.college_id, Gazette.exam_id==payload.exam_id, Gazette.scope_type==payload.scope_type, Gazette.scope_id==scope_id))
        if not gazette:
            gazette=Gazette(college_id=self.college_id, exam_id=payload.exam_id, scope_type=payload.scope_type, scope_id=scope_id, title=payload.title, generated_by=actor_id, summary_json='{}', rows_json='[]'); self.db.add(gazette)
        gazette.title=payload.title; gazette.summary_json=json.dumps(summary); gazette.rows_json=json.dumps(rows); gazette.generated_by=actor_id; gazette.generated_at=datetime.now(UTC)
        self.db.commit(); self.db.refresh(gazette); return gazette
    def list(self, exam_id, limit, offset):
        q=select(Gazette).where(Gazette.college_id==self.college_id)
        if exam_id: q=q.where(Gazette.exam_id==exam_id)
        total=self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
        return self.db.scalars(q.order_by(Gazette.generated_at.desc()).limit(limit).offset(offset)).all(), total
