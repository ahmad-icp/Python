# Core Database Tables

Initial normalized database planning includes these core tables:

- users
- roles
- permissions
- role_permissions
- colleges
- college_settings
- students
- parents
- teachers
- programs
- sessions
- classes
- sections
- subjects
- attendance
- exam_types
- exams
- marks
- grades
- fee_heads
- fee_invoices
- fee_payments
- timetables
- notifications
- documents
- audit_logs
- backups

Enterprise implementation is expected to grow toward 70-100 normalized tables as modules mature.


## Timetable Management

Core tables include `classrooms`, `time_slots`, `working_days`, `calendar_events`, `timetable_versions`, and `timetable_entries`. Entries reference Academic Management sections and subjects and enforce indexed clash checks for teachers, rooms, and sections by weekday/time slot.

## Examination Management Tables

- `exam_types`: tenant-scoped exam type catalog.
- `exams`: academic-session/class/section scoped exam headers and workflow status.
- `assessment_components`: subject-level marks components with maximum marks, passing marks, and weightage constraints.
- `exam_halls`: tenant-scoped exam rooms with capacity constraints.
- `exam_schedules`: exam timetable rows with hall and section conflict indexes.
- `invigilator_assignments`: teacher invigilation assignments with conflict-oriented indexes.

## Marks Entry Tables

- `marks_entry_batches`: tenant-scoped marks entry worklists by exam, section, subject, and assessment component.
- `marks_entries`: student marks with moderation/rechecking fields and uniqueness across exam, subject, component, and student.
- `marks_audit_trails`: immutable audit events for entry updates, imports, submission, locking, and unlock approvals.
