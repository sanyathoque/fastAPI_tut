from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


settings = get_settings()

# SQLite needs this flag when FastAPI handles requests across multiple threads.
# Other databases, like PostgreSQL, do not need this SQLite-only option.
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# The engine owns the database connection pool and knows how to talk to the DB.
# Nothing is queried here yet. This just prepares the database connection setup.
engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    future=True,
)

# A session is a short-lived unit of work. Routes get one session per request.
# The session is what CRUD functions use to select, add, update, and delete rows.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)


class Base(DeclarativeBase):
    # All SQLAlchemy models inherit from this so metadata can create tables.
    # Example: User(Base) and Post(Base) register themselves as database tables.
    pass


def get_db() -> Generator[Session, None, None]:
    # FastAPI dependency: open a DB session, give it to the route, then close it.
    # yield pauses here while the route runs. After the route finishes, finally
    # runs and closes the session.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
