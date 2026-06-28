# Notification Center API

Base path: `/api/v1/notifications`.

## RBAC

- `notification:read` lists templates and queued/sent notifications.
- `notification:send` queues notifications, broadcasts events, and creates announcements.
- `notification:manage` manages templates and processes the delivery queue.

## Capabilities

- In-app, email, SMS, WhatsApp, and push-ready channel architecture.
- Reusable templates by event type and channel.
- Scheduled notifications and queue processing.
- Delivery attempts, retry counts, failed delivery tracking, and provider abstraction.
- Attendance, result, fee, and announcement event broadcasting to students, parents, teachers, employees, or users.

## Endpoints

- `POST /templates`, `GET /templates`
- `POST /`, `GET /`
- `POST /queue/process`
- `POST /announcements`
- `POST /events`
