# Academic Management API

Academic Management is exposed under `/api/v1/academic` and is the required foundation for timetable, attendance, examinations, and results.

## Security

Routes enforce RBAC permissions:

- `academic:read` for lists and workload views.
- `academic:write` for institution, campus, department, session, program, class, section, subject, and promotion-rule configuration.
- `academic:assign` for subject allocation and teacher assignment.
- `academic:delete` for academic archive capture.

## Implemented resources

- Institutions and campuses
- Departments
- Academic sessions
- Programs
- Classes and sections
- Subjects, subject groups, elective groups, prerequisites, and subject allocations
- Teacher assignments and workload calculation
- Promotion rules
- Academic archives

## Key rules

- Tenant boundaries are enforced with `college_id` in the service layer and composite database constraints.
- Class names cannot repeat within the same program and academic session.
- Section capacity must be positive and enrolled count cannot exceed capacity.
- Subject prerequisites must be allocated before dependent subjects.
- Teacher assignment validates maximum weekly workload before accepting a new assignment.
