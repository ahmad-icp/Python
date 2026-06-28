import hashlib, html, json
from datetime import UTC, datetime
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.modules.results import report_card_schemas as s
from app.modules.results.gpa_models import StudentGradeCalculation
from app.modules.results.models import ResultStatus, StudentResult
from app.modules.results.report_card_models import ReportCard, ReportCardStatus
from app.modules.students.models import Student

class ReportCardService:
    def __init__(self, db: Session, college_id: str) -> None:
        self.db = db; self.college_id = college_id
    def _get(self, model, entity_id: str):
        entity = self.db.get(model, entity_id)
        if not entity or entity.college_id != self.college_id: raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        return entity
    def generate(self, payload: s.ReportCardGenerateRequest, actor_id: str):
        result = self._get(StudentResult, payload.result_id)
        if result.status == ResultStatus.DRAFT: raise HTTPException(status_code=409, detail="Only published or locked results can be printed")
        grade_calc = self._get(StudentGradeCalculation, payload.grade_calculation_id) if payload.grade_calculation_id else self.db.scalar(select(StudentGradeCalculation).where(StudentGradeCalculation.college_id == self.college_id, StudentGradeCalculation.result_id == result.id))
        student = self._get(Student, result.student_id)
        code = hashlib.sha256(f"{self.college_id}:{result.id}:{student.id}".encode()).hexdigest()[:24].upper()
        qr_payload = json.dumps({"college_id": self.college_id, "report_card": code, "student_id": student.id}, separators=(",", ":"))
        printable = self._render_html(payload.institution_name, payload.branding, result, grade_calc, student, payload.remarks, code)
        card = self.db.scalar(select(ReportCard).where(ReportCard.college_id == self.college_id, ReportCard.result_id == result.id))
        if card and card.status == ReportCardStatus.REVOKED: raise HTTPException(status_code=409, detail="Revoked report cards cannot be regenerated")
        if not card:
            card = ReportCard(college_id=self.college_id, result_id=result.id, exam_id=result.exam_id, student_id=student.id, verification_code=code, generated_by=actor_id, qr_payload=qr_payload, printable_html=printable, institution_name=payload.institution_name)
            self.db.add(card)
        card.grade_calculation_id = grade_calc.id if grade_calc else None; card.branding_json = json.dumps(payload.branding); card.remarks = payload.remarks; card.qr_payload = qr_payload; card.printable_html = printable; card.generated_by = actor_id; card.generated_at = datetime.now(UTC)
        self.db.commit(); self.db.refresh(card); return card
    def issue(self, card_id: str, actor_id: str):
        card = self._get(ReportCard, card_id)
        if card.status == ReportCardStatus.REVOKED: raise HTTPException(status_code=409, detail="Revoked report cards cannot be issued")
        card.status = ReportCardStatus.ISSUED; card.issued_by = actor_id; card.issued_at = datetime.now(UTC)
        self.db.commit(); self.db.refresh(card); return card
    def verify(self, code: str):
        card = self.db.scalar(select(ReportCard).where(ReportCard.college_id == self.college_id, ReportCard.verification_code == code, ReportCard.status == ReportCardStatus.ISSUED))
        if not card: raise HTTPException(status_code=404, detail="Report card verification failed")
        return card
    def list_cards(self, student_id: str | None, exam_id: str | None, limit: int, offset: int):
        q = select(ReportCard).where(ReportCard.college_id == self.college_id)
        if student_id: q = q.where(ReportCard.student_id == student_id)
        if exam_id: q = q.where(ReportCard.exam_id == exam_id)
        total = self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
        return self.db.scalars(q.order_by(ReportCard.generated_at.desc()).limit(limit).offset(offset)).all(), total
    def _render_html(self, institution, branding, result, grade_calc, student, remarks, code):
        rows = ''.join(f"<tr><td>{html.escape(subject.subject_id)}</td><td>{subject.obtained_marks}</td><td>{subject.maximum_marks}</td><td>{subject.percentage}%</td><td>{subject.outcome.value}</td></tr>" for subject in result.subjects)
        gpa = '' if not grade_calc else f"<p><strong>Grade:</strong> {html.escape(grade_calc.grade)} <strong>GPA:</strong> {grade_calc.gpa or 'N/A'} <strong>CGPA:</strong> {grade_calc.cgpa or 'N/A'}</p>"
        return f"""<!doctype html><html><head><meta charset='utf-8'><title>DMC {code}</title><style>body{{font-family:Arial,sans-serif}}table{{width:100%;border-collapse:collapse}}td,th{{border:1px solid #999;padding:6px}}@media print{{button{{display:none}}}}</style></head><body><header><h1>{html.escape(institution)}</h1><p>{html.escape(branding.get('tagline','Detailed Marks Certificate'))}</p></header><h2>Detailed Marks Certificate</h2><p><strong>Student:</strong> {html.escape(student.first_name)} {html.escape(student.last_name)} <strong>Admission:</strong> {html.escape(student.admission_number)}</p><table><thead><tr><th>Subject</th><th>Obtained</th><th>Total</th><th>%</th><th>Result</th></tr></thead><tbody>{rows}</tbody></table><p><strong>Total:</strong> {result.obtained_marks}/{result.total_marks} <strong>Percentage:</strong> {result.percentage}% <strong>Outcome:</strong> {result.outcome.value}</p>{gpa}<p><strong>Remarks:</strong> {html.escape(remarks or '')}</p><p><strong>QR Verification:</strong> {code}</p><button onclick='window.print()'>Print / Save PDF</button></body></html>"""
