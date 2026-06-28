from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.security import CurrentUser, Permission, require_permission
from app.db.session import get_db
from app.modules.reporting.models import ExportFormat, ReportType
from app.modules.reporting.schemas import DashboardResponse, ReportResponse, ScheduledReportCreate, ScheduledReportRead
from app.modules.reporting.service import ReportingService

router = APIRouter()


def service(db: Session, current_user: CurrentUser) -> ReportingService:
    return ReportingService(db=db, college_id=current_user.college_id)


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.REPORTING_READ)),
):
    return service(db, current_user).dashboard()


@router.post("/schedules", response_model=ScheduledReportRead)
def create_schedule(
    payload: ScheduledReportCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.REPORTING_MANAGE)),
):
    return service(db, current_user).create_schedule(payload, current_user.user_id)


@router.get("/schedules", response_model=list[ScheduledReportRead])
def list_schedules(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.REPORTING_READ)),
):
    return service(db, current_user).list_schedules()


@router.get("/{report_type}", response_model=ReportResponse)
def generate_report(
    report_type: ReportType,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.REPORTING_READ)),
):
    return service(db, current_user).generate_report(report_type)


@router.get("/{report_type}/export")
def export_report(
    report_type: ReportType,
    export_format: ExportFormat = Query(default=ExportFormat.CSV, alias="format"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.REPORTING_EXPORT)),
):
    media_type, filename, content = service(db, current_user).export_report(report_type, export_format)
    return Response(content=content, media_type=media_type, headers={"Content-Disposition": f"attachment; filename={filename}"})
