# Operations Architecture

The production topology uses nginx as the edge reverse proxy, a React static frontend, FastAPI backend workers, PostgreSQL for durable data, Redis for cache/rate limiting/background queues, object storage for uploads, and encrypted backup storage.

## Cross-cutting controls
- JWT access and refresh tokens.
- RBAC permissions mapped by role.
- Audit logs and activity history.
- Rate limiting and secure response headers at nginx/application layers.
- Health checks for load balancers and compose orchestration.
