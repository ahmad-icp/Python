from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from app.modules.reporting.models import ExportFormat, ReportType, ScheduleStatus

class KPIWidget(BaseModel):
    key: str
    label: str
    value: int | float | Decimal | str
    trend: str | None = None

class ChartSeries(BaseModel):
    label: str
    data: list[int | float]

class ChartDefinition(BaseModel):
    key: str
    title: str
    chart_type: str
    labels: list[str]
    series: list[ChartSeries]

class DashboardResponse(BaseModel):
    kpis: list[KPIWidget]
    charts: list[ChartDefinition]

class ReportResponse(BaseModel):
    report_type: ReportType
    title: str
    columns: list[str]
    rows: list[dict[str, int | float | Decimal | str | None]]
    generated_at: datetime

class ScheduledReportCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    report_type: ReportType
    cron_expression: str = Field(min_length=5, max_length=80)
    export_format: ExportFormat = ExportFormat.PDF
    recipients: list[str] = []
    filters: dict[str, str] = {}

class ScheduledReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    college_id: str
    name: str
    report_type: ReportType
    cron_expression: str
    export_format: ExportFormat
    recipients: str
    filters_json: str
    status: ScheduleStatus
    created_by: str
    last_run_at: datetime | None
    created_at: datetime
