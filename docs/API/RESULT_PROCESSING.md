# Result Processing API

The Result Processing module calculates student and subject results from locked Marks Entry batches.

## Security

All endpoints are tenant-scoped by `X-College-Id` and require result permissions:

- `result:read`
- `result:configure`
- `result:calculate`
- `result:publish`
- `result:lock`

## Endpoints

- `POST /api/v1/results/policies` creates a configurable grading policy.
- `GET /api/v1/results/policies` lists grading policies.
- `POST /api/v1/results/calculate` aggregates marks, applies moderation/grace rules, and creates draft results.
- `GET /api/v1/results/results` searches results by exam, student, and status with pagination.
- `POST /api/v1/results/results/{result_id}/publish` publishes a draft result.
- `POST /api/v1/results/results/{result_id}/lock` locks a published result.

## Calculation Rules

- All marks batches for the exam must be locked before calculation.
- Subject totals are aggregated across all configured assessment components.
- Moderation marks already approved in Marks Entry are included.
- Grace marks are capped by grading policy and only bridge pass-threshold shortfalls.
- Any missing component marks produce an `incomplete` subject and overall result.
