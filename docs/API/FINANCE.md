# Enterprise Finance API

Base path: `/api/v1/fees`. RBAC permissions: `fee:read`, `fee:write`, `fee:collect`, `fee:refund`, and `fee:manage`.

## Capabilities
- Configure tenant-isolated fee heads and versioned fee templates by program, class, section, frequency, and effective dates.
- Generate manual or bulk challans with due dates, carry-forward balances, discounts, late fines, partial payment tracking, and duplicate payment detection.
- Manage scholarships/discounts and installment approvals.
- Record cash, cheque, bank transfer, JazzCash, Easypaisa, and Raast-ready payments.
- Request refunds and view collection/outstanding/aging-style summary metrics.

## Endpoints
- `GET /heads`, `POST /heads`
- `POST /templates`
- `POST /challans/manual`, `POST /challans/generate`, `GET /challans`
- `POST /payments`
- `POST /scholarships`, `POST /scholarships/{scholarship_id}/approval`
- `POST /installments`
- `POST /refunds`
- `GET /reports/summary`
