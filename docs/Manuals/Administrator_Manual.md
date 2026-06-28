# Administrator Manual

Administrators configure colleges, users, roles, academic sessions, fee policies, reporting dashboards, notifications, backups, and restore plans.

## Daily operations
1. Review `/api/v1/platform/audit-logs` and `/api/v1/platform/activity-history`.
2. Validate admissions, enroll approved applicants, and reconcile student records.
3. Monitor attendance, examinations, finance collections, certificates, and reporting KPIs.
4. Run local or encrypted Google Drive backups from `/api/v1/platform/backups`.
5. Test restore readiness with dry-run restore plans before any live restore.

## Security responsibilities
- Enforce unique accounts and least-privilege roles.
- Rotate JWT, backup, database, and SMTP secrets.
- Enable MFA when the identity provider is connected.
