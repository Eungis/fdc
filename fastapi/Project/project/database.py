from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Make database connection
SQLALCHEMY_DATABASE_URL = "sqlite:///./product.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        # the second parameter only has to be passed whenever using SQLite database
        "check_same_thread": False
    },
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    """The get_db generator function is used as a dependency in the read_items route of a FastAPI application.
    The db argument is automatically injected into the route function,
    and the generator ensures that the database session is properly managed and closed after the route execution."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
