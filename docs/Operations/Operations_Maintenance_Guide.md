# Operations & Maintenance Guide

## Daily
- Check `/api/v1/health`.
- Review audit logs and failed login trends.
- Confirm backup job completion.

## Weekly
- Perform restore dry-run validation.
- Review slow endpoints and database growth.
- Rotate stale user accounts and verify tenant isolation alerts.

## Incident response
1. Preserve audit logs.
2. Disable affected accounts or tenant access.
3. Restore from the latest verified backup if data integrity is compromised.
4. Record post-incident corrective actions.
