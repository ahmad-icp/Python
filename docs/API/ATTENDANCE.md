# Attendance Management API

Attendance is tenant-isolated by `college_id` and protected by attendance RBAC permissions.

## Endpoints

- `GET /api/v1/attendance/sessions` lists attendance sessions with section/date pagination filters.
- `POST /api/v1/attendance/sessions` creates a draft attendance session for an academic section and date.
- `POST /api/v1/attendance/sessions/{attendance_session_id}/records` bulk creates or updates student attendance records.
- `POST /api/v1/attendance/sessions/{attendance_session_id}/finalize` locks a session after records are marked.
- `GET /api/v1/attendance/records` lists records by session or student.
- `GET /api/v1/attendance/summary` returns present, absent, late, excused, and percentage totals.

## Validation

The service rejects cross-tenant records, academic dates outside the owning session, holidays, non-working days, duplicate students in one bulk mark request, inactive students, and edits to finalized sessions.
