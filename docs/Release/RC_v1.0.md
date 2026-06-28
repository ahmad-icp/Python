# Release Candidate v1.0

College ERP Platform v1.0 is the production release candidate for multi-tenant college operations serving admissions, student information, attendance, examinations, marks, results, GPA, report cards, gazettes, merit lists, transcripts, finance, notifications, portals, certificates, and reporting.

## Production readiness scope
- Tenant-aware APIs using `X-College-Id` for isolation in development and JWT tenant claims in production.
- RBAC roles for super admin, college admin, principal, admission officer, accountant, teacher, student, and parent.
- Platform services for audit logs, activity history, backups, restore planning, tenant settings, and branding.
- Deployment assets for optimized backend/frontend containers, production compose, nginx reverse proxy, health checks, Redis, and PostgreSQL.
- CI workflow for backend tests and frontend production build.

## Release gates
- Backend tests must pass in an environment with Python dependencies installed.
- Frontend build must pass with Node dependencies installed.
- Production secrets must replace all `change-me-*` defaults before deployment.
