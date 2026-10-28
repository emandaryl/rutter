from datetime import date

from pydantic import BaseModel, Field

# Request/response schemas. Kept separate from the SQLAlchemy models so wire
# shapes can drift deliberately from table shapes.
class InvoiceIn(BaseModel):
    client_id: int
    total: float = Field(gt=0)
    due_date: date


class InvoiceOut(BaseModel):
    id: int
    client_id: int
    total: float
    due_date: date
    status: str
