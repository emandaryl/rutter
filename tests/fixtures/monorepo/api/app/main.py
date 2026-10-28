# Meridian API.

from fastapi import FastAPI

from app.schemas import InvoiceIn
from app.db import get_session  # noqa: F401  (router wiring below)
from app.routes import invoices

# The app object mounts three routers: invoices (CRUD), clients, and health.
app = FastAPI(title="Meridian API", version="0.2.0")

app.include_router(invoices.router, prefix="/invoices", tags=["invoices"])


@app.get("/health")
def health() -> dict:
    return {"ok": True}
