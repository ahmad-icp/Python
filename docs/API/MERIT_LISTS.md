# Merit Lists API

- `POST /api/v1/merit-lists/generate` generates institution, program, class, section, or session merit lists.
- `GET /api/v1/merit-lists/` lists merit lists.
- `POST /api/v1/merit-lists/{id}/publish` publishes a draft list.
- `POST /api/v1/merit-lists/{id}/lock` locks a published list.
- `POST /api/v1/merit-lists/items/{item_id}/certificate` issues a merit certificate.

Merit can be ranked by percentage for school/FSc systems or GPA for university systems. Tie breakers include date of birth, admission number, and name.
