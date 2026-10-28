from datetime import date

from fastapi import APIRouter, HTTPException

from app.db import get_session
from app.models import Invoice
from app.schemas import InvoiceIn, InvoiceOut

# Invoice CRUD. The web app calls these under /invoices; a service boundary
# would live here if business rules grow past validation.
router = APIRouter()


@router.get("", response_model=list[InvoiceOut])
def list_invoices():
    with get_session() as session:
        rows = session.query(Invoice).order_by(Invoice.due_date).all()
        return [InvoiceOut.model_validate(r) for r in rows]


@router.post("", response_model=InvoiceOut)
def create_invoice(payload: InvoiceIn):
    with get_session() as session:
        row = Invoice(**payload.model_dump())
        session.add(row)
        session.commit()
        session.refresh(row)
        return InvoiceOut.model_validate(row)


@router.patch("/{invoice_id}/pay", response_model=InvoiceOut)
def mark_paid(invoice_id: int):
    with get_session() as session:
        row = session.get(Invoice, invoice_id)
        if row is None:
            raise HTTPException(status_code=404, detail="no such invoice")
        row.status = "paid"
        session.commit()
        return InvoiceOut.model_validate(row)
