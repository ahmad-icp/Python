import hashlib, html, json
from datetime import UTC, datetime
from fastapi import HTTPException
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session
from app.modules.results import merit_schemas as s
from app.modules.results.gpa_models import StudentGradeCalculation
from app.modules.results.merit_models import MeritBasis, MeritCertificate, MeritList, MeritListItem, MeritScope, MeritStatus, TieBreaker
from app.modules.results.models import ResultOutcome, StudentResult
from app.modules.students.models import Student

class MeritService:
    def __init__(self, db: Session, college_id: str): self.db=db; self.college_id=college_id
    def _get(self, model, entity_id: str):
        entity=self.db.get(model,entity_id)
        if not entity or entity.college_id != self.college_id: raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        return entity
    def generate(self, payload: s.MeritListGenerateRequest, actor_id: str):
        scope_id=payload.scope_id or ""
        results=self.db.scalars(select(StudentResult).where(StudentResult.college_id==self.college_id, StudentResult.exam_id==payload.exam_id, StudentResult.outcome==ResultOutcome.PASS)).unique().all()
        rows=[]
        for result in results:
            student=self.db.get(Student,result.student_id)
            if not student or not self._in_scope(student,payload.scope_type,scope_id): continue
            grade=self.db.scalar(select(StudentGradeCalculation).where(StudentGradeCalculation.college_id==self.college_id, StudentGradeCalculation.result_id==result.id))
            if payload.basis==MeritBasis.GPA and (not grade or grade.gpa is None): continue
            score=float(grade.gpa) if payload.basis==MeritBasis.GPA and grade and grade.gpa is not None else float(result.percentage)
            rows.append((score,result,grade,student,self._tie_value(student,payload.tie_breakers)))
        if not rows: raise HTTPException(status_code=404, detail="No eligible students found for merit list")
        rows.sort(key=lambda row: self._sort_key(row,payload.basis,payload.tie_breakers))
        merit=self.db.scalar(select(MeritList).where(MeritList.college_id==self.college_id, MeritList.exam_id==payload.exam_id, MeritList.scope_type==payload.scope_type, MeritList.scope_id==scope_id, MeritList.basis==payload.basis))
        if merit and merit.status==MeritStatus.LOCKED: raise HTTPException(status_code=409, detail="Locked merit list cannot be regenerated")
        if not merit:
            merit=MeritList(college_id=self.college_id, exam_id=payload.exam_id, scope_type=payload.scope_type, scope_id=scope_id, basis=payload.basis, title=payload.title, tie_breakers="[]", analytics_json="{}", generated_by=actor_id); self.db.add(merit); self.db.flush()
        else: self.db.execute(delete(MeritListItem).where(MeritListItem.merit_list_id==merit.id))
        merit.title=payload.title; merit.tie_breakers=json.dumps([tb.value for tb in payload.tie_breakers]); merit.status=MeritStatus.PUBLISHED if payload.publish_immediately else MeritStatus.DRAFT; merit.generated_by=actor_id; merit.generated_at=datetime.now(UTC); merit.published_by=actor_id if payload.publish_immediately else None; merit.published_at=datetime.now(UTC) if payload.publish_immediately else None
        analytics={'eligible_count':len(rows),'basis':payload.basis.value,'top_score':rows[0][0],'average_score':round(sum(r[0] for r in rows)/len(rows),3)}; merit.analytics_json=json.dumps(analytics)
        for rank,(score,result,grade,student,tie_value) in enumerate(rows,1):
            self.db.add(MeritListItem(college_id=self.college_id, merit_list_id=merit.id, result_id=result.id, grade_calculation_id=grade.id if grade else None, student_id=student.id, rank=rank, score=score, percentage=float(result.percentage), gpa=float(grade.gpa) if grade and grade.gpa is not None else None, tie_breaker_value=tie_value))
        self.db.commit(); self.db.refresh(merit); return merit
    def publish(self, merit_id: str, actor_id: str):
        merit=self._get(MeritList,merit_id)
        if merit.status==MeritStatus.LOCKED: raise HTTPException(status_code=409, detail="Locked merit list cannot be republished")
        merit.status=MeritStatus.PUBLISHED; merit.published_by=actor_id; merit.published_at=datetime.now(UTC); self.db.commit(); self.db.refresh(merit); return merit
    def lock(self, merit_id: str, actor_id: str):
        merit=self._get(MeritList,merit_id)
        if merit.status!=MeritStatus.PUBLISHED: raise HTTPException(status_code=409, detail="Only published merit lists can be locked")
        merit.status=MeritStatus.LOCKED; self.db.commit(); self.db.refresh(merit); return merit
    def list(self, exam_id, scope_type, limit, offset):
        q=select(MeritList).where(MeritList.college_id==self.college_id)
        if exam_id: q=q.where(MeritList.exam_id==exam_id)
        if scope_type: q=q.where(MeritList.scope_type==scope_type)
        total=self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
        return self.db.scalars(q.order_by(MeritList.generated_at.desc()).limit(limit).offset(offset)).unique().all(), total
    def issue_certificate(self,item_id,actor_id):
        item=self._get(MeritListItem,item_id); code=hashlib.sha256(f"{self.college_id}:{item.id}:{item.rank}".encode()).hexdigest()[:24].upper()
        cert=self.db.scalar(select(MeritCertificate).where(MeritCertificate.college_id==self.college_id, MeritCertificate.merit_item_id==item.id))
        if cert: return cert
        body=f"<html><body><h1>Merit Certificate</h1><p>Rank {item.rank}</p><p>Student {html.escape(item.student_id)}</p><p>Score {item.score}</p><p>Verification {code}</p></body></html>"
        cert=MeritCertificate(college_id=self.college_id, merit_item_id=item.id, verification_code=code, printable_html=body, issued_by=actor_id); item.is_certificate_issued=True; self.db.add(cert); self.db.commit(); self.db.refresh(cert); return cert
    def _in_scope(self, st, scope, scope_id):
        if scope==MeritScope.INSTITUTION or not scope_id: return True
        return getattr(st,{MeritScope.PROGRAM:'program',MeritScope.CLASS:'current_class',MeritScope.SECTION:'current_section',MeritScope.SESSION:'academic_session'}[scope])==scope_id
    def _tie_value(self, st, breakers): return '|'.join(str(getattr(st,{TieBreaker.DOB_OLDER:'date_of_birth',TieBreaker.DOB_YOUNGER:'date_of_birth',TieBreaker.ADMISSION_NUMBER:'admission_number',TieBreaker.NAME:'first_name'}[b])) for b in breakers)
    def _sort_key(self,row,basis,breakers):
        score,_,_,st,_=row; keys=[-score]
        for b in breakers:
            if b==TieBreaker.DOB_OLDER: keys.append(st.date_of_birth.toordinal())
            elif b==TieBreaker.DOB_YOUNGER: keys.append(-st.date_of_birth.toordinal())
            elif b==TieBreaker.ADMISSION_NUMBER: keys.append(st.admission_number)
            else: keys.append(f"{st.first_name} {st.last_name}")
        return tuple(keys)
