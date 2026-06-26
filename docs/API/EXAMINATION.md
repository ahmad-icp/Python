# Examination Management API

The Examination Management module is tenant-isolated and supports exam type configuration, scoped exam creation, assessment components, hall allocation, scheduling, invigilator assignment, publishing, and locking.

## Endpoints

- `GET /api/v1/examinations/types` and `POST /api/v1/examinations/types` manage exam types.
- `GET /api/v1/examinations/exams` and `POST /api/v1/examinations/exams` manage class/section exams.
- `POST /api/v1/examinations/exams/{exam_id}/publish` publishes scheduled exams after component and schedule validation.
- `POST /api/v1/examinations/exams/{exam_id}/lock` locks published exams for downstream marks entry.
- `GET /api/v1/examinations/components` and `POST /api/v1/examinations/components` manage theory, practical, viva, internal, and external components.
- `GET /api/v1/examinations/halls` and `POST /api/v1/examinations/halls` manage exam rooms.
- `GET /api/v1/examinations/schedules` and `POST /api/v1/examinations/schedules` manage exam timetable rows.
- `GET /api/v1/examinations/invigilators` and `POST /api/v1/examinations/invigilators` manage invigilator assignments.

## Validation

The service rejects cross-tenant references, inactive exam types/halls, class/session/section mismatches, exam dates outside academic sessions, schedules outside exam windows, academic holidays, non-working days, unallocated subjects, missing assessment components, hall capacity shortfalls, overlapping hall bookings, overlapping section exams, and invigilator timetable conflicts.
