# Report Cards (DMC) API

Generates printable Detailed Marks Certificates from published or locked results.

## Endpoints

- `POST /api/v1/report-cards/generate` creates or refreshes a report card for a result.
- `GET /api/v1/report-cards/` lists generated cards by student or exam.
- `POST /api/v1/report-cards/{card_id}/issue` marks a card as officially issued.
- `GET /api/v1/report-cards/verify/{code}` validates an issued report card verification code.

## Features

The printable document includes institution branding, subject-wise marks, overall percentage, GPA/CGPA when a GPA calculation exists, remarks, and a QR-verification payload. The generated HTML is print/PDF-ready through the browser print flow.
