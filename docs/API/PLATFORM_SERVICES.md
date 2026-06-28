# Platform Services API

Base path: `/api/v1/platform`.

- `GET /audit-logs` returns tenant-scoped audit entries.
- `GET /activity-history` returns recent tenant activity.
- `POST /backups` creates a local or encrypted Google Drive backup job.
- `POST /restore` validates or queues a restore plan.
- `GET /tenant-settings` returns branding, enabled modules, and security capabilities.
