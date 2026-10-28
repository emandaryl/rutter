from datetime import date

from sqlalchemy import ForeignKey, String, Numeric, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

# Domain nouns: Client -> Invoice. A client is a company with one contact; an
# invoice drafts against exactly one client.
class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    contact_email: Mapped[str] = mapped_column(String(200))


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    total: Mapped[float] = mapped_column(Numeric(10, 2))
    due_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(10), default="draft")
