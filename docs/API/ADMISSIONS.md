# Admissions Management API

Base path: `/api/v1/admissions`

Admissions is the first module in the academic dependency chain. It captures online and offline applications, verifies submitted documents, evaluates eligibility, creates merit lists, publishes offers, and converts accepted applicants into student records.

## Permissions

| Action | Permission |
| --- | --- |
| Read applications | `admission:read` |
| Create/update applications and documents | `admission:write` |
| Review eligibility or rejection | `admission:decide` |
| Enroll accepted applicants | `admission:enroll` |
| Generate/publish merit lists | `merit_list:manage` |
| Verify admission documents | `document:verify` |

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/applications` | Search, filter, and paginate applications. |
| `POST` | `/applications` | Create an online or offline admission application. |
| `GET` | `/applications/{application_id}` | Read a full application profile. |
| `PATCH` | `/applications/{application_id}` | Update editable application details. |
| `POST` | `/applications/{application_id}/documents` | Attach required document metadata. |
| `POST` | `/applications/{application_id}/documents/{document_id}/verification` | Verify or reject an admission document. |
| `POST` | `/applications/{application_id}/decision` | Mark under-review, documents-pending, eligible, offered, rejected, or cancelled. |
| `POST` | `/merit-lists` | Generate a merit list from eligible applications. |
| `POST` | `/merit-lists/{merit_list_id}/publish` | Publish offers from a merit list. |
| `POST` | `/applications/{application_id}/enroll` | Convert an eligible/offered applicant into a student profile. |

## Business Rules

- Application numbers are unique per college.
- Duplicate applicants are blocked per college using normalized identity derived from applicant name, date of birth, and guardian mobile.
- Merit scores are calculated as `(obtained_marks / total_marks) * 100` when marks are provided.
- Merit lists select eligible applications by program, academic session, minimum score, and capacity.
- Submitted documents must be verified before enrollment when documents exist on the application.
- Enrollment creates a Student Information System record and marks the application as admitted.
