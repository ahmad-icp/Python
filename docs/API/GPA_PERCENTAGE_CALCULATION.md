# GPA & Percentage Calculation API

This module maps calculated Result Processing records to institution/program/class/section grading systems.

## Security

Endpoints are tenant-scoped by `X-College-Id` and require:

- `grade:read`
- `grade:configure`
- `grade:calculate`

## Endpoints

- `POST /api/v1/grade-calculations/systems` creates a GPA or percentage grading system with grade mappings.
- `GET /api/v1/grade-calculations/systems` lists configured grading systems with pagination.
- `POST /api/v1/grade-calculations/calculations` calculates percentage, grade, GPA/CGPA where applicable, standing, and promotion eligibility for result IDs.
- `GET /api/v1/grade-calculations/calculations` searches calculated grades by student or exam.

## Business Rules

- Percentage is retained for every institution type.
- GPA, CGPA, grade points, and credit hours are populated only for `gpa` systems.
- Percentage systems explicitly return `null` GPA/CGPA and credit-hour fields.
- GPA is credit-hour weighted from subject result percentages and grade mappings.
- CGPA is cumulative across prior GPA calculations for the same student.
- Grade mappings cannot overlap and must contain percentage ranges from 0 to 100 as required by institutional policy.
- Rounding supports `standard`, `floor`, and `ceil` modes with configurable decimal places.
