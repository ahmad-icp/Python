# Student Information System API

Base path: `/api/v1/students`

All endpoints are tenant-aware through the authenticated user's college context. During local development, `X-College-Id`, `X-User-Id`, and `X-Role` headers provide this context until JWT integration is completed.

## Permissions

| Action | Permission |
| --- | --- |
| List/profile read | `student:read` |
| Create/update/document upload | `student:write` |
| Delete withdrawn records | `student:delete` |
| Promote students | `student:promote` |
| Mark alumni | `student:alumni` |
| Verify documents | `document:verify` |

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/students` | Search and paginate student profiles. |
| `POST` | `/students` | Create a student with guardian and optional document records. |
| `GET` | `/students/{student_id}` | Read a full student profile. |
| `PATCH` | `/students/{student_id}` | Update mutable student profile fields. |
| `DELETE` | `/students/{student_id}` | Delete non-active records only. |
| `POST` | `/students/{student_id}/documents` | Attach a document metadata record. |
| `POST` | `/students/{student_id}/documents/{document_id}/verification` | Verify or reject a document. |
| `POST` | `/students/{student_id}/promotions` | Promote a student to another class/session. |
| `POST` | `/students/{student_id}/alumni` | Mark a student as alumni and record the graduation event. |

Duplicate prevention is enforced per college by admission number and normalized identity derived from student name, date of birth, and primary guardian mobile.
