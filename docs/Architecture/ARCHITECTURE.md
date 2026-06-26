# College ERP Platform Architecture

## 1. Platform Goals

The College ERP Platform (CEP) is a configurable, multi-tenant ERP for colleges and schools. The product goal is to support different institutions from the same codebase by storing institution-specific choices in configuration and tenant data instead of hardcoding behavior.

## 2. High-Level Architecture

```text
                            ┌──────────────────────────────┐
                            │      Web Application         │
                            │ React + TypeScript (PWA)     │
                            └──────────────┬───────────────┘
                                           │ HTTPS
                    ┌──────────────────────┴──────────────────────┐
                    │            FastAPI Backend                  │
                    │ Authentication, Student, Academic, Exam,    │
                    │ Attendance, Fee, Notification, Reports,     │
                    │ File, Backup, and Audit Services            │
                    └──────────────────────┬──────────────────────┘
                                           │
                          PostgreSQL Database + Redis Cache
                                           │
                 ┌─────────────────────────┼────────────────────────┐
                 │                         │                        │
          Local Storage              Google Drive            Backup Archive
          Documents/PDFs             Automatic Backup        External HDD
```

## 3. Modular Architecture

Each module owns its domain models, schemas, routes, services, permissions, and audit events. Modules should communicate through public service interfaces or domain events, not direct cross-module data mutation.

Target modules:

- Authentication
- Dashboard
- Admissions
- Student Information System
- Parent Portal
- Teacher Portal
- Academic Management
- Attendance
- Examination
- Result Management
- Fee Management
- Library
- Transport
- Hostel
- Inventory
- Human Resource
- Payroll
- Timetable
- Notifications
- Reports
- Settings
- Audit Logs
- Backup Manager
- AI Analytics

## 4. User Hierarchy and Access Control

Roles are implemented through RBAC backed by a permission engine.

```text
Platform Super Admin
        │
College Owner, Principal, Vice Principal, Administrator
        │
Admission Officer, Accountant, Teacher, Lab Assistant, Librarian, Transport Manager
        │
Parent, Student, Guest
```

Access decisions should evaluate tenant membership, role assignments, permissions, resource ownership, and feature flags.

## 5. Multi-Tenant Design

Every tenant college has independent configuration for logo, name, address, theme, subjects, grading policies, fee structures, sessions, academic calendars, templates, and enabled modules.

Tenant boundaries must be enforced at the API, service, and database query layers. Shared tables include a `college_id` tenant key unless they are global platform tables such as platform users, global permissions, or subscription metadata.

## 6. Authentication Flow

```text
Email or mobile login
        ↓
JWT access token
        ↓
Refresh token rotation
        ↓
RBAC permission check
        ↓
Audit log event
```

Planned features include password reset, session management, login history, and future two-factor authentication.

## 7. Student Lifecycle

```text
Admission → Enrollment → Section Allocation → Attendance → Assignments
→ Sessional Exams → Final Exams → Result → Promotion → Graduation → Alumni
```

Admissions and student information services must prevent duplicate student records by checking normalized identity, guardian, program, and tenant-specific admission details.

## 8. Notification Engine

Domain events trigger notification workflows. A single event can fan out to multiple channels such as email, SMS, WhatsApp, parent portal, and student portal.

Handled events include fee reminders, attendance alerts, holiday announcements, timetable updates, and result publication.

## 9. Reporting Engine

The reporting engine generates PDF, Excel, and CSV outputs for transcripts, result cards, DMCs, fee challans, certificates, attendance reports, gazettes, position lists, and teacher workload reports.

## 10. Storage and Backup

Documents are stored locally by category during initial development. Backup jobs create encrypted archives, upload them to Google Drive, verify integrity, and send email reports.

## 11. Future AI Module

AI Analytics is isolated as a future module for failing-student prediction, attendance shortage prediction, fee default risk, report comments, dashboards, chatbot support, OCR admission forms, and face-recognition attendance.


## 12. Timetable Management

Timetable Management depends on Academic Management for sessions, programs, classes, sections, subject allocations, and teacher assignments. It manages classrooms/labs, time slots, working days, academic calendar events, versioned section timetables, and entries. Validation prevents teacher, classroom, and section clashes; blocks holiday scheduling; enforces teacher assignment and workload; and preserves published timetable history through versioning.
