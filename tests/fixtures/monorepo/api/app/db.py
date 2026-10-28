from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Sole DB access path: everything goes through SessionLocal / get_session.
# Import Base from here so models and alembic share one metadata.
DATABASE_URL = "postgresql+psycopg://meridian:meridian@localhost:5432/meridian"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base = declarative_base()


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
