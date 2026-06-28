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

## Result Processing Tables

- `grading_policies`: tenant-scoped grading, passing, grace, and promotion policy versions.
- `student_results`: one calculated overall result per tenant, exam, and student.
- `subject_results`: normalized subject-level outcomes linked to student results.
- `result_audit_trails`: append-only audit log for calculation and state transitions.

## GPA & Percentage Calculation Tables

- `grade_systems`: tenant-scoped GPA or percentage grading policies for institution, program, class, or section scopes.
- `grade_mappings`: grade-to-percentage and optional grade-point mappings for each grading system.
- `student_grade_calculations`: calculated percentage, grade, GPA/CGPA where applicable, credit-hour totals, standing, and promotion eligibility per result.

## Report Cards DMC Tables

- `report_cards`: one DMC per result with verification code, printable HTML, optional GPA calculation link, branding metadata, and issue lifecycle fields.

## Gazette Tables

- `gazettes`: tenant-scoped generated gazette snapshots with summary JSON and ranked row JSON.

## Merit List Tables

- `merit_lists`: scoped merit list header with ranking basis, publication status, tie-breakers, and analytics.
- `merit_list_items`: ranked student entries linked to results and optional grade calculations.
- `merit_certificates`: printable merit certificates with tenant-scoped verification codes.

## Transcript Tables

- `transcripts`: generated academic-history snapshots with summary JSON, printable HTML, issue lifecycle, and verification codes.
