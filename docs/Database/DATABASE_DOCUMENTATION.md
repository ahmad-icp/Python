# Database Documentation

All operational tables are tenant-scoped by `college_id` where data belongs to a college. Core areas include admissions, students, academic setup, timetable, attendance, examinations, marks entry, result processing, GPA, report cards, gazettes, merit lists, transcripts, finance, notifications, certificates/documents, reporting, audit, and platform settings.

## Tenant isolation rules
- Every college-owned row must include `college_id`.
- Services must filter by the authenticated tenant before reads, updates, and deletes.
- Cross-tenant reporting is reserved for platform super admins.
