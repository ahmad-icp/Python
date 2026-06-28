import csv
import io
import json
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.attendance.models import AttendanceRecord, AttendanceStatus
from app.modules.examination.models import Exam
from app.modules.fees.models import FeeChallan, FeePayment, PaymentStatus
from app.modules.reporting.models import ExportFormat, ReportType, ScheduledReport
from app.modules.reporting.schemas import ChartDefinition, ChartSeries, DashboardResponse, KPIWidget, ReportResponse, ScheduledReportCreate
from app.modules.results.merit_models import MeritList
from app.modules.results.models import ResultStatus, StudentResult
from app.modules.students.models import Student, StudentStatus
from app.modules.timetable.models import TimetableEntry


class ReportingService:
    def __init__(self, db: Session, college_id: str) -> None:
        self.db = db
        self.college_id = college_id

    def dashboard(self) -> DashboardResponse:
        active_students = self._count(Student, Student.status == StudentStatus.ACTIVE)
        exams = self._count(Exam)
        published_results = self._count(StudentResult, StudentResult.status == ResultStatus.PUBLISHED)
        outstanding = self.db.scalar(select(func.coalesce(func.sum(FeeChallan.balance_amount), 0)).where(FeeChallan.college_id == self.college_id)) or Decimal("0")
        attendance_rows = self.db.execute(select(AttendanceRecord.status, func.count()).where(AttendanceRecord.college_id == self.college_id).group_by(AttendanceRecord.status)).all()
        attendance_labels = [row[0].value for row in attendance_rows]
        attendance_counts = [row[1] for row in attendance_rows]
        return DashboardResponse(
            kpis=[
                KPIWidget(key="active_students", label="Active Students", value=active_students),
                KPIWidget(key="exams", label="Exams", value=exams),
                KPIWidget(key="published_results", label="Published Results", value=published_results),
                KPIWidget(key="outstanding_dues", label="Outstanding Dues", value=outstanding),
            ],
            charts=[
                ChartDefinition(key="attendance_status", title="Attendance by Status", chart_type="bar", labels=attendance_labels, series=[ChartSeries(label="Records", data=attendance_counts)]),
                ChartDefinition(key="academic_pipeline", title="Academic Pipeline", chart_type="line", labels=["Students", "Exams", "Results"], series=[ChartSeries(label="Count", data=[active_students, exams, published_results])]),
            ],
        )

    def generate_report(self, report_type: ReportType) -> ReportResponse:
        handlers = {
            ReportType.ACADEMIC: self._academic_report,
            ReportType.ATTENDANCE: self._attendance_report,
            ReportType.EXAMINATION: self._examination_report,
            ReportType.RESULT: self._result_report,
            ReportType.MERIT: self._merit_report,
            ReportType.FINANCIAL: self._financial_report,
            ReportType.STUDENT: self._student_report,
            ReportType.TEACHER: self._teacher_report,
        }
        return handlers[report_type]()

    def export_report(self, report_type: ReportType, export_format: ExportFormat) -> tuple[str, str, bytes]:
        report = self.generate_report(report_type)
        if export_format == ExportFormat.JSON:
            return "application/json", f"{report_type.value}.json", report.model_dump_json().encode()
        if export_format == ExportFormat.CSV:
            return "text/csv", f"{report_type.value}.csv", self._csv_bytes(report)
        if export_format == ExportFormat.EXCEL:
            return "application/vnd.ms-excel", f"{report_type.value}.xls", self._csv_bytes(report)
        html = self._html_report(report)
        return "application/pdf", f"{report_type.value}.pdf", html.encode()

    def create_schedule(self, payload: ScheduledReportCreate, created_by: str) -> ScheduledReport:
        schedule = ScheduledReport(
            college_id=self.college_id,
            name=payload.name,
            report_type=payload.report_type,
            cron_expression=payload.cron_expression,
            export_format=payload.export_format,
            recipients=json.dumps(payload.recipients),
            filters_json=json.dumps(payload.filters),
            created_by=created_by,
        )
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def list_schedules(self) -> list[ScheduledReport]:
        return list(self.db.scalars(select(ScheduledReport).where(ScheduledReport.college_id == self.college_id).order_by(ScheduledReport.created_at.desc())).all())

    def _academic_report(self) -> ReportResponse:
        rows = [
            {"metric": "active_students", "value": self._count(Student, Student.status == StudentStatus.ACTIVE)},
            {"metric": "timetable_entries", "value": self._count(TimetableEntry)},
        ]
        return self._report(ReportType.ACADEMIC, "Academic Report", ["metric", "value"], rows)

    def _attendance_report(self) -> ReportResponse:
        rows = [{"status": row[0].value, "count": row[1]} for row in self.db.execute(select(AttendanceRecord.status, func.count()).where(AttendanceRecord.college_id == self.college_id).group_by(AttendanceRecord.status)).all()]
        return self._report(ReportType.ATTENDANCE, "Attendance Report", ["status", "count"], rows)

    def _examination_report(self) -> ReportResponse:
        rows = [{"metric": "exams", "value": self._count(Exam)}]
        return self._report(ReportType.EXAMINATION, "Examination Report", ["metric", "value"], rows)

    def _result_report(self) -> ReportResponse:
        rows = [{"status": row[0].value, "count": row[1]} for row in self.db.execute(select(StudentResult.status, func.count()).where(StudentResult.college_id == self.college_id).group_by(StudentResult.status)).all()]
        return self._report(ReportType.RESULT, "Result Report", ["status", "count"], rows)

    def _merit_report(self) -> ReportResponse:
        rows = [{"metric": "merit_lists", "value": self._count(MeritList)}]
        return self._report(ReportType.MERIT, "Merit Report", ["metric", "value"], rows)

    def _financial_report(self) -> ReportResponse:
        collected = self.db.scalar(select(func.coalesce(func.sum(FeePayment.amount), 0)).where(FeePayment.college_id == self.college_id, FeePayment.status == PaymentStatus.RECONCILED)) or Decimal("0")
        outstanding = self.db.scalar(select(func.coalesce(func.sum(FeeChallan.balance_amount), 0)).where(FeeChallan.college_id == self.college_id)) or Decimal("0")
        rows = [{"metric": "collections", "value": collected}, {"metric": "outstanding", "value": outstanding}]
        return self._report(ReportType.FINANCIAL, "Financial Report", ["metric", "value"], rows)

    def _student_report(self) -> ReportResponse:
        rows = [{"status": row[0].value, "count": row[1]} for row in self.db.execute(select(Student.status, func.count()).where(Student.college_id == self.college_id).group_by(Student.status)).all()]
        return self._report(ReportType.STUDENT, "Student Report", ["status", "count"], rows)

    def _teacher_report(self) -> ReportResponse:
        rows = [{"teacher_id": row[0], "entries": row[1]} for row in self.db.execute(select(TimetableEntry.teacher_id, func.count()).where(TimetableEntry.college_id == self.college_id).group_by(TimetableEntry.teacher_id)).all()]
        return self._report(ReportType.TEACHER, "Teacher Report", ["teacher_id", "entries"], rows)

    def _count(self, model, *criteria) -> int:
        query = select(func.count()).select_from(model).where(model.college_id == self.college_id)
        for criterion in criteria:
            query = query.where(criterion)
        return self.db.scalar(query) or 0

    def _report(self, report_type: ReportType, title: str, columns: list[str], rows: list[dict]) -> ReportResponse:
        return ReportResponse(report_type=report_type, title=title, columns=columns, rows=rows, generated_at=datetime.now(UTC))

    def _csv_bytes(self, report: ReportResponse) -> bytes:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=report.columns)
        writer.writeheader()
        writer.writerows(report.rows)
        return output.getvalue().encode()

    def _html_report(self, report: ReportResponse) -> str:
        rows = "".join("<tr>" + "".join(f"<td>{row.get(column, '')}</td>" for column in report.columns) + "</tr>" for row in report.rows)
        header = "".join(f"<th>{column}</th>" for column in report.columns)
        return f"<html><body><h1>{report.title}</h1><table><thead><tr>{header}</tr></thead><tbody>{rows}</tbody></table></body></html>"
