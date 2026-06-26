# Marks Entry API

The Marks Entry module provides tenant-isolated draft marks entry, bulk editing, CSV/Excel-style imports, submission, locking, administrator unlock, moderation/rechecking notes, and audit trails.

## Endpoints

- `GET /api/v1/marks-entry/batches` lists marks batches by exam, section, and status.
- `POST /api/v1/marks-entry/batches` creates a draft batch for an exam subject component.
- `POST /api/v1/marks-entry/batches/{batch_id}/entries` bulk creates or updates marks.
- `POST /api/v1/marks-entry/batches/{batch_id}/entries/single` creates or updates one student's marks.
- `POST /api/v1/marks-entry/batches/{batch_id}/import` imports CSV or Excel-exported CSV content with `student_id` and `marks_obtained` columns.
- `POST /api/v1/marks-entry/batches/{batch_id}/submit` submits a draft batch.
- `POST /api/v1/marks-entry/batches/{batch_id}/lock` locks a submitted batch.
- `POST /api/v1/marks-entry/batches/{batch_id}/unlock` unlocks a locked batch with administrator approval and a reason.
- `GET /api/v1/marks-entry/entries` lists marks entries by batch or student.
- `GET /api/v1/marks-entry/batches/{batch_id}/audit` lists marks audit trail rows.

## Validation

The service rejects cross-tenant references, marks entry for unpublished exams, mismatched components, inactive students, students outside the section, duplicate students in one payload, marks above component maximum, moderated marks outside the component range, edits after submission/lock, empty submissions, and unlocks without a meaningful reason.
