from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.modules.reporting.models import ExportFormat, ReportType
from app.modules.reporting.service import ReportingService


def db_session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    return Session()


def test_dashboard_returns_kpis_and_charts():
    service = ReportingService(db_session(), "college-a")
    dashboard = service.dashboard()
    assert {kpi.key for kpi in dashboard.kpis} >= {"active_students", "exams", "published_results", "outstanding_dues"}
    assert dashboard.charts


def test_report_export_csv_has_header():
    service = ReportingService(db_session(), "college-a")
    media_type, filename, content = service.export_report(ReportType.STUDENT, ExportFormat.CSV)
    assert media_type == "text/csv"
    assert filename == "student.csv"
    assert b"status,count" in content
