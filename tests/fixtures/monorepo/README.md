# Meridian

Small invoicing app for freelancers: create clients, issue invoices with a few
line items, mark them paid. Not multi-tenant; no user accounts beyond a shared
team passphrase at the API edge.

- `web/` — React (Vite) front end, talks to the API over `/invoices` routes.
- `api/` — FastAPI + SQLAlchemy + Postgres, alembic-managed migrations.
- `make install`, `make dev`, `make fmt`, `make test` from the root Makefile.

The web app has two routes: the invoice list and the create/edit form. There is
no auth library anywhere — the shared passphrase header is set by
`web/src/api/client.ts`. No CI or deploy config exists yet; it runs locally.
