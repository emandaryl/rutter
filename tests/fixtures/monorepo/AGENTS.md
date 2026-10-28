# Meridian — working rules (hand-written, keep as-is)

Rules for AI agents working in this repo:

- Never hand-edit `api/app/migrations/` — generate migrations with alembic.
- Always use the shared fetch helper in `web/src/api/client.ts` for HTTP calls;
  React components must never call fetch directly.
- Run `make fmt` before committing.

## Stack notes

- web/ is React (Vite) with plain CSS custom properties in `web/src/theme.css`.
- api/ is FastAPI; the schema lives in `api/app/schemas.py`.
- Tests: pytest for the API (`api/tests/`), vitest for the web app.
