# Alembic environment. Read-only for everyone: migrations are generated with
# `alembic revision --autogenerate` and applied by `alembic upgrade head`.
from alembic import context

from app.db import Base
from app import models  # noqa: F401 — import registers tables on Base.metadata

target_metadata = Base.metadata
