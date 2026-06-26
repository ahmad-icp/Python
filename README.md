# College ERP Platform (CEP)

College ERP Platform is planned as an enterprise-grade, multi-tenant ERP for colleges and schools. The platform is designed so each institution can configure branding, academics, fees, grading, calendars, and workflows without changing source code.

## Vision

Build one customizable ERP platform for many colleges and schools with independent modules, strong role-based access control, audited operations, automated backups, and plugin-friendly growth.

## Architecture at a Glance

```text
React + TypeScript PWA
        │ HTTPS
        ▼
FastAPI Backend (versioned REST API)
        │
PostgreSQL + Redis
        │
Local Document Storage + Google Drive Backup Archive
```

## Technology Stack

| Layer | Technology |
| --- | --- |
| Frontend | React + TypeScript |
| UI | Material UI |
| Backend | FastAPI |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Database | PostgreSQL |
| Cache | Redis |
| Background Jobs | Celery |
| File Storage | Local Storage |
| Backup | Google Drive API |
| Authentication | JWT |
| Reports | ReportLab |
| Charts | Chart.js |
| Web Server | Nginx |
| Containerization | Docker |

## Repository Layout

```text
frontend/      React + TypeScript PWA shell
backend/       FastAPI application, modules, services, workers
docs/          SRS, ERD, API, and architecture documentation
database/      Schema notes, migrations, and seed data
storage/       Local runtime document folders for development
scripts/       Operational and developer scripts
docker/        Docker and Nginx assets
tests/         Automated tests
deployment/    Deployment manifests and runbooks
.github/       CI workflows and repository automation
```

## Initial Development Roadmap

1. Requirements Specification (SRS)
2. System Architecture
3. UI/UX Design
4. Database ER Diagram
5. Authentication and Roles
6. Admissions Module
7. Student Information System
8. Attendance
9. Examination and Results
10. Fee Management
11. Reports
12. Parent and Student Portals
13. Notifications
14. Backup and Restore
15. Testing, Security, and Deployment

See `docs/Architecture/ARCHITECTURE.md` for the detailed target architecture and module boundaries.
