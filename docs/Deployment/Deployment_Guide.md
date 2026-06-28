# Deployment Guide

## Prerequisites
- Docker and Docker Compose
- DNS and TLS termination
- PostgreSQL backup storage
- Redis persistence

## Steps
1. Copy `.env.production.example` to `.env.production` and set strong secrets.
2. Build and start: `docker compose -f docker-compose.prod.yml up -d --build`.
3. Verify health: `curl http://localhost/api/v1/health`.
4. Configure scheduled database and upload backups.
5. Connect error tracking using `SENTRY_DSN` when available.
