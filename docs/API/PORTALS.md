# User Portals API

Base paths:

- `/api/v1/portal/student` for student self-service dashboards.
- `/api/v1/portal/parent` for parent child dashboards and teacher communication placeholders.
- `/api/v1/portal/teacher` for teacher workbench dashboards.

## RBAC

- `student_portal:read`
- `parent_portal:read`
- `teacher_portal:read`

## Endpoints

- `GET /portal/student/students/{student_id}/dashboard` returns profile, attendance, timetable, published results, report/transcript download links, merit positions, fee status, challans, payments, notifications, and academic calendar events.
- `GET /portal/parent/dashboard?child_id={student_id}` returns one or more child dashboards plus teacher communication placeholders.
- `GET /portal/teacher/dashboard` returns teacher timetable, attendance sessions, marks/result review placeholders, announcements, and class-management placeholders.
