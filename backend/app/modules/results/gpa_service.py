import math
from datetime import UTC, datetime
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.results import gpa_schemas as s
from app.modules.results.gpa_models import AcademicStanding, GradeMapping, GradeSystem, GradingSystemType, RoundingMode, StudentGradeCalculation
from app.modules.results.models import ResultOutcome, StudentResult


class GradeCalculationService:
    def __init__(self, db: Session, college_id: str) -> None:
        self.db = db
        self.college_id = college_id

    def _get(self, model, entity_id: str):
        entity = self.db.get(model, entity_id)
        if not entity or entity.college_id != self.college_id:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        return entity

    def create_system(self, payload: s.GradeSystemCreate):
        self._validate_mapping_coverage(payload.mappings)
        system = GradeSystem(college_id=self.college_id, **payload.model_dump(exclude={"mappings"}))
        self.db.add(system); self.db.flush()
        for mapping_payload in payload.mappings:
            if payload.system_type == GradingSystemType.PERCENTAGE and mapping_payload.grade_point:
                raise HTTPException(status_code=422, detail="Percentage grading systems cannot define GPA grade points")
            self.db.add(GradeMapping(college_id=self.college_id, system_id=system.id, **mapping_payload.model_dump()))
        self.db.commit(); self.db.refresh(system)
        return system

    def list_systems(self, scope_type: str | None, active_only: bool, limit: int, offset: int):
        q = select(GradeSystem).where(GradeSystem.college_id == self.college_id)
        if scope_type: q = q.where(GradeSystem.scope_type == scope_type)
        if active_only: q = q.where(GradeSystem.is_active.is_(True))
        total = self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
        return self.db.scalars(q.order_by(GradeSystem.scope_type, GradeSystem.name, GradeSystem.version.desc()).limit(limit).offset(offset)).unique().all(), total

    def calculate(self, payload: s.GradeCalculationRequest, actor_id: str):
        system = self._resolve_system(payload.system_id)
        calculations = []
        for result_id in payload.result_ids:
            result = self._get(StudentResult, result_id)
            existing = self.db.scalar(select(StudentGradeCalculation).where(StudentGradeCalculation.college_id == self.college_id, StudentGradeCalculation.result_id == result.id))
            if existing and not payload.force_recalculate:
                raise HTTPException(status_code=409, detail="Grade calculation already exists; use force_recalculate")
            calc = existing or StudentGradeCalculation(college_id=self.college_id, result_id=result.id, exam_id=result.exam_id, student_id=result.student_id, system_id=system.id, calculated_by=actor_id)
            if not existing: self.db.add(calc)
            percentage = self._round(float(result.percentage), system)
            mapping = self._mapping_for_percentage(system, percentage)
            calc.system_id = system.id; calc.percentage = percentage; calc.grade = mapping.grade
            if system.system_type == GradingSystemType.GPA:
                total_ch = sum(subject.credit_hours for subject in result.subjects)
                earned_ch = sum(subject.credit_hours for subject in result.subjects if subject.outcome == ResultOutcome.PASS)
                weighted_points = sum(subject.credit_hours * self._mapping_for_percentage(system, float(subject.percentage)).grade_point for subject in result.subjects)
                calc.total_credit_hours = total_ch; calc.earned_credit_hours = earned_ch
                calc.gpa = self._round(weighted_points / total_ch if total_ch else 0, system)
                previous = self.db.scalars(select(StudentGradeCalculation).where(StudentGradeCalculation.college_id == self.college_id, StudentGradeCalculation.student_id == result.student_id, StudentGradeCalculation.id != calc.id, StudentGradeCalculation.gpa.is_not(None))).all()
                total_weight = total_ch + sum(p.total_credit_hours or 0 for p in previous)
                calc.cgpa = self._round(((float(calc.gpa) * total_ch) + sum(float(p.gpa or 0) * (p.total_credit_hours or 0) for p in previous)) / total_weight if total_weight else float(calc.gpa), system)
                calc.is_promotion_eligible = result.outcome == ResultOutcome.PASS and float(calc.gpa) >= float(system.passing_gpa)
            else:
                calc.gpa = None; calc.cgpa = None; calc.total_credit_hours = None; calc.earned_credit_hours = None
                calc.is_promotion_eligible = result.outcome == ResultOutcome.PASS and percentage >= float(system.passing_percentage)
            calc.academic_standing = self._standing(system, percentage, calc.gpa)
            calc.calculated_by = actor_id; calc.calculated_at = datetime.now(UTC)
            calc.remarks = mapping.remark
            calculations.append(calc)
        self.db.commit()
        for calc in calculations: self.db.refresh(calc)
        return calculations

    def list_calculations(self, student_id: str | None, exam_id: str | None, limit: int, offset: int):
        q = select(StudentGradeCalculation).where(StudentGradeCalculation.college_id == self.college_id)
        if student_id: q = q.where(StudentGradeCalculation.student_id == student_id)
        if exam_id: q = q.where(StudentGradeCalculation.exam_id == exam_id)
        total = self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
        return self.db.scalars(q.order_by(StudentGradeCalculation.calculated_at.desc()).limit(limit).offset(offset)).all(), total

    def _resolve_system(self, system_id: str | None):
        if system_id: return self._get(GradeSystem, system_id)
        system = self.db.scalar(select(GradeSystem).where(GradeSystem.college_id == self.college_id, GradeSystem.is_active.is_(True)).order_by(GradeSystem.version.desc()))
        if not system:
            raise HTTPException(status_code=409, detail="No active grading system configured")
        return system

    def _mapping_for_percentage(self, system: GradeSystem, percentage: float) -> GradeMapping:
        for mapping in sorted(system.mappings, key=lambda m: float(m.min_percentage), reverse=True):
            if float(mapping.min_percentage) <= percentage <= float(mapping.max_percentage):
                return mapping
        raise HTTPException(status_code=409, detail="No grade mapping covers calculated percentage")

    def _round(self, value: float, system: GradeSystem) -> float:
        factor = 10 ** system.decimal_places
        if system.rounding_mode == RoundingMode.FLOOR:
            return math.floor(value * factor) / factor
        if system.rounding_mode == RoundingMode.CEIL:
            return math.ceil(value * factor) / factor
        return round(value, system.decimal_places)

    def _standing(self, system: GradeSystem, percentage: float, gpa: float | None) -> AcademicStanding:
        if system.system_type == GradingSystemType.GPA and gpa is not None:
            ratio = gpa / float(system.gpa_scale)
            if ratio >= 0.85: return AcademicStanding.EXCELLENT
            if ratio >= 0.70: return AcademicStanding.GOOD
            if gpa >= float(system.passing_gpa): return AcademicStanding.SATISFACTORY
            if gpa >= max(float(system.passing_gpa) - 0.5, 0): return AcademicStanding.PROBATION
            return AcademicStanding.FAILING
        if percentage >= 85: return AcademicStanding.EXCELLENT
        if percentage >= 70: return AcademicStanding.GOOD
        if percentage >= float(system.passing_percentage): return AcademicStanding.SATISFACTORY
        if percentage >= max(float(system.passing_percentage) - 5, 0): return AcademicStanding.PROBATION
        return AcademicStanding.FAILING

    def _validate_mapping_coverage(self, mappings: list[s.GradeMappingCreate]) -> None:
        ordered = sorted(mappings, key=lambda m: m.min_percentage)
        for previous, current in zip(ordered, ordered[1:]):
            if current.min_percentage <= previous.max_percentage:
                raise HTTPException(status_code=422, detail="Grade mappings cannot overlap")
