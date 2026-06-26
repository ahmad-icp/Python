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
