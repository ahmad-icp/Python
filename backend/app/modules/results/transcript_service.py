import hashlib, html, json
from datetime import UTC, datetime
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.modules.results import transcript_schemas as s
from app.modules.results.gpa_models import StudentGradeCalculation
from app.modules.results.models import StudentResult
from app.modules.results.transcript_models import Transcript, TranscriptStatus
from app.modules.students.models import Student
class TranscriptService:
    def __init__(self, db:Session, college_id:str): self.db=db; self.college_id=college_id
    def _get(self, model, entity_id):
        e=self.db.get(model,entity_id)
        if not e or e.college_id!=self.college_id: raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        return e
    def generate(self,payload:s.TranscriptGenerateRequest,actor_id:str):
        student=self._get(Student,payload.student_id)
        results=self.db.scalars(select(StudentResult).where(StudentResult.college_id==self.college_id, StudentResult.student_id==student.id).order_by(StudentResult.calculated_at)).unique().all()
        if not results: raise HTTPException(status_code=404, detail="No academic history found for transcript")
        history=[]; total_obt=total_marks=0; latest_cgpa=None; total_ch=earned_ch=0
        for r in results:
            g=self.db.scalar(select(StudentGradeCalculation).where(StudentGradeCalculation.college_id==self.college_id, StudentGradeCalculation.result_id==r.id))
            history.append({'exam_id':r.exam_id,'percentage':float(r.percentage),'outcome':r.outcome.value,'gpa':float(g.gpa) if g and g.gpa is not None else None,'cgpa':float(g.cgpa) if g and g.cgpa is not None else None,'grade':g.grade if g else None,'subjects':[{'subject_id':s.subject_id,'obtained':float(s.obtained_marks),'maximum':float(s.maximum_marks),'percentage':float(s.percentage),'outcome':s.outcome.value} for s in r.subjects]})
            total_obt+=float(r.obtained_marks); total_marks+=float(r.total_marks)
            if g and g.cgpa is not None: latest_cgpa=float(g.cgpa)
            if g: total_ch+=g.total_credit_hours or 0; earned_ch+=g.earned_credit_hours or 0
        summary={'overall_percentage':round((total_obt/total_marks)*100,2) if total_marks else 0,'latest_cgpa':latest_cgpa,'total_credit_hours':total_ch or None,'earned_credit_hours':earned_ch or None,'records':len(history)}
        code=hashlib.sha256(f"{self.college_id}:{student.id}:{len(history)}".encode()).hexdigest()[:24].upper()
        printable=self._html(payload.institution_name,student,history,summary,code,payload.remarks)
        tr=Transcript(college_id=self.college_id,student_id=student.id,verification_code=code,institution_name=payload.institution_name,academic_history_json=json.dumps(history),summary_json=json.dumps(summary),printable_html=printable,generated_by=actor_id)
        self.db.add(tr); self.db.commit(); self.db.refresh(tr); return tr
    def issue(self,id,actor_id):
        tr=self._get(Transcript,id)
        if tr.status==TranscriptStatus.REVOKED: raise HTTPException(status_code=409, detail="Revoked transcript cannot be issued")
        tr.status=TranscriptStatus.ISSUED; tr.issued_by=actor_id; tr.issued_at=datetime.now(UTC); self.db.commit(); self.db.refresh(tr); return tr
    def verify(self,code):
        tr=self.db.scalar(select(Transcript).where(Transcript.college_id==self.college_id,Transcript.verification_code==code,Transcript.status==TranscriptStatus.ISSUED))
        if not tr: raise HTTPException(status_code=404, detail="Transcript verification failed")
        return tr
    def list(self,student_id,limit,offset):
        q=select(Transcript).where(Transcript.college_id==self.college_id)
        if student_id: q=q.where(Transcript.student_id==student_id)
        total=self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
        return self.db.scalars(q.order_by(Transcript.generated_at.desc()).limit(limit).offset(offset)).all(), total
    def _html(self,institution,student,history,summary,code,remarks):
        rows=''.join(f"<tr><td>{h['exam_id']}</td><td>{h['percentage']}%</td><td>{h.get('gpa') or 'N/A'}</td><td>{h.get('cgpa') or 'N/A'}</td><td>{h['outcome']}</td></tr>" for h in history)
        return f"<html><body><h1>{html.escape(institution)}</h1><h2>Official Transcript</h2><p>{html.escape(student.first_name)} {html.escape(student.last_name)} - {html.escape(student.admission_number)}</p><table><thead><tr><th>Exam</th><th>%</th><th>GPA</th><th>CGPA</th><th>Outcome</th></tr></thead><tbody>{rows}</tbody></table><p>Overall %: {summary['overall_percentage']} CGPA: {summary.get('latest_cgpa') or 'N/A'}</p><p>{html.escape(remarks or '')}</p><p>Verification: {code}</p><button onclick='window.print()'>Print / Save PDF</button></body></html>"
