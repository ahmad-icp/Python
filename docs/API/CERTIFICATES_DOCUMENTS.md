# Certificate & Document Management API

Base path: `/api/v1/certificates`.

## RBAC

- `certificate:read`, `certificate:write`, `certificate:approve`, `certificate:issue`, `certificate:manage`
- `document:read`, `document:write`, `document:approve`

## Capabilities

- Character, bonafide, leaving, migration, experience, and custom certificates.
- Versioned certificate templates with token rendering.
- Request, approval, rejection, issue, and QR verification workflow.
- Student/employee document repository with SHA-256 checksums and approval workflow.

## Endpoints

- `POST /templates`, `GET /templates`
- `POST /requests`, `GET /requests`
- `POST /requests/{request_id}/approval`
- `POST /requests/{request_id}/issue`
- `GET /verify/{verification_code}`
- `POST /documents`, `GET /documents`
- `POST /documents/{document_id}/approval`
