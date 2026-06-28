# Transcript Generation API

- `POST /api/v1/transcripts/generate` creates a complete academic transcript for a student.
- `GET /api/v1/transcripts/` lists transcript history.
- `POST /api/v1/transcripts/{id}/issue` marks a transcript official.
- `GET /api/v1/transcripts/verify/{code}` verifies issued transcripts.

Transcripts include percentage records, GPA/CGPA when available, credit-hour summaries, subject history JSON, printable HTML, and verification codes.
