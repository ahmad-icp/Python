# Reporting & Analytics API

Base path: `/api/v1/reporting`.

## RBAC

- `reporting:read`
- `reporting:export`
- `reporting:manage`

## Capabilities

- Academic, attendance, examination, result, merit, financial, student, and teacher reports.
- Interactive dashboard payloads with KPI widgets and chart definitions.
- Scheduled report definitions with recipients, filters, cron expression, and export format.
- Exports in JSON, CSV, Excel-compatible XLS, and printable HTML delivered with a PDF media type.

## Endpoints

- `GET /dashboard`
- `GET /{report_type}`
- `GET /{report_type}/export?format=csv|json|excel|pdf`
- `POST /schedules`
- `GET /schedules`
